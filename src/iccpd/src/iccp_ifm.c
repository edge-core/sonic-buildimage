/*
 * iccp_ifm.c
 *
 * Copyright(c) 2016-2019 Nephos/Estinet.
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, see <http://www.gnu.org/licenses/>.
 *
 * The full GNU General Public License is included in this distribution in
 * the file called "COPYING".
 *
 *  Maintainer: jianjun, grace Li from nephos
 */

#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_bridge.h>
#include <netlink/msg.h>

#include "../include/system.h"
#include "../include/iccp_cli.h"
#include "../include/logger.h"
#include "../include/mlacp_sync_update.h"
#include "../include/mlacp_link_handler.h"
#include "../include/port.h"
#include "../include/iccp_netlink.h"

#define fwd_neigh_state_valid(state) (state & (NUD_REACHABLE | NUD_STALE | NUD_DELAY | NUD_PROBE | NUD_PERMANENT))

#ifndef NDA_RTA
#define NDA_RTA(r) \
    ((struct rtattr*)(((char*)(r)) + NLMSG_ALIGN(sizeof(struct ndmsg))))
#endif

static int iccp_valid_handler(struct nl_msg *msg, void *arg)
{
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    unsigned int event = 0;

    if (nlh->nlmsg_type != RTM_NEWLINK)
        return 0;

    if (nl_msg_parse(msg, &iccp_event_handler_obj_input_newlink, &event) < 0)
        ICCPD_LOG_ERR(__FUNCTION__, "Unknown message type.");

    return 0;
}

/*Get kernel interfaces and ports during initialization*/
int iccp_sys_local_if_list_get_init()
{
    struct System *sys = NULL;
    struct nl_cb *cb;
    struct nl_cb *orig_cb;
    struct rtgenmsg rt_hdr = {
        .rtgen_family   = AF_UNSPEC,
    };
    int ret;
    int retry = 1;

    if (!(sys = system_get_instance()))
        return MCLAG_ERROR;

    while (retry)
    {
        retry = 0;
        ret = nl_send_simple(sys->route_sock, RTM_GETLINK, NLM_F_DUMP,
                             &rt_hdr, sizeof(rt_hdr));
        if (ret < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "send netlink msg error.");
            return ret;
        }

        orig_cb = nl_socket_get_cb(sys->route_sock);
        cb = nl_cb_clone(orig_cb);
        nl_cb_put(orig_cb);
        if (!cb)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "nl cb clone error.");
            return -ENOMEM;
        }

        nl_cb_set(cb, NL_CB_VALID, NL_CB_CUSTOM, iccp_valid_handler, sys);

        ret = nl_recvmsgs(sys->route_sock, cb);
        nl_cb_put(cb);
        if (ret < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "receive netlink msg error. ret = %d  errno = %d ", ret, errno);
            if (ret != -NLE_DUMP_INTR)
                return ret;
            retry = 1;
        }
    }

    return ret;
}

static void do_arp_learn_from_kernel(struct ndmsg *ndm, struct rtattr *tb[], int msgtype)
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct Msg *msg = NULL;
    struct ARPMsg *arp_msg = NULL, *arp_info = NULL;
    struct VLAN_ID *vlan_id_list = NULL;
    struct Msg *msg_send = NULL;

    char buf[MAX_BUFSIZE];
    size_t msg_len = 0;

    struct LocalInterface *lif_po = NULL, *arp_lif = NULL;

    int verify_arp = 0;
    int arp_update = 0;

    if (!(sys = system_get_instance()))
        return;

    /* Find local itf*/
    if (!(arp_lif = local_if_find_by_ifindex(ndm->ndm_ifindex)))
        return;

    /* create ARP msg*/
    memset(buf, 0, MAX_BUFSIZE);
    msg_len = sizeof(struct ARPMsg);
    arp_msg = (struct ARPMsg*)&buf;
    arp_msg->op_type = NEIGH_SYNC_LIF;
    sprintf(arp_msg->ifname, "%s", arp_lif->name);
    if (tb[NDA_DST])
        memcpy(&arp_msg->ipv4_addr, RTA_DATA(tb[NDA_DST]), RTA_PAYLOAD(tb[NDA_DST]));
    if (tb[NDA_LLADDR])
        memcpy(arp_msg->mac_addr, RTA_DATA(tb[NDA_LLADDR]), RTA_PAYLOAD(tb[NDA_LLADDR]));

    arp_msg->ipv4_addr = arp_msg->ipv4_addr;

    ICCPD_LOG_NOTICE(__FUNCTION__, "ARP type %s, state (%04X)(%d) ifindex [%d] (%s) ip %s, mac [%02X:%02X:%02X:%02X:%02X:%02X]",
                    msgtype == RTM_NEWNEIGH ? "New":"Del", ndm->ndm_state, fwd_neigh_state_valid(ndm->ndm_state),
                    ndm->ndm_ifindex, arp_lif->name,
                    show_ip_str(arp_msg->ipv4_addr),
                    arp_msg->mac_addr[0], arp_msg->mac_addr[1], arp_msg->mac_addr[2], arp_msg->mac_addr[3], arp_msg->mac_addr[4],
                    arp_msg->mac_addr[5]);

    /* Find MLACP itf, member of port-channel*/
    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        LIST_FOREACH(lif_po, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (lif_po->type != IF_T_PORT_CHANNEL)
                continue;

            if (!local_if_is_l3_mode(lif_po))
            {
                /* Is the L2 MLAG itf belong to a vlan?*/
                LIST_FOREACH(vlan_id_list, &(lif_po->vlan_list), port_next)
                {
                    if ( !(vlan_id_list->vlan_itf
                           && vlan_id_list->vlan_itf->ifindex == ndm->ndm_ifindex))
                        continue;
                    break;
                }

                if (!vlan_id_list)
                    continue;

                ICCPD_LOG_DEBUG(__FUNCTION__, "ARP is from mclag enabled member port of vlan %s",
                                vlan_id_list->vlan_itf->name);
            }
            else
            {
                /* Is the ARP belong to a L3 mode MLAG itf?*/
                if (ndm->ndm_ifindex != lif_po->ifindex)
                    continue;

                ICCPD_LOG_DEBUG(__FUNCTION__, "ARP is from mclag enabled intf %s", lif_po->name);
            }

            verify_arp = 1;

            break;
        }

        if (lif_po)
            break;
    }

    if (!(csm && lif_po))
        return;
    if (!verify_arp)
        return;

    /* update lif ARP*/
    TAILQ_FOREACH(msg, &MLACP(csm).arp_list, tail)
    {
        arp_info = (struct ARPMsg*)msg->buf;
        if (arp_info->ipv4_addr != arp_msg->ipv4_addr)
            continue;

        if (msgtype == RTM_DELNEIGH)
        {
            /* delete ARP*/
            TAILQ_REMOVE(&MLACP(csm).arp_list, msg, tail);
            free(msg->buf);
            free(msg);
            msg = NULL;
            ICCPD_LOG_DEBUG(__FUNCTION__, "Delete ARP %s", show_ip_str(arp_msg->ipv4_addr));
        }
        else
        {
            /* update ARP*/
            if (arp_info->op_type != arp_msg->op_type
                || strcmp(arp_info->ifname, arp_msg->ifname) != 0
                || memcmp(arp_info->mac_addr, arp_msg->mac_addr,
                          ETHER_ADDR_LEN) != 0)
            {
                arp_update = 1;
                arp_info->op_type = arp_msg->op_type;
                sprintf(arp_info->ifname, "%s", arp_msg->ifname);
                memcpy(arp_info->mac_addr, arp_msg->mac_addr, ETHER_ADDR_LEN);
                ICCPD_LOG_DEBUG(__FUNCTION__, "Update ARP for %s", show_ip_str(arp_msg->ipv4_addr));
            }
        }
        break;
    }

    if (msg && !arp_update)
        return;

    if (msgtype != RTM_DELNEIGH)
    {
        /* enquene lif_msg (add)*/
        if (!msg)
        {
            arp_msg->op_type = NEIGH_SYNC_LIF;
            if (iccp_csm_init_msg(&msg, (char*)arp_msg, msg_len) == 0)
            {
                mlacp_enqueue_arp(csm, msg);
                /*ICCPD_LOG_DEBUG(__FUNCTION__, "ARP-list enqueue: %s, add %s",
                                arp_msg->ifname, show_ip_str(arp_msg->ipv4_addr));*/
            }
            else
                ICCPD_LOG_WARN(__FUNCTION__, "Failed to enqueue ARP-list: %s, add %s",
                                arp_msg->ifname, show_ip_str(arp_msg->ipv4_addr));
        }

        /* enqueue iccp_msg (add)*/
        if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
        {
            arp_msg->op_type = NEIGH_SYNC_ADD;
            if (iccp_csm_init_msg(&msg_send, (char*)arp_msg, msg_len) == 0)
            {
                TAILQ_INSERT_TAIL(&(MLACP(csm).arp_msg_list), msg_send, tail);
                /*ICCPD_LOG_DEBUG(__FUNCTION__, "Enqueue ARP[ADD] message for %s",
                                show_ip_str(arp_msg->ipv4_addr));*/
            }
            else
                ICCPD_LOG_WARN(__FUNCTION__, "Failed to enqueue ARP[ADD] message for %s",
                                show_ip_str(arp_msg->ipv4_addr));

        }
    }
    else
    {
        /* enqueue iccp_msg (delete)*/
        if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
        {
            arp_msg->op_type = NEIGH_SYNC_DEL;
            if (iccp_csm_init_msg(&msg_send, (char*)arp_msg, msg_len) == 0)
            {
                TAILQ_INSERT_TAIL(&(MLACP(csm).arp_msg_list), msg_send, tail);
                /*ICCPD_LOG_DEBUG(__FUNCTION__, "Enqueue ARP[DEL] message for %s",
                                show_ip_str(arp_msg->ipv4_addr));*/
            }
            else
                ICCPD_LOG_WARN(__FUNCTION__, "Failed to enqueue ARP[DEL] message for %s",
                                show_ip_str(arp_msg->ipv4_addr));

        }
    }

    return;
}

static void do_ndisc_learn_from_kernel(struct ndmsg *ndm, struct rtattr *tb[], int msgtype)
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct Msg *msg = NULL;
    struct NDISCMsg *ndisc_msg = NULL, *ndisc_info = NULL;
    struct VLAN_ID *vlan_id_list = NULL;
    struct Msg *msg_send = NULL;

    char buf[MAX_BUFSIZE];
    size_t msg_len = 0;

    struct LocalInterface *lif_po = NULL, *ndisc_lif = NULL;

    int verify_neigh = 0;
    int neigh_update = 0;

    if (!(sys = system_get_instance()))
        return;

    /* Find local itf */
    if (!(ndisc_lif = local_if_find_by_ifindex(ndm->ndm_ifindex)))
        return;

    /* create NDISC msg */
    memset(buf, 0, MAX_BUFSIZE);
    msg_len = sizeof(struct NDISCMsg);
    ndisc_msg = (struct NDISCMsg *)&buf;
    ndisc_msg->op_type = NEIGH_SYNC_LIF;
    sprintf(ndisc_msg->ifname, "%s", ndisc_lif->name);
    if (tb[NDA_DST])
        memcpy(&ndisc_msg->ipv6_addr, RTA_DATA(tb[NDA_DST]), RTA_PAYLOAD(tb[NDA_DST]));
    if (tb[NDA_LLADDR])
        memcpy(ndisc_msg->mac_addr, RTA_DATA(tb[NDA_LLADDR]), RTA_PAYLOAD(tb[NDA_LLADDR]));

    ICCPD_LOG_NOTICE(__FUNCTION__, "ndisc type %s, state (%04X)(%d), ifindex [%d] (%s), ip %s, mac [%02X:%02X:%02X:%02X:%02X:%02X]",
                    msgtype == RTM_NEWNEIGH ? "New" : "Del", ndm->ndm_state, fwd_neigh_state_valid(ndm->ndm_state),
                    ndm->ndm_ifindex, ndisc_lif->name,
                    show_ipv6_str((char *)ndisc_msg->ipv6_addr),
                    ndisc_msg->mac_addr[0], ndisc_msg->mac_addr[1], ndisc_msg->mac_addr[2], ndisc_msg->mac_addr[3], ndisc_msg->mac_addr[4],
                    ndisc_msg->mac_addr[5]);

    /* Find MLACP itf, member of port-channel */
    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        LIST_FOREACH(lif_po, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (lif_po->type != IF_T_PORT_CHANNEL)
                continue;

            if (!local_if_is_l3_mode(lif_po))
            {
                /* Is the L2 MLAG itf belong to a vlan? */
                LIST_FOREACH(vlan_id_list, &(lif_po->vlan_list), port_next)
                {
                    if (!(vlan_id_list->vlan_itf && vlan_id_list->vlan_itf->ifindex == ndm->ndm_ifindex))
                        continue;
                    break;
                }

                if (!vlan_id_list)
                    continue;

                ICCPD_LOG_DEBUG(__FUNCTION__, "ND is from mclag enabled member port of vlan %s", vlan_id_list->vlan_itf->name);
            }
            else
            {
                /* Is the ND belong to a L3 mode MLAG itf? */
                if (ndm->ndm_ifindex != lif_po->ifindex)
                    continue;

                ICCPD_LOG_DEBUG(__FUNCTION__, "ND is from mclag enabled intf %s", lif_po->name);
            }

            verify_neigh = 1;

            break;
        }

        if (lif_po)
            break;
    }

    if (!(csm && lif_po))
        return;
    if (!verify_neigh)
        return;

    /* update lif ND */
    TAILQ_FOREACH(msg, &MLACP(csm).ndisc_list, tail)
    {
        ndisc_info = (struct NDISCMsg *)msg->buf;

        if (memcmp(&ndisc_info->ipv6_addr, &ndisc_msg->ipv6_addr, 16) != 0)
            continue;

        if (msgtype == RTM_DELNEIGH)
        {
            /* delete ND */
            TAILQ_REMOVE(&MLACP(csm).ndisc_list, msg, tail);
            free(msg->buf);
            free(msg);
            msg = NULL;
            ICCPD_LOG_DEBUG(__FUNCTION__, "Delete neighbor %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr));
        }
        else
        {
            /* update ND */
            if (ndisc_info->op_type != ndisc_info->op_type
                || strcmp(ndisc_info->ifname, ndisc_info->ifname) != 0
                || memcmp(ndisc_info->mac_addr, ndisc_info->mac_addr, ETHER_ADDR_LEN) != 0)
            {
                neigh_update = 1;
                ndisc_info->op_type = ndisc_msg->op_type;
                sprintf(ndisc_info->ifname, "%s", ndisc_msg->ifname);
                memcpy(ndisc_info->mac_addr, ndisc_msg->mac_addr, ETHER_ADDR_LEN);
                ICCPD_LOG_DEBUG(__FUNCTION__, "Update neighbor for %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr));
            }
        }
        break;
    }

    if (msg && !neigh_update)
        return;

    if (msgtype != RTM_DELNEIGH)
    {
        /* enquene lif_msg (add) */
        if (!msg)
        {
            ndisc_msg->op_type = NEIGH_SYNC_LIF;
            if (iccp_csm_init_msg(&msg, (char *)ndisc_msg, msg_len) == 0)
            {
                mlacp_enqueue_ndisc(csm, msg);
                /* ICCPD_LOG_DEBUG(__FUNCTION__, "Ndisc-list enqueue: %s, add %s", ndisc_msg->ifname, show_ipv6_str((char *)ndisc_msg->ipv6_addr)); */
            }
            else
                ICCPD_LOG_DEBUG(__FUNCTION__, "Failed to enqueue Ndisc-list: %s, add %s",
                                ndisc_msg->ifname, show_ipv6_str((char *)ndisc_msg->ipv6_addr));
        }

        /* enqueue iccp_msg (add) */
        if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
        {
            ndisc_msg->op_type = NEIGH_SYNC_ADD;
            if (iccp_csm_init_msg(&msg_send, (char *)ndisc_msg, msg_len) == 0)
            {
                TAILQ_INSERT_TAIL(&(MLACP(csm).ndisc_msg_list), msg_send, tail);
                /* ICCPD_LOG_DEBUG(__FUNCTION__, "Enqueue Ndisc[ADD] for %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr)); */
            }
            else
                ICCPD_LOG_DEBUG(__FUNCTION__, "Failed to enqueue Ndisc[ADD] message for %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr));

        }
    }
    else
    {
        /* enqueue iccp_msg (delete) */
        if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
        {
            ndisc_msg->op_type = NEIGH_SYNC_DEL;
            if (iccp_csm_init_msg(&msg_send, (char *)ndisc_msg, msg_len) == 0)
            {
                TAILQ_INSERT_TAIL(&(MLACP(csm).ndisc_msg_list), msg_send, tail);
                /* ICCPD_LOG_DEBUG(__FUNCTION__, "Enqueue Ndisc[DEL] for %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr)); */
            }
            else
                ICCPD_LOG_DEBUG(__FUNCTION__, "Failed to enqueue Ndisc[DEL] message for [%x:%x:%x:%x]", show_ipv6_str((char *)ndisc_msg->ipv6_addr));

        }
    }

    return;
}

int parse_rtattr_flags(struct rtattr *tb[], int max, struct rtattr *rta, int len, unsigned short flags)
{
    unsigned short type;

    memset(tb, 0, sizeof(struct rtattr *) * (max + 1));
    while (RTA_OK(rta, len))
    {
        type = rta->rta_type & ~flags;
        if ((type <= max) && (!tb[type]))
            tb[type] = rta;
        rta = RTA_NEXT(rta, len);
    }
    return 0;
}

int parse_rtattr(struct rtattr *tb[], int max, struct rtattr *rta, int len)
{
    return parse_rtattr_flags(tb, max, rta, len, 0);
}

void ifm_parse_rtattr(struct rtattr **tb, int max, struct rtattr *rta, int len)
{
    while (RTA_OK(rta, len))
    {
        if (rta->rta_type <= max)
            tb[rta->rta_type] = rta;
        rta = RTA_NEXT(rta, len);
    }
}

int do_one_neigh_request(struct nlmsghdr *n)
{
    struct ndmsg *ndm = NLMSG_DATA(n);
    int len = n->nlmsg_len;
    struct rtattr *tb[NDA_MAX + 1] = {0};

    if (n->nlmsg_type == NLMSG_DONE)
    {
        return 0;
    }

    /* process msg_type RTM_NEWNEIGH, RTM_GETNEIGH, RTM_DELNEIGH */
    if (n->nlmsg_type != RTM_NEWNEIGH && n->nlmsg_type  != RTM_DELNEIGH )
        return(0);

    len -= NLMSG_LENGTH(sizeof(*ndm));
    if (len < 0)
        return MCLAG_ERROR;

    ifm_parse_rtattr(tb, NDA_MAX, NDA_RTA(ndm), len);

    if (n->nlmsg_type == RTM_NEWNEIGH
		&& (ndm->ndm_state == NUD_INCOMPLETE
        || ndm->ndm_state == NUD_FAILED
        || ndm->ndm_state == NUD_NOARP
        || ndm->ndm_state == NUD_PERMANENT
        || ndm->ndm_state == NUD_NONE))
    {
        return(0);
    }

    if (!tb[NDA_DST] || ndm->ndm_type != RTN_UNICAST)
    {
        return(0);
    }

    if (ndm->ndm_family == AF_INET)
    {
        do_arp_learn_from_kernel(ndm, tb, n->nlmsg_type);
    }

    if (ndm->ndm_family == AF_INET6)
    {
        do_ndisc_learn_from_kernel(ndm, tb, n->nlmsg_type);
    }
    return(0);
}

static int iccp_neigh_valid_handler(struct nl_msg *msg, void *arg)
{
    struct nlmsghdr *nlh = nlmsg_hdr(msg);

    do_one_neigh_request(nlh);

    return 0;
}

int iccp_neigh_get_init()
{
    struct System *sys = NULL;
    struct nl_cb *cb;
    struct nl_cb *orig_cb;
    struct rtgenmsg rt_hdr = {
        .rtgen_family   = AF_UNSPEC,
    };
    int ret;
    int retry = 1;

    if (!(sys = system_get_instance()))
        return MCLAG_ERROR;

    while (retry)
    {
        retry = 0;
        ret = nl_send_simple(sys->route_sock, RTM_GETNEIGH, NLM_F_DUMP,
                             &rt_hdr, sizeof(rt_hdr));
        if (ret < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "Send netlink msg error.");
            return ret;
        }

        orig_cb = nl_socket_get_cb(sys->route_sock);
        cb = nl_cb_clone(orig_cb);
        nl_cb_put(orig_cb);
        if (!cb)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "nl cb clone error.");
            return -ENOMEM;
        }

        nl_cb_set(cb, NL_CB_VALID, NL_CB_CUSTOM, iccp_neigh_valid_handler, sys);

        ret = nl_recvmsgs(sys->route_sock, cb);
        nl_cb_put(cb);
        if (ret < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "Receive netlink msg error.");
            if (ret != -NLE_DUMP_INTR)
                return ret;

            retry = 1;
        }
    }

    return ret;
}

/*When received ARP packets from kernel, update arp information*/
void do_arp_update_from_reply_packet(unsigned int ifindex, unsigned int addr, uint8_t mac_addr[ETHER_ADDR_LEN])
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct Msg *msg = NULL;
    struct ARPMsg *arp_msg = NULL, *arp_info = NULL;
    struct VLAN_ID *vlan_id_list = NULL;
    struct Msg *msg_send = NULL;

    char buf[MAX_BUFSIZE];
    size_t msg_len = 0;

    struct LocalInterface *lif_po = NULL, *arp_lif = NULL;

    int verify_arp = 0;

    if (!(sys = system_get_instance()))
        return;

    /* Find local itf*/
    if (!(arp_lif = local_if_find_by_ifindex(ifindex)))
        return;

    /* create ARP msg*/
    memset(buf, 0, MAX_BUFSIZE);
    msg_len = sizeof(struct ARPMsg);
    arp_msg = (struct ARPMsg*)&buf;
    arp_msg->op_type = NEIGH_SYNC_LIF;
    sprintf(arp_msg->ifname, "%s", arp_lif->name);
    memcpy(&arp_msg->ipv4_addr, &addr, 4);
    memcpy(arp_msg->mac_addr, mac_addr, 6);

    ICCPD_LOG_DEBUG(__FUNCTION__, "ARP ifindex [%d] (%s) ip %s mac [%02X:%02X:%02X:%02X:%02X:%02X]",
                    ifindex, arp_lif->name,
                    show_ip_str(arp_msg->ipv4_addr),
                    arp_msg->mac_addr[0], arp_msg->mac_addr[1], arp_msg->mac_addr[2], arp_msg->mac_addr[3], arp_msg->mac_addr[4],
                    arp_msg->mac_addr[5]);

    /* Find MLACP itf, member of port-channel*/
    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        LIST_FOREACH(lif_po, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (lif_po->type != IF_T_PORT_CHANNEL)
                continue;

            if (!local_if_is_l3_mode(lif_po))
            {
                /* Is the L2 MLAG itf belong to a vlan?*/
                LIST_FOREACH(vlan_id_list, &(lif_po->vlan_list), port_next)
                {
                    if ( !(vlan_id_list->vlan_itf
                           && vlan_id_list->vlan_itf->ifindex == ifindex))
                        continue;
                    break;
                }

                if (!vlan_id_list)
                    continue;
                ICCPD_LOG_DEBUG(__FUNCTION__, "ARP is from mclag enabled port %s of vlan %s",
                                              lif_po->name, vlan_id_list->vlan_itf->name);
            }
            else
            {
                /* Is the ARP belong to a L3 mode MLAG itf?*/
                if (ifindex != lif_po->ifindex)
                    continue;
                ICCPD_LOG_DEBUG(__FUNCTION__, "ARP is from mclag enabled intf %s", lif_po->name);
            }

            verify_arp = 1;

            break;
        }

        if (lif_po)
            break;
    }

    if (!(csm && lif_po))
        return;
    if (!verify_arp)
        return;

    if (iccp_check_if_addr_from_netlink(AF_INET, (uint8_t *)&addr, arp_lif))
    {
        ICCPD_LOG_DEBUG(__FUNCTION__, "ARP %s is identical with the ip address of interface %s",
                                      show_ip_str(arp_msg->ipv4_addr), arp_lif->name);
        return;
    }

    /* update lif ARP*/
    TAILQ_FOREACH(msg, &MLACP(csm).arp_list, tail)
    {
        arp_info = (struct ARPMsg*)msg->buf;
        if (arp_info->ipv4_addr != arp_msg->ipv4_addr)
            continue;

        /* update ARP*/
        if (arp_info->op_type != arp_msg->op_type
            || strcmp(arp_info->ifname, arp_msg->ifname) != 0
            || memcmp(arp_info->mac_addr, arp_msg->mac_addr,
                      ETHER_ADDR_LEN) != 0)
        {
            arp_info->op_type = arp_msg->op_type;
            sprintf(arp_info->ifname, "%s", arp_msg->ifname);
            memcpy(arp_info->mac_addr, arp_msg->mac_addr, ETHER_ADDR_LEN);
            ICCPD_LOG_NOTICE(__FUNCTION__, "Update ARP for %s by ARP reply, intf %s mac [%02X:%02X:%02X:%02X:%02X:%02X]",
                            show_ip_str(arp_msg->ipv4_addr), arp_msg->ifname,
                            arp_msg->mac_addr[0], arp_msg->mac_addr[1], arp_msg->mac_addr[2], arp_msg->mac_addr[3], arp_msg->mac_addr[4], arp_msg->mac_addr[5]);
        }
        break;
    }

    /* enquene lif_msg (add)*/
    if (!msg)
    {
        arp_msg->op_type = NEIGH_SYNC_LIF;
        if (iccp_csm_init_msg(&msg, (char*)arp_msg, msg_len) == 0)
        {
            mlacp_enqueue_arp(csm, msg);
            /*ICCPD_LOG_DEBUG(__FUNCTION__, "ARP-list enqueue: %s, add %s",
                            arp_msg->ifname, show_ip_str(arp_msg->ipv4_addr));*/
        }
        else
            ICCPD_LOG_WARN(__FUNCTION__, "Failed to enqueue ARP-list: %s, add %s",
                            arp_msg->ifname, show_ip_str(arp_msg->ipv4_addr));
    }

    /* enqueue iccp_msg (add)*/
    if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
    {
        arp_msg->op_type = NEIGH_SYNC_ADD;
        if (iccp_csm_init_msg(&msg_send, (char*)arp_msg, msg_len) == 0)
        {
            TAILQ_INSERT_TAIL(&(MLACP(csm).arp_msg_list), msg_send, tail);
            /*ICCPD_LOG_DEBUG(__FUNCTION__, "Enqueue ARP[ADD] for %s",
                            show_ip_str(arp_msg->ipv4_addr));*/
        }
        else
            ICCPD_LOG_WARN(__FUNCTION__, "Failed to enqueue ARP[ADD] message for %s",
                            show_ip_str(arp_msg->ipv4_addr));
    }

    return;
}

void do_ndisc_update_from_reply_packet(unsigned int ifindex, char *ipv6_addr, uint8_t mac_addr[ETHER_ADDR_LEN])
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct Msg *msg = NULL;
    struct NDISCMsg *ndisc_msg = NULL, *ndisc_info = NULL;
    struct VLAN_ID *vlan_id_list = NULL;
    struct Msg *msg_send = NULL;
    char mac_str[18] = "";
    uint8_t null_mac[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };

    char buf[MAX_BUFSIZE];
    size_t msg_len = 0;

    struct LocalInterface *lif_po = NULL, *ndisc_lif = NULL;

    int verify_ndisc = 0;

    if (!(sys = system_get_instance()))
        return;

    /* Find local itf */
    if (!(ndisc_lif = local_if_find_by_ifindex(ifindex)))
        return;

    sprintf(mac_str, "%02x:%02x:%02x:%02x:%02x:%02x", mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);

    /* create Ndisc msg */
    memset(buf, 0, MAX_BUFSIZE);
    msg_len = sizeof(struct NDISCMsg);
    ndisc_msg = (struct NDISCMsg *)&buf;
    ndisc_msg->op_type = NEIGH_SYNC_LIF;
    sprintf(ndisc_msg->ifname, "%s", ndisc_lif->name);
    memcpy((char *)ndisc_msg->ipv6_addr, ipv6_addr, 16);
    memcpy(ndisc_msg->mac_addr, mac_addr, ETHER_ADDR_LEN);

    ICCPD_LOG_DEBUG(__FUNCTION__, "nd ifindex [%d] (%s) ip %s mac %s",
                    ifindex, ndisc_lif->name, show_ipv6_str(ipv6_addr), mac_str);

    /* Find MLACP itf, member of port-channel */
    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        LIST_FOREACH(lif_po, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (lif_po->type != IF_T_PORT_CHANNEL)
                continue;

            if (!local_if_is_l3_mode(lif_po))
            {
                /* Is the L2 MLAG itf belong to a vlan? */
                LIST_FOREACH(vlan_id_list, &(lif_po->vlan_list), port_next)
                {
                    if (!(vlan_id_list->vlan_itf && vlan_id_list->vlan_itf->ifindex == ifindex))
                        continue;
                    break;
                }

                if (!vlan_id_list)
                    continue;
                ICCPD_LOG_DEBUG(__FUNCTION__, "ND is from mclag enabled port %s of vlan %s", lif_po->name, vlan_id_list->vlan_itf->name);
            }
            else
            {
                /* Is the ND belong to a L3 mode MLAG itf? */
                if (ifindex != lif_po->ifindex)
                    continue;
                ICCPD_LOG_DEBUG(__FUNCTION__, "ND is from mclag enabled port %s", lif_po->name);
            }

            verify_ndisc = 1;

            break;
        }

        if (lif_po)
            break;
    }

    if (!(csm && lif_po))
        return;
    if (!verify_ndisc)
        return;

    if (iccp_check_if_addr_from_netlink(AF_INET6, (uint8_t *)ndisc_msg->ipv6_addr, ndisc_lif))
    {
        ICCPD_LOG_DEBUG(__FUNCTION__, "NA %s is identical with the ipv6 address of interface %s",
                                      show_ipv6_str((char *)ndisc_msg->ipv6_addr), ndisc_lif->name);
        return;
    }

    /* update lif ND */
    TAILQ_FOREACH(msg, &MLACP(csm).ndisc_list, tail)
    {
        ndisc_info = (struct NDISCMsg *)msg->buf;

        if (memcmp((char *)ndisc_info->ipv6_addr, (char *)ndisc_msg->ipv6_addr, 16) != 0)
            continue;

        /* If MAC addr is NULL, use the old one */
        if (memcmp(mac_addr, null_mac, ETHER_ADDR_LEN) == 0)
        {
            memcpy(ndisc_msg->mac_addr, ndisc_info->mac_addr, ETHER_ADDR_LEN);
            sprintf(mac_str, "%02x:%02x:%02x:%02x:%02x:%02x", ndisc_info->mac_addr[0], ndisc_info->mac_addr[1],
                    ndisc_info->mac_addr[2], ndisc_info->mac_addr[3], ndisc_info->mac_addr[4], ndisc_info->mac_addr[5]);
        }

        /* update ND */
        if (ndisc_info->op_type != ndisc_msg->op_type
            || strcmp(ndisc_info->ifname, ndisc_msg->ifname) != 0
            || memcmp(ndisc_info->mac_addr, ndisc_msg->mac_addr, ETHER_ADDR_LEN) != 0)
        {
            ndisc_info->op_type = ndisc_msg->op_type;
            sprintf(ndisc_info->ifname, "%s", ndisc_msg->ifname);
            memcpy(ndisc_info->mac_addr, ndisc_msg->mac_addr, ETHER_ADDR_LEN);
            ICCPD_LOG_DEBUG(__FUNCTION__, "Update ND for %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr));
        }
        break;
    }

    /* enquene lif_msg (add) */
    if (!msg)
    {
        /* If MAC addr is NULL, and same ipv6 item is not exist in ndisc_list */
        if (memcmp(mac_addr, null_mac, ETHER_ADDR_LEN) == 0)
        {
            return;
        }

        ndisc_msg->op_type = NEIGH_SYNC_LIF;
        if (iccp_csm_init_msg(&msg, (char *)ndisc_msg, msg_len) == 0)
        {
            mlacp_enqueue_ndisc(csm, msg);
            /* ICCPD_LOG_DEBUG(__FUNCTION__, "NDISC-list enqueue: %s, add %s", ndisc_msg->ifname, show_ipv6_str((char *)ndisc_msg->ipv6_addr)); */
        }
        else
            ICCPD_LOG_WARN(__FUNCTION__, "Failed to enqueue NDISC-list: %s, add %s", ndisc_msg->ifname, show_ipv6_str((char *)ndisc_msg->ipv6_addr));
    }

    if (iccp_netlink_neighbor_request(AF_INET6, (uint8_t *)ndisc_msg->ipv6_addr, 1, ndisc_msg->mac_addr, ndisc_msg->ifname) < 0)
    {
        ICCPD_LOG_WARN(__FUNCTION__, "Failed to add ND entry(%s, %s, %s) to kernel",
                        ndisc_msg->ifname, show_ipv6_str((char *)ndisc_msg->ipv6_addr), mac_str);
        return;
    }

    /* enqueue iccp_msg (add) */
    if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
    {
        ndisc_msg->op_type = NEIGH_SYNC_ADD;
        if (iccp_csm_init_msg(&msg_send, (char *)ndisc_msg, msg_len) == 0)
        {
            TAILQ_INSERT_TAIL(&(MLACP(csm).ndisc_msg_list), msg_send, tail);
            /* ICCPD_LOG_DEBUG(__FUNCTION__, "Enqueue ND[ADD] for %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr)); */
        }
        else
            ICCPD_LOG_WARN(__FUNCTION__, "Failed to enqueue ND[ADD] message for %s", show_ipv6_str((char *)ndisc_msg->ipv6_addr));
    }

    return;
}
void iccp_from_netlink_port_state_handler( char * ifname, int state)
{
    struct CSM *csm = NULL;
    struct LocalInterface *lif_po = NULL;
    struct System *sys;
    int po_is_active = 0;

    if ((sys = system_get_instance()) == NULL)
    {
        ICCPD_LOG_WARN(__FUNCTION__, "Failed to obtain System instance.");
        return;
    }

    po_is_active = (state == PORT_STATE_UP);

    /* traverse all CSM */
    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        /*If peer-link changes to down or up */
        if (strcmp(ifname, csm->peer_itf_name) == 0)
        {
            if (po_is_active == 0)
                mlacp_peerlink_down_handler(csm);
            else
                mlacp_peerlink_up_handler(csm);

            break;
        }

        LIST_FOREACH(lif_po, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (lif_po->type == IF_T_PORT_CHANNEL && strncmp(lif_po->name, ifname, MAX_L_PORT_NAME) == 0)
            {
                mlacp_portchannel_state_handler(csm, lif_po, po_is_active);
            }
        }
    }

    return;
}

void iccp_parse_if_vlan_info_from_netlink(struct nlmsghdr *n)
{
    struct LocalInterface *lif = NULL;
    int msglen = 0;

    msglen = n->nlmsg_len;

    while (NLMSG_OK(n, msglen))
    {
        struct ifinfomsg *ifm = NLMSG_DATA(n);
        int len = n->nlmsg_len;
        struct rtattr *tb[IFLA_MAX + 1] = {0};

        if (n->nlmsg_type != RTM_NEWLINK)
        {
            return;
        }

        len -= NLMSG_LENGTH(sizeof(*ifm));
        if (len < 0)
        {
            ICCPD_LOG_WARN(__FUNCTION__, "BUG: wrong nlmsg len %d\n", len);
            return;
        }

        if (ifm->ifi_family != AF_BRIDGE)
        {
            return;
        }

        if ((lif = local_if_find_by_ifindex(ifm->ifi_index)) != NULL)
        {
            parse_rtattr(tb, IFLA_MAX, IFLA_RTA(ifm), len);

            /* if AF_SPEC isn't there, vlan table is not preset for this port */
            if (!tb[IFLA_AF_SPEC])
            {
                ICCPD_LOG_WARN(__FUNCTION__, "Vlan table is not preset for %d", ifm->ifi_index);
                return;
            }
            else
            {
                struct rtattr *i, *list = tb[IFLA_AF_SPEC];
                int rem = RTA_PAYLOAD(list);
                struct VLAN_ID *vlan = NULL;

                /*set vlan flag is removed*/
                LIST_FOREACH(vlan, &(lif->vlan_list), port_next)
                {
                    vlan->vlan_removed = 1;
                }

                for (i = RTA_DATA(list); RTA_OK(i, rem); i = RTA_NEXT(i, rem))
                {
                    struct bridge_vlan_info *vinfo;

                    if (i->rta_type != IFLA_BRIDGE_VLAN_INFO)
                        continue;

                    vinfo = RTA_DATA(i);

                    local_if_add_vlan(lif, vinfo->vid);
                }

                /*After update vlan list, remove unused item*/
                LIST_FOREACH(vlan, &(lif->vlan_list), port_next)
                {
                    if (vlan->vlan_removed == 1)
                    {
                        ICCPD_LOG_DEBUG(__FUNCTION__, "Remove %s from VLAN %d", lif->name, vlan->vid);

                        LIST_REMOVE(vlan, port_next);
                        free(vlan);
                    }
                }
            }
        }

        n = NLMSG_NEXT(n, msglen);
    }
}
