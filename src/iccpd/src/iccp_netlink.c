/*
 * iccp_netlink.c
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

#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdlib.h>

#include <sys/epoll.h>
#include <sys/types.h>
#include <sys/socket.h>

#include <netlink/netlink.h>
#include <netlink/msg.h>
#include <netlink/attr.h>
#include <netlink/types.h>
#include <netlink/route/link.h>
#include <netlink/route/route.h>
#include <netlink/route/neighbour.h>
#include <netlink/route/link/bridge.h>
#include <netlink/cli/utils.h>

#include <linux/if.h>
#include <linux/if_ether.h>
#include <linux/if_arp.h>
#include <linux/if_team.h>
#include <linux/types.h>
#include <linux/socket.h>
#include <linux/in6.h>

#include "../include/system.h"
#include "../include/iccp_ifm.h"
#include "../include/port.h"
#include "../include/iccp_csm.h"
#include "../include/logger.h"
#include "../include/scheduler.h"
#include "../include/mlacp_link_handler.h"
#include "../include/msg_format.h"
#include "../include/iccp_netlink.h"

/**
 * SECTION: Netlink helpers
 */
/* \cond HIDDEN_SYMBOLS */
#ifndef SOL_NETLINK
#define SOL_NETLINK 270
#endif

#define ARRAY_SIZE(array_name) (sizeof(array_name) / sizeof(array_name[0]))

#ifndef NETLINK_BROADCAST_SEND_ERROR
#define NETLINK_BROADCAST_SEND_ERROR    0x4
#endif

static int iccp_ack_handler(struct nl_msg *msg, void *arg)
{
    bool *acked = arg;

    *acked = true;

    return NL_STOP;
}

static int iccp_seq_check_handler(struct nl_msg *msg, void *arg)
{
    unsigned int *seq = arg;
    struct nlmsghdr *hdr = nlmsg_hdr(msg);

    if (hdr->nlmsg_seq != *seq)
        return NL_SKIP;

    return NL_OK;
}

int iccp_send_and_recv(struct System *sys, struct nl_msg *msg,
                       int (*valid_handler)(struct nl_msg *, void *),
                       void *valid_data)
{
    int ret;
    struct nl_cb *cb;
    struct nl_cb *orig_cb;
    bool acked;
    unsigned int seq = sys->genric_sock_seq++;
    int err;

    ret = nl_send_auto(sys->genric_sock, msg);
    nlmsg_free(msg);
    if (ret < 0)
        return ret;

    orig_cb = nl_socket_get_cb(sys->genric_sock);
    cb = nl_cb_clone(orig_cb);
    nl_cb_put(orig_cb);
    if (!cb)
        return -ENOMEM;

    nl_cb_set(cb, NL_CB_ACK, NL_CB_CUSTOM, iccp_ack_handler, &acked);
    nl_cb_set(cb, NL_CB_SEQ_CHECK, NL_CB_CUSTOM, iccp_seq_check_handler, &seq);
    if (valid_handler)
        nl_cb_set(cb, NL_CB_VALID, NL_CB_CUSTOM, valid_handler, valid_data);

    /* There is a bug in libnl. When implicit sequence number checking is in
     * use the expected next number is increased when NLMSG_DONE is
     * received. The ACK which comes after that correctly includes the
     * original sequence number. However libnl is checking that number
     * against the incremented one and therefore ack handler is never called
     * and nl_recvmsgs finished with an error. To resolve this, custom
     * sequence number checking is used here.
     */

    acked = false;

    while (!acked)
    {
        ret = nl_recvmsgs(sys->genric_sock, cb);
        if (ret)
        {
            err = ret;
            goto put_cb;
        }
    }

    err = 0;
 put_cb:
    nl_cb_put(cb);
    return err;
}

int iccp_get_portchannel_member_list_handler(struct nl_msg *msg, void * arg)
{
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    struct nlattr *attrs[TEAM_ATTR_MAX + 1];
    struct nlattr *nl_port;
    struct nlattr *port_attrs[TEAM_ATTR_PORT_MAX + 1];
    struct LocalInterface* lif = NULL;
    struct LocalInterface* local_if_member = NULL;
    struct CSM* csm;
    int i;
    uint32_t ifindex = 0;
    struct System* sys = NULL;
    struct LocalInterface* local_if = NULL;
    char temp_buf[512];
    int len = 0;

    sys = system_get_instance();
    if (sys == NULL)
        return 0;

    genlmsg_parse(nlh, 0, attrs, TEAM_ATTR_MAX, NULL);

    if (attrs[TEAM_ATTR_TEAM_IFINDEX])
        ifindex = nla_get_u32(attrs[TEAM_ATTR_TEAM_IFINDEX]);

    local_if = local_if_find_by_ifindex(ifindex);

    if (!local_if)
        return NL_SKIP;

    if (local_if->type != IF_T_PORT_CHANNEL)
        return NL_SKIP;

    csm = local_if->csm;

    if (csm)
    {
        if (!attrs[TEAM_ATTR_LIST_PORT])
            return NL_SKIP;

        nla_for_each_nested(nl_port, attrs[TEAM_ATTR_LIST_PORT], i)
        {
            uint32_t member_index;

            if (nla_parse_nested(port_attrs, TEAM_ATTR_PORT_MAX, nl_port, NULL))
            {
                ICCPD_LOG_ERR(__FUNCTION__, "Failed to parse nested attributes.");
                return NL_SKIP;
            }

            if (!port_attrs[TEAM_ATTR_PORT_IFINDEX])
            {
                ICCPD_LOG_ERR(__FUNCTION__, "ifindex port attribute not found.");
                return NL_SKIP;
            }

            member_index = nla_get_u32(port_attrs[TEAM_ATTR_PORT_IFINDEX]);

            local_if_member = local_if_find_by_ifindex(member_index);
            if (local_if_member == NULL)
            {

                ICCPD_LOG_WARN(__FUNCTION__, "%s: Failed to find a port instance (%d).",
                               local_if->name, member_index);
                continue;
            }

            if (port_attrs[TEAM_ATTR_PORT_REMOVED] && local_if_member->po_id != -1)
            {
                local_if_member->po_id = -1;
                mlacp_unbind_local_if(local_if_member);
            }
            else if ( local_if_member->po_id == -1)
            {
                local_if_member->po_id = local_if->po_id;
                mlacp_bind_local_if(local_if->csm, local_if_member);
            }
        }

        memset(temp_buf, 0, 512);
        LIST_FOREACH(lif, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (lif->type == IF_T_PORT && lif->po_id == local_if->po_id)
            {
                if (strlen(temp_buf) != 0)
                    len += snprintf(temp_buf + len, 512 - len, "%s", ",");

                len += snprintf(temp_buf + len, 512 - len, "%s", lif->name);
            }
        }

        if (strcmp(temp_buf, local_if->portchannel_member_buf))
        {
            memset(local_if->portchannel_member_buf, 0, 512);
            memcpy(local_if->portchannel_member_buf, temp_buf, sizeof(local_if->portchannel_member_buf) - 1);

            if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
            {
                /* portchannel member changed, update port isolate attribute*/
                update_peerlink_isolate_from_all_csm_lif(csm);
            }
        }
    }
    else /*peerlink portchannel */
    {
        if (local_if->is_peer_link)
        {
            LIST_FOREACH(csm, &(sys->csm_list), next)
            {
                if (csm->peer_link_if == local_if )
                {
                    break;
                }
            }

            if (csm == NULL)
                return 0;

            nla_for_each_nested(nl_port, attrs[TEAM_ATTR_LIST_PORT], i)
            {
                uint32_t member_index;

                if (nla_parse_nested(port_attrs, TEAM_ATTR_PORT_MAX, nl_port, NULL))
                {
                    ICCPD_LOG_WARN(__FUNCTION__, "Failed to parse nested attributes.");
                    return NL_SKIP;
                }

                if (!port_attrs[TEAM_ATTR_PORT_IFINDEX])
                {
                    ICCPD_LOG_WARN(__FUNCTION__, "ifindex port attribute not found.");
                    return NL_SKIP;
                }

                member_index = nla_get_u32(port_attrs[TEAM_ATTR_PORT_IFINDEX]);

                local_if_member = local_if_find_by_ifindex(member_index);
                if (local_if_member == NULL)
                {
                    ICCPD_LOG_WARN(__FUNCTION__, "%s: Failed to find a port instance (%d).",
                                   local_if->name, member_index);
                    continue;
                }

                if (port_attrs[TEAM_ATTR_PORT_REMOVED] && local_if_member->po_id != -1)
                {
                    local_if_member->po_id = -1;
                    if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
                    {
                        /*link removed from portchannel, must be enabled mac learn*/
                        set_peerlink_mlag_port_learn(local_if_member, 1);
                    }

                    continue;
                }
                else if ( local_if_member->po_id == -1)
                {
                    local_if_member->po_id = local_if->po_id;

                    if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
                    {
                        /*link add to portchannel, must be disabled mac learn*/
                        set_peerlink_mlag_port_learn(local_if, 0);
                    }
                }
            }

            memset(temp_buf, 0, 512);
            LIST_FOREACH(lif, &(sys->lif_list), system_next)
            {
                if (lif->type == IF_T_PORT && lif->po_id == local_if->po_id)
                {
                    if (strlen(temp_buf) != 0)
                        len += snprintf(temp_buf + len, 512 - len, "%s", ",");

                    len += snprintf(temp_buf + len, 512 - len, "%s", lif->name);
                }
            }

            if (strcmp(temp_buf, local_if->portchannel_member_buf))
            {
                memset(local_if->portchannel_member_buf, 0, 512);
                memcpy(local_if->portchannel_member_buf, temp_buf, sizeof(local_if->portchannel_member_buf) - 1);
            }
        }
    }

    return 0;
}

int iccp_genric_socket_team_family_get()
{
    struct System* sys = NULL;
    int err = 0;
    int grp_id = 0;

    if ((sys = system_get_instance()) == NULL )
        return MCLAG_ERROR;
    if (sys->family < 0)
    {
        sys->family = genl_ctrl_resolve(sys->genric_sock, TEAM_GENL_NAME);

        while (sys->family < 0)
        {
            sleep(1);

            /*If no portchannel configuration, teamd will not started, genl_ctrl_resolve() will return <0 forever */
            /*Only log error message 5 times*/

            ICCPD_LOG_ERR(__FUNCTION__, "Failed to resolve netlink family. %d of TEAM_GENL_NAME %s ", sys->family, TEAM_GENL_NAME);
            sys->family = genl_ctrl_resolve(sys->genric_sock, TEAM_GENL_NAME);

        }

        grp_id = genl_ctrl_resolve_grp(sys->genric_sock, TEAM_GENL_NAME,
                                       TEAM_GENL_CHANGE_EVENT_MC_GRP_NAME);
        if (grp_id < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "Failed to resolve netlink multicast groups. %d", grp_id);
        }

        err = nl_socket_add_membership(sys->genric_event_sock, grp_id);
        if (err < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "Failed to add netlink membership.");

        }
    }

    return err;
}

int iccp_get_port_member_list(struct LocalInterface* lif)
{
    struct System *sys;
    struct nl_msg *msg;
    int err;

    sys = system_get_instance();
    if (sys == NULL)
        return 0;

    msg = nlmsg_alloc();
    if (!msg)
        return -ENOMEM;

    err = iccp_genric_socket_team_family_get();
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "genric socket family get err err = %d . errno = %d", err, errno);
        return err;
    }

    genlmsg_put(msg, NL_AUTO_PID, sys->genric_sock_seq, sys->family, 0, 0,
                TEAM_CMD_PORT_LIST_GET, 0);
    nla_put_u32(msg, TEAM_ATTR_TEAM_IFINDEX, lif->ifindex);

    err = iccp_send_and_recv(sys, msg, iccp_get_portchannel_member_list_handler, lif);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "recv msg err err = %d . errno = %d", err, errno);
        return err;
    }

    return 0;
}

int iccp_netlink_if_hwaddr_set(uint32_t ifindex, uint8_t *addr, unsigned int addr_len)
{
    struct rtnl_link *link;
    int err;
    struct nl_addr *nl_addr;
    struct System* sys = NULL;

    if (!(sys = system_get_instance()))
        return MCLAG_ERROR;

    link = rtnl_link_alloc();
    if (!link)
        return -ENOMEM;

    nl_addr = nl_addr_build(AF_UNSPEC, (void *)addr, addr_len);
    if (!nl_addr)
    {
        err = -ENOMEM;
        goto errout;
    }

    rtnl_link_set_ifindex(link, ifindex);
    rtnl_link_set_addr(link, nl_addr);

    err = rtnl_link_change(sys->route_sock, link, link, 0);

    nl_addr_put(nl_addr);

 errout:
    rtnl_link_put(link);
    return err;
}

#define SET_MAC_STR(buf, macArray) \
    snprintf(buf, 64, "%02x:%02x:%02x:%02x:%02x:%02x", \
             macArray[0], macArray[1], macArray[2], \
             macArray[3], macArray[4], macArray[5]);

void iccp_set_interface_ipadd_mac(struct LocalInterface *lif, char * mac_addr )
{
    struct IccpSyncdHDr * msg_hdr;
    mclag_sub_option_hdr_t * sub_msg;
    char msg_buf[4096];
    struct System *sys;

    int src_len = 0, dst_len = 0;

    sys = system_get_instance();
    if (sys == NULL)
        return;

    memset(msg_buf, 0, 4095);

    msg_hdr = (struct IccpSyncdHDr *)msg_buf;
    msg_hdr->ver = 1;
    msg_hdr->type = MCLAG_MSG_TYPE_SET_MAC;
    msg_hdr->len = sizeof(struct IccpSyncdHDr);

    /*sub msg src*/
    sub_msg = (mclag_sub_option_hdr_t *)&msg_buf[msg_hdr->len];
    sub_msg->op_type = MCLAG_SUB_OPTION_TYPE_SET_MAC_SRC;

    /*src_len = snprintf((char *)sub_msg->data, 512, "%s:%s/%d", lif->name,show_ip_str(htonl(lif->ipv4_addr)),lif->prefixlen);*/
    src_len = snprintf((char *)sub_msg->data, 512, "%s", lif->name);

    sub_msg->op_len = src_len;

    /*sub msg dst */
    msg_hdr->len += sub_msg->op_len;
    msg_hdr->len += sizeof(mclag_sub_option_hdr_t);
    sub_msg = (mclag_sub_option_hdr_t  *)&msg_buf[msg_hdr->len];
    sub_msg->op_type = MCLAG_SUB_OPTION_TYPE_SET_MAC_DST;

    dst_len = strlen(mac_addr);
    memcpy(sub_msg->data, mac_addr, dst_len);

    ICCPD_LOG_NOTICE(__FUNCTION__, "If name %s ip %s mac %s", lif->name, show_ip_str(htonl(lif->ipv4_addr)), sub_msg->data);

    sub_msg->op_len = dst_len;
    msg_hdr->len += sizeof(mclag_sub_option_hdr_t);
    msg_hdr->len += sub_msg->op_len;

    /*send msg*/
    if (sys->sync_fd)
        write(sys->sync_fd, msg_buf, msg_hdr->len);

    return;
}

int iccp_netlink_if_startup_set(uint32_t ifindex)
{
    struct rtnl_link *link;
    int err;
    struct System *sys = NULL;

    if (!(sys = system_get_instance()))
        return MCLAG_ERROR;

    link = rtnl_link_alloc();
    if (!link)
        return -ENOMEM;

    rtnl_link_set_ifindex(link, ifindex);
    rtnl_link_set_flags(link, IFF_UP);

    err = rtnl_link_change(sys->route_sock, link, link, 0);

errout:
    rtnl_link_put(link);
    return err;
}

int iccp_netlink_if_shutdown_set(uint32_t ifindex)
{
    struct rtnl_link *link;
    int err;
    struct System *sys = NULL;

    if (!(sys = system_get_instance()))
        return MCLAG_ERROR;

    link = rtnl_link_alloc();
    if (!link)
        return -ENOMEM;

    rtnl_link_set_ifindex(link, ifindex);
    rtnl_link_unset_flags(link, IFF_UP);

    err = rtnl_link_change(sys->route_sock, link, link, 0);

errout:
    rtnl_link_put(link);
    return err;
}
void update_if_ipmac_on_standby(struct LocalInterface* lif_po)
{
    struct CSM* csm;
    uint8_t null_mac[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
    struct VLAN_ID *vlan = NULL;

    csm = lif_po->csm;
    struct LocalInterface* lif_Bri;
    char macaddr[64];
    int ret = 0;

    if (!csm)
        return;

    if (lif_po->type != IF_T_PORT_CHANNEL)
        return;

    if (csm->role_type != STP_ROLE_STANDBY)
    {
        return;
    }

    if (memcmp(MLACP(csm).remote_system.system_id, null_mac, ETHER_ADDR_LEN) == 0)
        return;

    /*Set new mac*/
    if (memcmp( lif_po->mac_addr, MLACP(csm).remote_system.system_id, ETHER_ADDR_LEN) != 0)
    {
        /*Backup old sysmac*/
        memcpy(lif_po->mac_addr_ori, lif_po->mac_addr, ETHER_ADDR_LEN);

        ICCPD_LOG_NOTICE(__FUNCTION__,
                        "%s Change the system-id of %s from [%02X:%02X:%02X:%02X:%02X:%02X] to [%02X:%02X:%02X:%02X:%02X:%02X].",
                        (csm->role_type == STP_ROLE_STANDBY) ? "Standby" : "Active",
                        lif_po->name,  lif_po->mac_addr[0], lif_po->mac_addr[1], lif_po->mac_addr[2], lif_po->mac_addr[3], lif_po->mac_addr[4], lif_po->mac_addr[5],
                        MLACP(csm).remote_system.system_id[0], MLACP(csm).remote_system.system_id[1], MLACP(csm).remote_system.system_id[2], MLACP(csm).remote_system.system_id[3], MLACP(csm).remote_system.system_id[4], MLACP(csm).remote_system.system_id[5]);

        ret =  iccp_netlink_if_hwaddr_set(lif_po->ifindex,  MLACP(csm).remote_system.system_id, ETHER_ADDR_LEN);
        if (ret != 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "Set %s mac error, ret = %d", lif_po->name, ret);
        }

        /* Refresh link local address according the new MAC */
        iccp_netlink_if_shutdown_set(lif_po->ifindex);
        iccp_netlink_if_startup_set(lif_po->ifindex);
    }

    /*Set portchannel ip mac */
    memset(macaddr, 0, 64);
    SET_MAC_STR(macaddr, MLACP(csm).remote_system.system_id);
    if (local_if_is_l3_mode(lif_po))
    {
        if (memcmp(lif_po->l3_mac_addr, MLACP(csm).remote_system.system_id, ETHER_ADDR_LEN) != 0)
        {
            iccp_set_interface_ipadd_mac(lif_po, macaddr );
            memcpy(lif_po->l3_mac_addr, MLACP(csm).remote_system.system_id, ETHER_ADDR_LEN);
        }
    }
    else
    {
        LIST_FOREACH(vlan, &(lif_po->vlan_list), port_next)
        {
            if (!vlan->vlan_itf)
                continue;

            /*If the po is under a vlan, update vlan mac*/
            if (local_if_is_l3_mode(vlan->vlan_itf))
            {
                if (memcmp(vlan->vlan_itf->l3_mac_addr, MLACP(csm).remote_system.system_id, ETHER_ADDR_LEN) != 0)
                {
                    ret =  iccp_netlink_if_hwaddr_set(vlan->vlan_itf->ifindex,  MLACP(csm).remote_system.system_id, ETHER_ADDR_LEN);
                    if (ret != 0)
                    {
                        ICCPD_LOG_ERR(__FUNCTION__, "Set %s mac error, ret = %d", vlan->vlan_itf->name, ret);
                    }

                    /* Refresh link local address according the new MAC */
                    iccp_netlink_if_shutdown_set(vlan->vlan_itf->ifindex);
                    iccp_netlink_if_startup_set(vlan->vlan_itf->ifindex);

                    iccp_set_interface_ipadd_mac(vlan->vlan_itf, macaddr);
                    memcpy(vlan->vlan_itf->l3_mac_addr, MLACP(csm).remote_system.system_id, ETHER_ADDR_LEN);
                }
            }
        }
    }

    return;
}

void recover_if_ipmac_on_standby(struct LocalInterface* lif_po)
{
    struct CSM* csm;
    uint8_t null_mac[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
    struct VLAN_ID *vlan = NULL;

    csm = lif_po->csm;
    char macaddr[64];
    int ret = 0;

    if (!csm)
        return;

    if (lif_po->type != IF_T_PORT_CHANNEL)
        return;

    if (csm->role_type != STP_ROLE_STANDBY)
    {
        return;
    }

    /*Recover mac to origin mac, it is the 'mac' value in 'localhost' currently*/
    if (memcmp( lif_po->mac_addr, MLACP(csm).system_id, ETHER_ADDR_LEN) != 0)
    {
        ICCPD_LOG_NOTICE(__FUNCTION__,
                        "%s Recover the system-id of %s from [%02X:%02X:%02X:%02X:%02X:%02X] to [%02X:%02X:%02X:%02X:%02X:%02X].",
                        (csm->role_type == STP_ROLE_STANDBY) ? "Standby" : "Active",
                        lif_po->name,  lif_po->mac_addr[0], lif_po->mac_addr[1], lif_po->mac_addr[2], lif_po->mac_addr[3], lif_po->mac_addr[4], lif_po->mac_addr[5],
                        MLACP(csm).system_id[0], MLACP(csm).system_id[1], MLACP(csm).system_id[2], MLACP(csm).system_id[3], MLACP(csm).system_id[4], MLACP(csm).system_id[5]);

        ret = iccp_netlink_if_hwaddr_set(lif_po->ifindex,  MLACP(csm).system_id, ETHER_ADDR_LEN);
        if (ret != 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "Set %s mac error, ret = %d", lif_po->name, ret);
        }

        /* Refresh link local address according the new MAC */
        iccp_netlink_if_shutdown_set(lif_po->ifindex);
        iccp_netlink_if_startup_set(lif_po->ifindex);
    }

    /*Set portchannel ip mac */
    memset(macaddr, 0, 64);
    SET_MAC_STR(macaddr, MLACP(csm).system_id);
    if (local_if_is_l3_mode(lif_po))
    {
        iccp_set_interface_ipadd_mac(lif_po, macaddr );
        memcpy(lif_po->l3_mac_addr, MLACP(csm).system_id, ETHER_ADDR_LEN);
    }
    else
    {
        LIST_FOREACH(vlan, &(lif_po->vlan_list), port_next)
        {
            if (!vlan->vlan_itf)
                continue;

            /*If the po is under a vlan, update vlan mac*/
            if (local_if_is_l3_mode(vlan->vlan_itf))
            {
                ret =  iccp_netlink_if_hwaddr_set(vlan->vlan_itf->ifindex, MLACP(csm).system_id, ETHER_ADDR_LEN);
                if (ret != 0)
                {
                    ICCPD_LOG_ERR(__FUNCTION__, "Set %s mac error, ret = %d", vlan->vlan_itf->name, ret);
                }

                /* Refresh link local address according the new MAC */
                iccp_netlink_if_shutdown_set(vlan->vlan_itf->ifindex);
                iccp_netlink_if_startup_set(vlan->vlan_itf->ifindex);

                iccp_set_interface_ipadd_mac(vlan->vlan_itf, macaddr);
                memcpy(vlan->vlan_itf->l3_mac_addr, MLACP(csm).system_id, ETHER_ADDR_LEN);
            }
        }
    }

    return;
}

int iccp_netlink_neighbor_request(int family, uint8_t *addr, int add, uint8_t *mac, char *portname)
{
    struct System *sys = NULL;
    struct rtnl_neigh *neigh = NULL;
    struct nl_addr *nl_addr_mac = NULL;
    struct nl_addr *nl_addr_dst = NULL;
    struct LocalInterface *lif = NULL;
    struct nl_cache *link_cache;
    char mac_str[18] = "";
    int err = 0;

    if (!(sys = system_get_instance()))
        return MCLAG_ERROR;

    lif = local_if_find_by_name(portname);
    if (!lif)
        return MCLAG_ERROR;

    neigh = rtnl_neigh_alloc();
    if (!neigh)
    {
        ICCPD_LOG_INFO(__FUNCTION__, "Unable to allocate neighbour object");
        return MCLAG_ERROR;
    }

    sprintf(mac_str, "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    ICCPD_LOG_NOTICE(__FUNCTION__, "Notify kernel %s %s entry(ip:%s, mac:%s, intf:%s)",
                   add ? "add" : "del", (family == AF_INET) ? "ARP" : "ND",
                   (family == AF_INET) ? show_ip_str(*((int *)addr)) : show_ipv6_str(addr), mac_str, portname);

    nl_addr_mac = nl_addr_build(AF_LLC, (void *)mac, ETHER_ADDR_LEN);
    if (!nl_addr_mac)
    {
        err = MCLAG_ERROR;
        goto errout;
    }

    if (family == AF_INET)
        nl_addr_dst = nl_addr_build(family, (void *)addr, 4);
    else
        nl_addr_dst = nl_addr_build(family, (void *)addr, 16);

    if (!nl_addr_dst)
    {
        err = MCLAG_ERROR;
        goto errout;
    }

    rtnl_neigh_set_lladdr(neigh, nl_addr_mac);
    rtnl_neigh_set_dst(neigh, nl_addr_dst);
    rtnl_neigh_set_ifindex(neigh, lif->ifindex);
    rtnl_neigh_set_state(neigh, NUD_REACHABLE);

    if (add)
    {
        if ((err = rtnl_neigh_add(sys->route_sock, neigh, NLM_F_REPLACE | NLM_F_CREATE)) < 0)
            ICCPD_LOG_WARN(__FUNCTION__, "Add %s (ip:%s, mac:%s) error, err = %d", (family == AF_INET) ? "ARP" : "ND",
                            (family == AF_INET) ? show_ip_str(*((int *)addr)) : show_ipv6_str(addr), mac_str, err);
    }
    else
    {
        if ((err = rtnl_neigh_delete(sys->route_sock, neigh, 0)) < 0)
            ICCPD_LOG_WARN(__FUNCTION__, "Del %s (ip:%s, mac:%s) error, err = %d", (family == AF_INET) ? "ARP" : "ND",
                            (family == AF_INET) ? show_ip_str(*((int *)addr)) : show_ipv6_str(addr), mac_str, err);
    }

errout:
    nl_addr_put(nl_addr_mac);
    nl_addr_put(nl_addr_dst);
    rtnl_neigh_put(neigh);
    return err;
}

void iccp_event_handler_obj_input_newlink(struct nl_object *obj, void *arg)
{
    struct rtnl_link *link;
    unsigned int *event = arg;
    uint32_t ifindex;
    char * ifname, *p;
    struct LocalInterface *lif = NULL;
    struct nl_addr *nl_addr;
    int addr_type = 0;
    int op_state = 0;
    int link_flag = 0;

    link = (struct rtnl_link *)obj;
    ifindex = rtnl_link_get_ifindex(link);
    op_state = rtnl_link_get_operstate(link);
    ifname = rtnl_link_get_name(link);
    nl_addr = rtnl_link_get_addr(link);
    link_flag = rtnl_link_get_flags(link);

    if (nl_addr)
        addr_type = nl_addr_guess_family(nl_addr);

    /*Vxlan tunnel dev name is like VTTNL0001-1000, VTTNL0001 is vxlan tunnel name, 1000 is vni*/
    /*If dev is vxlan tunnel, only create the tunnel with name no vni, like VTTNL0001*/
    if ((strncmp(ifname, VXLAN_TUNNEL_PREFIX, strlen(VXLAN_TUNNEL_PREFIX)) == 0))
    {
        /*Change ifname from VTTNL0001-1000 to VTTNL0001*/
        if ((p = strchr(ifname, '-')) != NULL)
        {
            *p = '\0';
        }
        /*Create vxlan tunnel dev, state is always UP*/
        lif = local_if_find_by_name(ifname);
        if (!lif)
        {
            lif = local_if_create(ifindex, ifname, IF_T_VXLAN);
            lif->state = PORT_STATE_UP;
        }
        return;
    }
    else
        lif = local_if_find_by_ifindex(ifindex);

    if (!lif)
    {
        const itf_type_t if_whitelist[] = {
            { PORTCHANNEL_PREFIX,      IF_T_PORT_CHANNEL },
            { VLAN_PREFIX,             IF_T_VLAN         },
            { FRONT_PANEL_PORT_PREFIX, IF_T_PORT         },
            { VXLAN_TUNNEL_PREFIX,     IF_T_VXLAN        },
            { NULL,                    0                 }
        };
        int i = 0;

        for (i = 0; if_whitelist[i].ifname != NULL; ++i)
        {
            if ((strncmp(ifname,
                         if_whitelist[i].ifname, strlen(if_whitelist[i].ifname)) == 0))
            {
                lif = local_if_create(ifindex, ifname, if_whitelist[i].type);

                lif->state = PORT_STATE_DOWN;

                if (IF_OPER_UP == op_state )
                {
                    lif->state = PORT_STATE_UP;
                }

                switch (addr_type)
                {
                    case AF_LLC:
                        memcpy( lif->mac_addr, nl_addr_get_binary_addr(nl_addr), ETHER_ADDR_LEN);
                    default:
                        break;
                }

                break;
            }
        }
    }
    else /*update*/
    {
        /*update*/
        if (lif->state == PORT_STATE_DOWN && op_state == IF_OPER_UP)
        {
            lif->state = PORT_STATE_UP;
            /*if(lif->type ==IF_T_PORT_CHANNEL)*/
            ICCPD_LOG_NOTICE(__FUNCTION__, "Update local port %s state up", ifname);

            iccp_from_netlink_port_state_handler(lif->name, lif->state);
        }
        else if (lif->state == PORT_STATE_UP && ( IF_OPER_UP != op_state || !(link_flag & IFF_LOWER_UP)))
        {
            lif->state = PORT_STATE_DOWN;
            /*if(lif->type ==IF_T_PORT_CHANNEL)*/
            ICCPD_LOG_NOTICE(__FUNCTION__, "Update local port %s state down", ifname);

            iccp_from_netlink_port_state_handler(lif->name, lif->state);
        }

        switch (addr_type)
        {
        case AF_LLC:
            if (memcmp(nl_addr_get_binary_addr(nl_addr), lif->mac_addr, ETHER_ADDR_LEN) != 0)
            {
                memcpy( lif->mac_addr, nl_addr_get_binary_addr(nl_addr), ETHER_ADDR_LEN);
                lif->port_config_sync = 1;
            }

        default:
            break;
        }
    }

    return;
}

void iccp_event_handler_obj_input_dellink(struct nl_object *obj, void *arg)
{
    struct rtnl_link *link;
    struct LocalInterface *lif;
    uint32_t ifindex;

    link = (struct rtnl_link *)obj;

    ifindex = rtnl_link_get_ifindex(link);
    if ((lif = local_if_find_by_ifindex(ifindex)) != NULL)
        local_if_destroy(lif->name);

    return;
}

void iccp_event_handler_obj_input_newaddr(struct nl_object *obj, void *arg)
{
    struct rtnl_addr *addr;
    struct nl_addr *nl_addr;
    struct LocalInterface *lif;
    uint32_t ifindex;
    char addrStr[65] = { 0 };
    char addr_null[16] = { 0 };
    addr = (struct rtnl_addr *)obj;

    ifindex = rtnl_addr_get_ifindex(addr);
    nl_addr = rtnl_addr_get_local(addr);

    if (!(lif = local_if_find_by_ifindex(ifindex)))
        return;

    if (rtnl_addr_get_family(addr) == AF_INET)
    {
        lif->ipv4_addr = *(uint32_t *) nl_addr_get_binary_addr(nl_addr);
        lif->prefixlen = nl_addr_get_prefixlen(nl_addr);
        lif->l3_mode = 1;
        lif->port_config_sync = 1;
        if (memcmp((char *)lif->ipv6_addr, addr_null, 16) == 0)
            update_if_ipmac_on_standby(lif);
        ICCPD_LOG_DEBUG(__FUNCTION__, "Ifname %s index %d address %s", lif->name, lif->ifindex, show_ip_str(lif->ipv4_addr));
    }
    else if (rtnl_addr_get_family(addr) == AF_INET6)
    {
        if (memcmp(show_ipv6_str((char *)nl_addr_get_binary_addr(nl_addr)), "FE80", 4) == 0
            || memcmp(show_ipv6_str((char *)nl_addr_get_binary_addr(nl_addr)), "fe80", 4) == 0)
            return;

        memcpy((char *)lif->ipv6_addr, nl_addr_get_binary_addr(nl_addr), 16);
        lif->prefixlen = nl_addr_get_prefixlen(nl_addr);
        lif->l3_mode = 1;
        lif->port_config_sync = 1;
        if (lif->ipv4_addr == 0)
            update_if_ipmac_on_standby(lif);
        ICCPD_LOG_DEBUG(__FUNCTION__, "Ifname %s index %d address %s", lif->name, lif->ifindex, show_ipv6_str((char *)lif->ipv6_addr));
    }

    return;
}

void iccp_event_handler_obj_input_deladdr(struct nl_object *obj, void *arg)
{
    struct rtnl_addr *addr;
    struct nl_addr *nl_addr;
    struct LocalInterface *lif;
    uint32_t ifindex;
    char addr_null[16] = { 0 };

    addr = (struct rtnl_addr *)obj;

    ifindex = rtnl_addr_get_ifindex(addr);
    nl_addr = rtnl_addr_get_local(addr);

    if (!(lif = local_if_find_by_ifindex(ifindex)))
        return;

    if (rtnl_addr_get_family(addr) == AF_INET)
    {
        lif->ipv4_addr = 0;
        lif->prefixlen = 0;
    }
    else if (rtnl_addr_get_family(addr) == AF_INET6)
    {
        if (memcmp(show_ipv6_str((char *)nl_addr_get_binary_addr(nl_addr)), "FE80", 4) == 0
            || memcmp(show_ipv6_str((char *)nl_addr_get_binary_addr(nl_addr)), "fe80", 4) == 0)
            return;

        memset((char *)lif->ipv6_addr, 0, 16);
        lif->prefixlen_v6 = 0;
    }

    if (lif->ipv4_addr == 0 && memcmp((char *)lif->ipv6_addr, addr_null, 16) == 0)
    {
        lif->l3_mode = 0;
        memset(lif->l3_mac_addr, 0, ETHER_ADDR_LEN);
    }

    return;
}

int iccp_addr_valid_handler(struct nl_msg *msg, void *arg)
{
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    unsigned int event = 0;
    if (nlh->nlmsg_type != RTM_NEWADDR)
        return 0;

    if (nl_msg_parse(msg, &iccp_event_handler_obj_input_newaddr, &event) < 0)
        ICCPD_LOG_ERR(__FUNCTION__, "Unknown message type.");

    return 0;
}

int iccp_check_if_addr_from_netlink(int family, uint8_t *addr, struct LocalInterface *lif)
{
    struct
    {
        struct nlmsghdr nlh;
        struct ifaddrmsg ifa;
    } req;

    struct sockaddr_nl nladdr;
    struct iovec iov;
    struct msghdr msg = {
        .msg_name       = &nladdr,
        .msg_namelen    = sizeof(nladdr),
        .msg_iov        = &iov,
        .msg_iovlen     = 1,
    };

    int fd;
    struct System *sys;
    if ((sys = system_get_instance()) == NULL)
    {
        return 0;
    }

    memset(&req, 0, sizeof(req));
    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifaddrmsg));
    req.nlh.nlmsg_type = RTM_GETADDR;
    req.nlh.nlmsg_flags =  NLM_F_ROOT | NLM_F_MATCH | NLM_F_REQUEST;
    req.nlh.nlmsg_pid = 0;
    req.nlh.nlmsg_seq = 0;
    req.ifa.ifa_family = family;

    fd = nl_socket_get_fd(sys->route_sock);
    send(fd, (void*)&req, sizeof(req), 0);

    char * buf = malloc(10000);
    iov.iov_base = buf;

    while (1)
    {
        int status;
        int msglen = 0;
        iov.iov_len = 10000;
        status = recvmsg(fd, &msg, 0);

        if (status < 0 || status == 0)
        {
            ICCPD_LOG_WARN(__FUNCTION__, "netlink receive error  (%d) status %d %d ", fd, status, errno);
            free(buf);
            return 0;
        }
        struct nlmsghdr *n = (struct nlmsghdr*)buf;
        msglen = status;

        while (NLMSG_OK(n, msglen))
        {
            if (n->nlmsg_type != RTM_NEWADDR)
            {
                free(buf);
                return 0;
            }
            struct ifaddrmsg *ifa;
            ifa = NLMSG_DATA(n);
            if (lif && lif->ifindex == ifa->ifa_index)
            {
                struct rtattr *rth = IFA_RTA(ifa);
                int rtl = IFA_PAYLOAD(n);

                while (rtl && RTA_OK(rth, rtl))
                {
                    if (rth->rta_type == IFA_ADDRESS || rth->rta_type == IFA_LOCAL)
                    {
                        if (family == AF_INET && ifa->ifa_family == AF_INET)
                        {
                            if (*(uint32_t *)addr == ntohl(*((uint32_t *)RTA_DATA(rth))))
                            {
                                free(buf);
                                return 1;
                            }
                        }

                        if (family == AF_INET6 && ifa->ifa_family == AF_INET6)
                        {
                            void *addr_netlink;
                            addr_netlink = RTA_DATA(rth);
                            if (!memcmp((uint8_t *)addr_netlink, addr, 16))
                            {
                                free(buf);
                                return 1;
                            }
                        }
                    }
                    rth = RTA_NEXT(rth, rtl);
                }
            }
            n = NLMSG_NEXT(n, msglen);
        }
    }

    free(buf);

    return 0;
}

int iccp_sys_local_if_list_get_addr()
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
        ret = nl_send_simple(sys->route_sock, RTM_GETADDR, NLM_F_DUMP,
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

        nl_cb_set(cb, NL_CB_VALID, NL_CB_CUSTOM, iccp_addr_valid_handler, sys);
        ret = nl_recvmsgs(sys->route_sock, cb);
        nl_cb_put(cb);
        if (ret < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "Receive netlink msg error, ret = %d  errno = %d .", ret, errno);
            if (ret != -NLE_DUMP_INTR)
                return ret;
            retry = 1;
        }
    }

    return ret;
}

static int iccp_route_event_handler(struct nl_msg *msg, void *arg)
{
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    unsigned int event = 1;

    switch (nlh->nlmsg_type)
    {
        case RTM_NEWLINK:
            if (nl_msg_parse(msg, &iccp_event_handler_obj_input_newlink, &event) < 0)
                ICCPD_LOG_DEBUG(__FUNCTION__, "Unknown message type(RTM_NEWLINK)");
            iccp_parse_if_vlan_info_from_netlink(nlh);
            break;

        case RTM_DELLINK:
            if (nl_msg_parse(msg, &iccp_event_handler_obj_input_dellink, NULL) < 0)
                ICCPD_LOG_DEBUG(__FUNCTION__, "Unknown message type(RTM_DELLINK)");
            break;

        case RTM_NEWNEIGH:
        case RTM_DELNEIGH:
            do_one_neigh_request(nlh);
            break;

        case RTM_NEWADDR:
            if (nl_msg_parse(msg, &iccp_event_handler_obj_input_newaddr, NULL) < 0)
                ICCPD_LOG_DEBUG(__FUNCTION__, "Unknown message type(RTM_NEWADDR).");
            break;
        case RTM_DELADDR:
            if (nl_msg_parse(msg, &iccp_event_handler_obj_input_deladdr, NULL) < 0)
                ICCPD_LOG_DEBUG(__FUNCTION__, "Unknown message type(RTM_DELADDR).");
            break;
        default:
            return NL_OK;
    }

    return NL_STOP;
}

/**
 * SECTION: Context functions
 */
static int iccp_genric_event_handler(struct nl_msg *msg, void *arg)
{
    struct genlmsghdr *gnlh = nlmsg_data(nlmsg_hdr(msg));

    switch (gnlh->cmd)
    {
        case TEAM_CMD_PORT_LIST_GET:
            return iccp_get_portchannel_member_list_handler(msg, NULL);
    }

    return NL_SKIP;
}

int iccp_make_nd_socket(void)
{
    int sock;
    int ret;
    int val;
    struct icmp6_filter filter;

    sock = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6);

    if (sock < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to create nd socket");
        return MCLAG_ERROR;
    }

    val = 1;
#ifdef IPV6_RECVPKTINFO /* 2292bis-01 */
    if (setsockopt(sock, IPPROTO_IPV6, IPV6_RECVPKTINFO, &val, sizeof(val)) < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to set IPV6_RECVPKTINFO for nd socket");
        close(sock);
        return MCLAG_ERROR;
    }
#else /* RFC2292 */
    if (setsockopt(sock, IPPROTO_IPV6, IPV6_PKTINFO, &val, sizeof(val)) < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to set IPV6_PKTINFO for nd socket");
        close(sock);
        return MCLAG_ERROR;
    }
#endif

    ICMP6_FILTER_SETBLOCKALL(&filter);
    ICMP6_FILTER_SETPASS(ND_NEIGHBOR_ADVERT, &filter);

    ret = setsockopt(sock, IPPROTO_ICMPV6, ICMP6_FILTER, &filter, sizeof(struct icmp6_filter));

    if (ret < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to set ICMP6_FILTER");
        close(sock);
        return MCLAG_ERROR;
    }

    return sock;
}

/*init netlink socket*/
int iccp_system_init_netlink_socket()
{
    struct System* sys = NULL;
    int val = 0;
    int err = 0;

    if ((sys = system_get_instance()) == NULL )
        return MCLAG_ERROR;

    sys->genric_sock = nl_socket_alloc();
    if (!sys->genric_sock)
        goto err_genric_sock_alloc;

    sys->genric_sock_seq = time(NULL);
    err = genl_connect(sys->genric_sock);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to connect to netlink sock sys->genric_sock.");
        goto err_genric_sock_connect;
    }

    sys->genric_event_sock = nl_socket_alloc();
    if (!sys->genric_event_sock)
        goto err_genric_event_sock_alloc;

    err = genl_connect(sys->genric_event_sock);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to connect to netlink sys->genric_event_sock.");
        goto err_genric_event_sock_connect;
    }

    sys->route_sock = nl_socket_alloc();
    if (!sys->route_sock)
        goto err_route_sock_alloc;
    err = nl_connect(sys->route_sock, NETLINK_ROUTE);
    if (err)
        goto err_route_sock_connect;

    err = nl_socket_set_buffer_size(sys->route_sock, 98304, 0);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to set buffer size of netlink route event sock.");
        goto err_route_sock_connect;
    }

    sys->route_event_sock = nl_socket_alloc();
    if (!sys->route_event_sock)
        goto err_route_event_sock_alloc;

    err = nl_connect(sys->route_event_sock, NETLINK_ROUTE);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to connect to netlink sys->route_event_sock. ");
        goto err_route_event_sock_connect;
    }

    err = nl_socket_set_buffer_size(sys->route_event_sock, 983040, 0);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to set buffer size of netlink route event sock.");
        goto err_route_event_sock_connect;
    }

    val = NETLINK_BROADCAST_SEND_ERROR;
    err = setsockopt(nl_socket_get_fd(sys->genric_event_sock), SOL_NETLINK,
                     NETLINK_BROADCAST_ERROR, &val, sizeof(val));
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed set NETLINK_BROADCAST_ERROR on netlink event sock.");
        goto err_return;
    }

    err = nl_socket_set_buffer_size(sys->genric_sock, 98304, 0);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to set buffer size of netlink sock.");
        goto err_return;
    }

    err = nl_socket_set_buffer_size(sys->genric_event_sock, 98304, 0);
    if (err)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to set buffer size of netlink event sock.");
        goto err_return;
    }

    nl_socket_disable_seq_check(sys->genric_event_sock);
    nl_socket_modify_cb(sys->genric_event_sock, NL_CB_VALID, NL_CB_CUSTOM,
                        iccp_genric_event_handler, sys);

    nl_socket_disable_seq_check(sys->route_event_sock);
    nl_socket_modify_cb(sys->route_event_sock, NL_CB_VALID, NL_CB_CUSTOM,
                        iccp_route_event_handler, sys);

    err = nl_socket_add_membership(sys->route_event_sock, RTNLGRP_NEIGH);
    if (err < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__,  "Failed to add netlink membership.");
        goto err_return;
    }

    err = nl_socket_add_membership(sys->route_event_sock, RTNLGRP_LINK);
    if (err < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__,  "Failed to add netlink membership.");
        goto err_return;
    }

    err = nl_socket_add_membership(sys->route_event_sock, RTNLGRP_IPV4_IFADDR);
    if (err < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__,  "Failed to add netlink membership.");
        goto err_return;
    }
    err = nl_socket_add_membership(sys->route_event_sock, RTNLGRP_IPV6_IFADDR);
    if (err < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "Failed to add netlink membership.");
        goto err_return;
    }
    /* receive arp packet socket */
    sys->arp_receive_fd = socket(PF_PACKET, SOCK_DGRAM, 0);
    if (sys->arp_receive_fd  < 0)
    {
        ICCPD_LOG_ERR(__FUNCTION__, "socket error ");
        goto err_return;
    }

    if (1)
    {
        struct sockaddr_ll sll;
        memset(&sll, 0, sizeof(sll));
        sll.sll_family = AF_PACKET;
        sll.sll_protocol = htons(ETH_P_ARP);
        sll.sll_ifindex = 0;
        if (bind(sys->arp_receive_fd, (struct sockaddr*)&sll, sizeof(sll)) < 0)
        {
            ICCPD_LOG_ERR(__FUNCTION__, "socket bind error");
            goto err_return;
        }
    }

    sys->ndisc_receive_fd = iccp_make_nd_socket();

    if (sys->ndisc_receive_fd < 0)
    {
        goto err_return;
    }

    goto succes_return;

 err_return:

 err_route_event_sock_connect:
    nl_socket_free(sys->route_event_sock);

 err_route_sock_alloc:
 err_route_sock_connect:
    nl_socket_free(sys->route_sock);

 err_route_event_sock_alloc:
 err_genric_event_sock_connect:
    nl_socket_free(sys->genric_event_sock);

 err_genric_event_sock_alloc:
 err_genric_sock_connect:
    nl_socket_free(sys->genric_sock);

    return err;

 err_genric_sock_alloc:

 succes_return:
    return 0;
}

void iccp_system_dinit_netlink_socket()
{
    struct System* sys = NULL;

    if ((sys = system_get_instance()) == NULL )
        return;

    nl_socket_free(sys->route_event_sock);
    nl_socket_free(sys->route_sock);
    nl_socket_free(sys->genric_event_sock);
    nl_socket_free(sys->genric_sock);
    return;
}

static int iccp_get_netlink_genic_sock_event_fd(struct System *sys)
{
    return nl_socket_get_fd(sys->genric_event_sock);
}

static int iccp_netlink_genic_sock_event_handler(struct System *sys)
{
    int ret = 0;

    ret = nl_recvmsgs_default(sys->genric_event_sock);
    if (ret)
    {
        sys->need_sync_team_again = 1;
        ICCPD_LOG_DEBUG(__FUNCTION__, "genric_event_sock %d recvmsg error ret = %d ", nl_socket_get_fd(sys->genric_event_sock), ret);
    }

    return ret;
}

static int iccp_get_netlink_route_sock_event_fd(struct System *sys)
{
    return nl_socket_get_fd(sys->route_event_sock);
}

static int iccp_get_receive_arp_packet_sock_fd(struct System *sys)
{
    return sys->arp_receive_fd;
}

static int iccp_get_receive_ndisc_packet_sock_fd(struct System *sys)
{
    return sys->ndisc_receive_fd;
}

static int iccp_receive_arp_packet_handler(struct System *sys)
{
    unsigned char buf[1024];
    struct sockaddr_ll sll;
    socklen_t sll_len = sizeof(sll);
    struct arphdr *a = (struct arphdr*)buf;
    int n;
    unsigned int ifindex;
    unsigned int addr;
    uint8_t mac_addr[ETHER_ADDR_LEN];

    n = recvfrom(sys->arp_receive_fd, buf, sizeof(buf), MSG_DONTWAIT,
                 (struct sockaddr*)&sll, &sll_len);
    if (n < 0)
    {
        ICCPD_LOG_WARN(__FUNCTION__, "ARP recvfrom error: %s", buf);
        return MCLAG_ERROR;
    }

    /* Sanity checks */
    /*Only process ARPOP_REPLY*/
    if (n < sizeof(*a) ||
        a->ar_op != htons(ARPOP_REPLY) ||
        a->ar_pln != 4 ||
        a->ar_pro != htons(ETH_P_IP) ||
        a->ar_hln != sll.sll_halen ||
        sizeof(*a) + 2 * 4 + 2 * a->ar_hln > n)
        return 0;

    ifindex = sll.sll_ifindex;
    memcpy(mac_addr,  (char*)(a + 1), ETHER_ADDR_LEN);
    memcpy(&addr, (char*)(a + 1) + a->ar_hln, 4);

    do_arp_update_from_reply_packet(ifindex, addr, mac_addr);

    return 0;
}

int iccp_receive_ndisc_packet_handler(struct System *sys)
{
    uint8_t buf[4096];
    uint8_t adata[1024];
    struct sockaddr_in6 from;
    unsigned int ifindex = 0;
    struct msghdr msg;
    struct iovec iov;
    struct cmsghdr *cmsgptr;
    struct nd_msg *ndmsg = NULL;
    struct nd_opt_hdr *nd_opt = NULL;
    struct in6_addr target;
    uint8_t mac_addr[ETHER_ADDR_LEN];
    int8_t *opt = NULL;
    int opt_len = 0, l = 0;
    int len;

    memset(mac_addr, 0, ETHER_ADDR_LEN);

    /* Fill in message and iovec. */
    msg.msg_name = (void *)(&from);
    msg.msg_namelen = sizeof(struct sockaddr_in6);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = (void *)adata;
    msg.msg_controllen = sizeof adata;
    iov.iov_base = buf;
    iov.iov_len = 4096;

    len = recvmsg(sys->ndisc_receive_fd, &msg, 0);

    if (len < 0)
    {
        ICCPD_LOG_WARN(__FUNCTION__, "Ndisc recvmsg error!");
        return MCLAG_ERROR;
    }

    if (msg.msg_controllen >= sizeof(struct cmsghdr))
        for (cmsgptr = CMSG_FIRSTHDR(&msg); cmsgptr != NULL; cmsgptr = CMSG_NXTHDR(&msg, cmsgptr))
        {
            /* I want interface index which this packet comes from. */
            if (cmsgptr->cmsg_level == IPPROTO_IPV6 && cmsgptr->cmsg_type == IPV6_PKTINFO)
            {
                struct in6_pktinfo *ptr;

                ptr = (struct in6_pktinfo *)CMSG_DATA(cmsgptr);
                ifindex = ptr->ipi6_ifindex;
            }
        }

    ndmsg = (struct nd_msg *)buf;

    if (ndmsg->icmph.icmp6_type != NDISC_NEIGHBOUR_ADVERTISEMENT)
        return 0;

    memcpy((char *)(&target), (char *)(&ndmsg->target), sizeof(struct in6_addr));

    opt = (char *)ndmsg->opt;

    opt_len = len - sizeof(struct nd_msg);

    if (opt && opt_len > 0)
    {
        while (opt_len)
        {
            if (opt_len < sizeof(struct nd_opt_hdr))
                return 0;

            nd_opt = (struct nd_opt_hdr *)opt;

            l = nd_opt->nd_opt_len << 3;

            if (l == 0)
                return 0;

            if (nd_opt->nd_opt_type == ND_OPT_TARGET_LL_ADDR)
            {
                memcpy(mac_addr, (char *)((char *)nd_opt + sizeof(struct nd_opt_hdr)), ETHER_ADDR_LEN);
                break;
            }

            opt += l;
            opt_len -= l;
        }
    }

    /* ICCPD_LOG_DEBUG(__FUNCTION__, "Recv na pkt(%s,%02X:%02X:%02X:%02X:%02X:%02X)!", show_ipv6_str((char *)&target), mac_addr[0], mac_addr[1],
       mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]); */
    do_ndisc_update_from_reply_packet(ifindex, (char *)&target, mac_addr);

    return 0;
}

void iccp_netlink_sync_again()
{
    struct System* sys = NULL;
    struct LocalInterface* lif = NULL;

    if ((sys = system_get_instance()) == NULL )
        return;

    if (sys->need_sync_netlink_again)
    {
        sys->need_sync_netlink_again = 0;

        /*Get kernel interface and port */
        iccp_sys_local_if_list_get_init();
    }

    if (sys->need_sync_team_again)
    {
        sys->need_sync_team_again = 0;

        LIST_FOREACH(lif, &(sys->lif_list), system_next)
        {
            if (lif->type == IF_T_PORT_CHANNEL)
            {
                iccp_get_port_member_list(lif);
            }
        }
    }

    return;
}

static int iccp_netlink_route_sock_event_handler(struct System *sys)
{
    int ret = 0;

    ret = nl_recvmsgs_default(sys->route_event_sock);

    if (ret)
    {
        sys->need_sync_netlink_again = 1;
        ICCPD_LOG_DEBUG(__FUNCTION__, "fd %d recvmsg error ret = %d  errno = %d ", nl_socket_get_fd(sys->route_event_sock), ret, errno);
    }
    /*get netlink info again when error happens */
    if (ret == 0 && sys->need_sync_netlink_again == 1)
    {
        iccp_netlink_sync_again();
    }

    return ret;
}

extern int iccp_get_receive_fdb_sock_fd(struct System *sys);
extern int iccp_receive_fdb_handler_from_syncd(struct System *sys);

/* cond HIDDEN_SYMBOLS */
struct iccp_eventfd
{
    int (*get_fd)(struct System* sys);
    int (*event_handler)(struct System* sys);
};
/* endcond */

static const struct iccp_eventfd iccp_eventfds[] = {
    {
        .get_fd = iccp_get_server_sock_fd,
        .event_handler = scheduler_server_accept,
    },
    {
        .get_fd = iccp_get_netlink_genic_sock_event_fd,
        .event_handler = iccp_netlink_genic_sock_event_handler,
    },
    {
        .get_fd = iccp_get_netlink_route_sock_event_fd,
        .event_handler = iccp_netlink_route_sock_event_handler,
    },
    {
        .get_fd = iccp_get_receive_arp_packet_sock_fd,
        .event_handler = iccp_receive_arp_packet_handler,
    },
    {
        .get_fd = iccp_get_receive_ndisc_packet_sock_fd,
        .event_handler = iccp_receive_ndisc_packet_handler,
     }
};

/* \cond HIDDEN_SYMBOLS */
#define ICCP_EVENT_FDS_COUNT ARRAY_SIZE(iccp_eventfds)
/* \endcond */
/*
   @return fd.
 *
 **/

int iccp_get_eventfd_fd(struct System *sys)
{
    return sys->epoll_fd;
}

int iccp_init_netlink_event_fd(struct System *sys)
{
    int efd;
    int i;
    struct epoll_event event;
    int err;

    efd = epoll_create1(0);
    if (efd == -1)
        return -errno;

    for (i = 0; i < ICCP_EVENT_FDS_COUNT; i++)
    {
        int fd = iccp_eventfds[i].get_fd(sys);

        event.data.fd = fd;
        event.events = EPOLLIN;
        err = epoll_ctl(efd, EPOLL_CTL_ADD, fd, &event);
        if (err == -1)
        {
            err = -errno;
            goto close_efd;
        }
    }

    sys->epoll_fd = efd;

    return 0;

 close_efd:
    close(efd);

    return err;
}

/**
 *
 * @details Handler events which happened on event filedescriptor.
 *
 * @return Zero on success or negative number in case of an error.
 **/

int iccp_handle_events(struct System * sys)
{
    struct epoll_event events[ICCP_EVENT_FDS_COUNT + sys->readfd_count];
    struct CSM* csm = NULL;
    int nfds;
    int n;
    int i;
    int err;
    int max_nfds;

    max_nfds = ICCP_EVENT_FDS_COUNT + sys->readfd_count;

    nfds = epoll_wait(sys->epoll_fd, events, max_nfds, EPOLL_TIMEOUT_MSEC);

    /* Go over list of event fds and handle them sequentially */
    for (i = 0; i < nfds; i++)
    {
        for (n = 0; n < ICCP_EVENT_FDS_COUNT; n++)
        {
            const struct iccp_eventfd *eventfd = &iccp_eventfds[n];
            if (events[i].data.fd == eventfd->get_fd(sys))
            {
                err = eventfd->event_handler(sys);
                if (err)
                    ICCPD_LOG_INFO(__FUNCTION__, "Scheduler fd %d handler error %d !", events[i].data.fd, err );
                break;
            }
        }

        if (n < ICCP_EVENT_FDS_COUNT)
            continue;

        if (events[i].data.fd == sys->sync_ctrl_fd)
        {
            int client_fd = mclagd_ctl_sock_accept(sys->sync_ctrl_fd);
            if (client_fd > 0)
            {
                mclagd_ctl_interactive_process(client_fd);
                close(client_fd);
            }
            continue;
        }

        if (events[i].data.fd == sys->sync_fd)
        {
            iccp_receive_fdb_handler_from_syncd(sys);

            continue;
        }

        if (events[i].data.fd == sys->sig_pipe_r)
        {
            iccp_receive_signal_handler(sys);

            continue;
        }

        if (FD_ISSET(events[i].data.fd, &sys->readfd))
        {
            LIST_FOREACH(csm, &(sys->csm_list), next)
            {
                if (csm->sock_fd == events[i].data.fd )
                {
                    scheduler_csm_read_callback(csm);
                    break;
                }
            }
        }
    }

    return 0;
}

