/********************************************************************************
 * mlacp_sync_update.c
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
 *
 *******************************************************************************/
#include <stdio.h>
#include <stdlib.h>

#include <sys/queue.h>
#include <netinet/ip.h>

#include "../include/system.h"
#include "../include/logger.h"
#include "../include/mlacp_tlv.h"
#include "../include/iccp_csm.h"
#include "../include/mlacp_link_handler.h"
#include "../include/iccp_consistency_check.h"
#include "../include/port.h"
#include "../include/iccp_netlink.h"
/*****************************************
* Port-Conf Update
*
* ***************************************/
extern void update_if_ipmac_on_standby(struct LocalInterface* lif_po);
int mlacp_fsm_update_system_conf(struct CSM* csm, mLACPSysConfigTLV*sysconf)
{
    struct LocalInterface* lif = NULL;

    /*NOTE
       a little tricky, we change the NodeID local side if collision happened first time*/
    if (sysconf->node_id == MLACP(csm).node_id)
        MLACP(csm).node_id++;

    memcpy(MLACP(csm).remote_system.system_id, sysconf->sys_id, ETHER_ADDR_LEN);
    MLACP(csm).remote_system.system_priority = ntohs(sysconf->sys_priority);
    MLACP(csm).remote_system.node_id = sysconf->node_id;

    ICCPD_LOG_DEBUG(__FUNCTION__, "SystemID [%02X:%02X:%02X:%02X:%02X:%02X], SystemPriority [%d], Remote NodeID [%d], NodeID [%d]",
                    MLACP(csm).remote_system.system_id[0], MLACP(csm).remote_system.system_id[1], MLACP(csm).remote_system.system_id[2],
                    MLACP(csm).remote_system.system_id[3], MLACP(csm).remote_system.system_id[4], MLACP(csm).remote_system.system_id[5],
                    MLACP(csm).remote_system.system_priority,
                    MLACP(csm).remote_system.node_id,
                    MLACP(csm).node_id);

    LIST_FOREACH(lif, &(MLACP(csm).lif_list), mlacp_next)
    {
        update_if_ipmac_on_standby(lif);
    }

    return 0;
}

/*****************************************
* Port-Conf Update
*
* ***************************************/
int mlacp_fsm_update_Agg_conf(struct CSM* csm, mLACPAggConfigTLV* portconf)
{
    struct PeerInterface* pif = NULL;
    uint8_t po_active;
    uint8_t new_create = 0;

    ICCPD_LOG_DEBUG(__FUNCTION__, "Port name  %s, po id %d  flag %d MAC[%02x:%02x:%02x:%02x:%02x:%02x] ",
                    portconf->agg_name, ntohs(portconf->agg_id), portconf->flags, portconf->mac_addr[0], portconf->mac_addr[1], portconf->mac_addr[2],
                    portconf->mac_addr[3], portconf->mac_addr[4], portconf->mac_addr[5] );

    /* Looking for the peer port instance, is any peer if exist?*/
    pif = peer_if_find_by_name(csm, portconf->agg_name);

    /* Process purge*/
    if (portconf->flags & 0x02)
    {
        /*Purge*/
        if (pif != NULL )
            peer_if_destroy(pif);
        else
            MLACP(csm).need_to_sync = 1;
        /*ICCPD_LOG_INFO("mlacp_fsm",
            "    Peer port %s is removed from port-channel member.",portconf->port_name);*/

        return 0;
    }

    if (pif == NULL && portconf->flags & 0x01)
    {
        pif = peer_if_create(csm, ntohs(portconf->agg_id), IF_T_PORT_CHANNEL);
        if (pif == NULL)
            return MCLAG_ERROR;

        new_create = 1;
    }

    pif->po_id = ntohs(portconf->agg_id);
    memcpy(pif->name, portconf->agg_name, portconf->agg_name_len);
    memcpy(pif->mac_addr, portconf->mac_addr, ETHER_ADDR_LEN);

    po_active = (pif->state == PORT_STATE_UP);
    update_stp_peer_link(csm, pif, po_active, new_create);
    update_peerlink_isolate_from_pif(csm, pif, po_active, new_create);
    pif->po_active = po_active;

    return 0;
}

/*****************************************
* Agg Port-State Update
*
* ***************************************/
int mlacp_fsm_update_Aggport_state(struct CSM* csm, mLACPAggPortStateTLV* tlv)
{
    struct PeerInterface* peer_if = NULL;
    uint8_t po_active;

    if (csm == NULL || tlv == NULL)
        return MCLAG_ERROR;
    ICCPD_LOG_DEBUG(__FUNCTION__, "Portchannel id %d state %d", ntohs(tlv->agg_id), tlv->agg_state);

    po_active = (tlv->agg_state == PORT_STATE_UP);

    LIST_FOREACH(peer_if, &(MLACP(csm).pif_list), mlacp_next)
    {
        if (peer_if->type != IF_T_PORT_CHANNEL)
            continue;

        if (peer_if->po_id != ntohs(tlv->agg_id))
            continue;

        peer_if->state = tlv->agg_state;

        update_stp_peer_link(csm, peer_if, po_active, 0);
        update_peerlink_isolate_from_pif(csm, peer_if, po_active, 0);

        peer_if->po_active = po_active;
        ICCPD_LOG_DEBUG(__FUNCTION__, "Update peer interface %s to state %s", peer_if->name, tlv->agg_state ? "down" : "up");

        break;
    }

    return 0;
}

/*****************************************
* Recv from peer, MAC-Info Update
* ***************************************/
int mlacp_fsm_update_mac_entry_from_peer( struct CSM* csm, struct mLACPMACData *MacData)
{

    struct Msg* msg = NULL;
    struct MACMsg *mac_msg = NULL, mac_data;
    struct LocalInterface* local_if = NULL;
    uint8_t from_mclag_intf = 0;/*0: orphan port, 1: MCLAG port*/

    ICCPD_LOG_NOTICE(__FUNCTION__,
                   "Received MAC Info, port[%s] vid[%d] MAC[%s] type[%s]",
                   MacData->ifname, ntohs(MacData->vid), MacData->mac_str, MacData->type == MAC_SYNC_ADD ? "add" : "del");

    /*Find the interface in MCLAG interface list*/
    LIST_FOREACH(local_if, &(MLACP(csm).lif_list), mlacp_next)
    {
        if (local_if->type == IF_T_PORT_CHANNEL && strcmp(local_if->name, MacData->ifname) == 0)
        {
            from_mclag_intf = 1;
            break;
        }
    }

    /* update MAC list*/
    TAILQ_FOREACH(msg, &(MLACP(csm).mac_list), tail)
    {
        mac_msg = (struct MACMsg*)msg->buf;

        /*Same MAC is exist in local switch, this may be mac move*/
        if (strcmp(mac_msg->mac_str, MacData->mac_str) == 0 && mac_msg->vid == ntohs(MacData->vid))
        {
            if (MacData->type == MAC_SYNC_ADD)
            {
                mac_msg->age_flag &= ~MAC_AGE_PEER;
                ICCPD_LOG_DEBUG(__FUNCTION__, "Recv ADD, Remove peer age flag:%d ifname %s, MAC %s vlan-id %d",
                                mac_msg->age_flag, mac_msg->ifname, mac_msg->mac_str, mac_msg->vid);

                /*mac_msg->fdb_type = tlv->fdb_type;*/
                /*The port ifname is different to the local item*/
                if (from_mclag_intf == 0 || strcmp(mac_msg->ifname, MacData->ifname) != 0 || strcmp(mac_msg->origin_ifname, MacData->ifname) != 0)
                {
                    if (mac_msg->fdb_type != MAC_TYPE_STATIC)
                    {
                        /*Update local item*/
                        memcpy(&mac_msg->origin_ifname, MacData->ifname, MAX_L_PORT_NAME);
                    }

                    /*If the MAC is learned from orphan port, or from MCLAG port but the local port is down*/
                    if (from_mclag_intf == 0 || (local_if->state == PORT_STATE_DOWN && strcmp(mac_msg->ifname, csm->peer_itf_name) != 0))
                    {
                        /*Set MAC_AGE_LOCAL flag*/
                        mac_msg->age_flag = set_mac_local_age_flag(csm, mac_msg, 1);

                        if (strlen(csm->peer_itf_name) != 0)
                        {
                            if (strcmp(mac_msg->ifname, csm->peer_itf_name) == 0)
                            {
                                /* This MAC is already point to peer-link */
                                return 0;
                            }

                            if (csm->peer_link_if && csm->peer_link_if->state == PORT_STATE_UP)
                            {
                                /*Redirect the mac to peer-link*/
                                memcpy(&mac_msg->ifname, csm->peer_itf_name, IFNAMSIZ);

                                /*Send mac add message to mclagsyncd*/
                                add_mac_to_chip(mac_msg, MAC_TYPE_DYNAMIC);
                            }
                            else
                            {
                                /*must redirect but peerlink is down, del mac from ASIC*/
                                /*if peerlink change to up, mac will add back to ASIC*/
                                del_mac_from_chip(mac_msg);

                                /*Redirect the mac to peer-link*/
                                memcpy(&mac_msg->ifname, csm->peer_itf_name, IFNAMSIZ);
                            }
                        }
                        else
                        {
                            /*must redirect but no peerlink, del mac from ASIC*/
                            del_mac_from_chip(mac_msg);

                            /*Update local item*/
                            memcpy(&mac_msg->ifname, MacData->ifname, MAX_L_PORT_NAME);

                            /*if orphan port mac but no peerlink, don't keep this mac*/
                            if (from_mclag_intf == 0)
                            {
                                TAILQ_REMOVE(&(MLACP(csm).mac_list), msg, tail);
                                free(msg->buf);
                                free(msg);
                                return 0;
                            }
                        }
                    }
                    else
                    {
                        /*Remove MAC_AGE_LOCAL flag*/
                        mac_msg->age_flag = set_mac_local_age_flag(csm, mac_msg, 0);

                        /*Update local item*/
                        memcpy(&mac_msg->ifname, MacData->ifname, MAX_L_PORT_NAME);

                        /*from MCLAG port and the local port is up, add mac to ASIC to update port*/
                        add_mac_to_chip(mac_msg, MAC_TYPE_DYNAMIC);
                    }
                }
            }

            break;
        }
    }

    /* delete/add MAC list*/
    if (msg && MacData->type == MAC_SYNC_DEL)
    {
        mac_msg->age_flag |= MAC_AGE_PEER;
        ICCPD_LOG_DEBUG(__FUNCTION__, "Recv DEL, Add peer age flag: %d ifname %s, MAC %s vlan-id %d",
                        mac_msg->age_flag, mac_msg->ifname, mac_msg->mac_str, mac_msg->vid);

        if (mac_msg->age_flag == (MAC_AGE_LOCAL | MAC_AGE_PEER))
        {
            /*send mac del message to mclagsyncd.*/
            del_mac_from_chip(mac_msg);

            /*If local and peer both aged, del the mac*/
            TAILQ_REMOVE(&(MLACP(csm).mac_list), msg, tail);
            free(msg->buf);
            free(msg);
        }
        else
        {
            return 0;
        }
    }
    else if (!msg && MacData->type == MAC_SYNC_ADD)
    {
        mac_msg = (struct MACMsg*)&mac_data;
        mac_msg->fdb_type = MAC_TYPE_DYNAMIC;
        mac_msg->vid = ntohs(MacData->vid);
        sprintf(mac_msg->mac_str, "%s", MacData->mac_str);
        sprintf(mac_msg->ifname, "%s", MacData->ifname);
        sprintf(mac_msg->origin_ifname, "%s", MacData->ifname);
        mac_msg->age_flag = 0;

        /*If the MAC is learned from orphan port, or from MCLAG port but the local port is down*/
        if (from_mclag_intf == 0 || local_if->state == PORT_STATE_DOWN)
        {
            /*Set MAC_AGE_LOCAL flag*/
            mac_msg->age_flag = set_mac_local_age_flag(csm, mac_msg, 1);

            if (strlen(csm->peer_itf_name) == 0)
            {
                ICCPD_LOG_NOTICE(__FUNCTION__, "From orphan port or portchannel is down, but peer-link is not configured: ifname %s, MAC %s vlan-id %d",
                                mac_msg->ifname, mac_msg->mac_str, mac_msg->vid);

                /*if orphan port mac but no peerlink, don't keep this mac*/
                if (from_mclag_intf == 0)
                    return 0;
            }
            else
            {
                /*Redirect the mac to peer-link*/
                memcpy(&mac_msg->ifname, csm->peer_itf_name, IFNAMSIZ);

                ICCPD_LOG_NOTICE(__FUNCTION__, "Redirect to peerlink for orphan port or portchannel is down, Add local age flag: %d  ifname %s, MAC %s vlan-id %d",
                                mac_msg->age_flag, mac_msg->ifname, mac_msg->mac_str, mac_msg->vid);
            }
        }
        else
        {
            /*Remove MAC_AGE_LOCAL flag*/
            mac_msg->age_flag = set_mac_local_age_flag(csm, mac_msg, 0);
        }

        if (iccp_csm_init_msg(&msg, (char*)mac_msg, sizeof(struct MACMsg)) == 0)
        {
            TAILQ_INSERT_TAIL(&(MLACP(csm).mac_list), msg, tail);
            /*ICCPD_LOG_INFO(__FUNCTION__, "add mac queue successfully");*/

            /*If the mac is from orphan port, or from MCLAG port but the local port is down*/
            if (strcmp(mac_msg->ifname, csm->peer_itf_name) == 0)
            {
                /*Send mac add message to mclagsyncd*/
                if (csm->peer_link_if && csm->peer_link_if->state == PORT_STATE_UP)
                    add_mac_to_chip(mac_msg, mac_msg->fdb_type);
            }
            else
            {
                /*from MCLAG port and the local port is up*/
                add_mac_to_chip(mac_msg, mac_msg->fdb_type);
            }
        }
    }

    return 0;
}

int mlacp_fsm_update_mac_info_from_peer(struct CSM* csm, struct mLACPMACInfoTLV* tlv)
{
    int count = 0;
    int i;

    if (!csm || !tlv)
        return MCLAG_ERROR;
    count = ntohs(tlv->num_of_entry);
    ICCPD_LOG_INFO(__FUNCTION__, "Received MAC Info count %d", count );

    for (i = 0; i < count; i++)
    {
        mlacp_fsm_update_mac_entry_from_peer(csm, &(tlv->MacEntry[i]));
    }
}

/*****************************************
 * Tool : Add ARP Info into ARP list
 *
 ****************************************/
void mlacp_enqueue_arp(struct CSM* csm, struct Msg* msg)
{
    struct ARPMsg *arp_msg = NULL;

    if (!csm)
    {
        if (msg)
            free(msg);
        return;
    }
    if (!msg)
        return;

    arp_msg = (struct ARPMsg*)msg->buf;
    if (arp_msg->op_type != NEIGH_SYNC_DEL)
    {
        TAILQ_INSERT_TAIL(&(MLACP(csm).arp_list), msg, tail);
    }

    return;
}

/*****************************************
 * Tool : Add Ndisc Info into ndisc list
 *
 ****************************************/
void mlacp_enqueue_ndisc(struct CSM *csm, struct Msg *msg)
{
    struct NDISCMsg *ndisc_msg = NULL;

    if (!csm)
    {
        if (msg)
            free(msg);
        return;
    }
    if (!msg)
        return;

    ndisc_msg = (struct NDISCMsg *)msg->buf;
    if (ndisc_msg->op_type != NEIGH_SYNC_DEL)
    {
        TAILQ_INSERT_TAIL(&(MLACP(csm).ndisc_list), msg, tail);
    }

    return;
}

/*****************************************
* ARP-Info Update
* ***************************************/
int mlacp_fsm_update_arp_entry(struct CSM* csm, struct ARPMsg *arp_entry)
{
    struct Msg* msg = NULL;
    struct ARPMsg *arp_msg = NULL, arp_data;
    struct LocalInterface* local_if;
    struct LocalInterface *peer_link_if = NULL;
    struct VLAN_ID *vlan_id_list = NULL;
    int set_arp_flag = 0;
    char mac_str[18] = "";

    if (!csm || !arp_entry)
        return MCLAG_ERROR;

    sprintf(mac_str, "%02x:%02x:%02x:%02x:%02x:%02x", arp_entry->mac_addr[0], arp_entry->mac_addr[1], arp_entry->mac_addr[2],
            arp_entry->mac_addr[3], arp_entry->mac_addr[4], arp_entry->mac_addr[5]);

    ICCPD_LOG_NOTICE(__FUNCTION__,
                   "Received ARP Info, intf[%s] IP[%s], MAC[%02x:%02x:%02x:%02x:%02x:%02x]",
                   arp_entry->ifname, show_ip_str(arp_entry->ipv4_addr),
                   arp_entry->mac_addr[0], arp_entry->mac_addr[1], arp_entry->mac_addr[2],
                   arp_entry->mac_addr[3], arp_entry->mac_addr[4], arp_entry->mac_addr[5]);

    if (strncmp(arp_entry->ifname, "Vlan", 4) == 0)
    {
        peer_link_if = local_if_find_by_name(csm->peer_itf_name);

        if (peer_link_if && !local_if_is_l3_mode(peer_link_if))
        {
            /* Is peer-linlk itf belong to a vlan the same as peer?*/
            LIST_FOREACH(vlan_id_list, &(peer_link_if->vlan_list), port_next)
            {
                if (!vlan_id_list->vlan_itf)
                    continue;
                if (strcmp(vlan_id_list->vlan_itf->name, arp_entry->ifname) != 0)
                    continue;
                if (!local_if_is_l3_mode(vlan_id_list->vlan_itf))
                    continue;

                ICCPD_LOG_DEBUG(__FUNCTION__, "ARP is learnt from intf %s, peer-link %s is the member of this vlan",
                                vlan_id_list->vlan_itf->name, peer_link_if->name);

                /* Peer-link belong to L3 vlan is alive, set the ARP info*/
                set_arp_flag = 1;

                break;
            }
        }
    }

    if (set_arp_flag == 0)
    {
        LIST_FOREACH(local_if, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (local_if->type == IF_T_PORT_CHANNEL)
            {
                if (!local_if_is_l3_mode(local_if))
                {
                    /* Is the L2 MLAG itf belong to a vlan the same as peer?*/
                    LIST_FOREACH(vlan_id_list, &(local_if->vlan_list), port_next)
                    {
                        if (!vlan_id_list->vlan_itf)
                            continue;
                        if (strcmp(vlan_id_list->vlan_itf->name, arp_entry->ifname) != 0)
                            continue;
                        if (!local_if_is_l3_mode(vlan_id_list->vlan_itf))
                            continue;

                        ICCPD_LOG_DEBUG(__FUNCTION__, "ARP is learnt from intf %s, mclag %s is the member of this vlan",
                                        vlan_id_list->vlan_itf->name, local_if->name);
                        break;
                    }

                    if (vlan_id_list && local_if->po_active == 1)
                    {
                        /* Any po of L3 vlan is alive, set the ARP info*/
                        set_arp_flag = 1;
                        break;
                    }
                }
                else
                {
                    /* Is the ARP belong to a L3 mode MLAG itf?*/
                    if (strcmp(local_if->name, arp_entry->ifname) == 0)
                    {
                        ICCPD_LOG_DEBUG(__FUNCTION__, "ARP is learnt from mclag L3 intf %s", local_if->name);
                        if (local_if->po_active == 1)
                        {
                            /* po is alive, set the ARP info*/
                            set_arp_flag = 1;
                            break;
                        }
                    }
                    else
                    {
                        continue;
                    }
                }
            }
        }
    }

    /* set dynamic ARP*/
    if (set_arp_flag == 1)
    {
        if (arp_entry->op_type == NEIGH_SYNC_ADD)
        {
            if (iccp_netlink_neighbor_request(AF_INET, (uint8_t *)&arp_entry->ipv4_addr, 1, arp_entry->mac_addr, arp_entry->ifname) < 0)
            {
                ICCPD_LOG_WARN(__FUNCTION__, "ARP add failure for %s %s %s",
                                arp_entry->ifname, show_ip_str(arp_entry->ipv4_addr), mac_str);
                return MCLAG_ERROR;
            }
        }
        else
        {
            if (iccp_netlink_neighbor_request(AF_INET, (uint8_t *)&arp_entry->ipv4_addr, 0, arp_entry->mac_addr, arp_entry->ifname) < 0)
            {
                ICCPD_LOG_WARN(__FUNCTION__, "ARP delete failure for %s %s %s",
                                arp_entry->ifname, show_ip_str(arp_entry->ipv4_addr), mac_str);
                return MCLAG_ERROR;
            }
        }

        /*ICCPD_LOG_DEBUG(__FUNCTION__, "%s: ARP update for %s %s %s",
                        __FUNCTION__, arp_entry->ifname, show_ip_str(arp_entry->ipv4_addr), mac_str);*/
    }
    else
    {
        ICCPD_LOG_NOTICE(__FUNCTION__, "Failure: port-channel is not alive");
        /*TODO Set static route through peer-link or just skip it?*/
    }

    /* update ARP list*/
    TAILQ_FOREACH(msg, &(MLACP(csm).arp_list), tail)
    {
        arp_msg = (struct ARPMsg*)msg->buf;
        if (arp_msg->ipv4_addr == arp_entry->ipv4_addr)
        {
            /*arp_msg->op_type = tlv->type;*/
            sprintf(arp_msg->ifname, "%s", arp_entry->ifname);
            memcpy(arp_msg->mac_addr, arp_entry->mac_addr, ETHER_ADDR_LEN);
            break;
        }
    }

    /* delete/add ARP list*/
    if (msg && arp_entry->op_type == NEIGH_SYNC_DEL)
    {
        TAILQ_REMOVE(&(MLACP(csm).arp_list), msg, tail);
        free(msg->buf);
        free(msg);
        /*ICCPD_LOG_INFO(__FUNCTION__, "Del arp queue successfully");*/
    }
    else if (!msg && arp_entry->op_type == NEIGH_SYNC_ADD)
    {
        arp_msg = (struct ARPMsg*)&arp_data;
        sprintf(arp_msg->ifname, "%s", arp_entry->ifname);
        arp_msg->ipv4_addr = arp_entry->ipv4_addr;
        arp_msg->op_type = arp_entry->op_type;
        memcpy(arp_msg->mac_addr, arp_entry->mac_addr, ETHER_ADDR_LEN);
        if (iccp_csm_init_msg(&msg, (char*)arp_msg, sizeof(struct ARPMsg)) == 0)
        {
            mlacp_enqueue_arp(csm, msg);
            /*ICCPD_LOG_INFO(__FUNCTION__, "Add arp queue successfully");*/
        }
    }

    /* remove all ARP msg queue, when receive peer's ARP list at the same time*/
    TAILQ_FOREACH(msg, &(MLACP(csm).arp_msg_list), tail)
    {
        arp_msg = (struct ARPMsg*)msg->buf;
        if (arp_msg->ipv4_addr == arp_entry->ipv4_addr)
            break;
    }

    while (msg)
    {
        arp_msg = (struct ARPMsg*)msg->buf;
        TAILQ_REMOVE(&(MLACP(csm).arp_msg_list), msg, tail);
        free(msg->buf);
        free(msg);
        TAILQ_FOREACH(msg, &(MLACP(csm).arp_msg_list), tail)
        {
            arp_msg = (struct ARPMsg*)msg->buf;
            if (arp_msg->ipv4_addr == arp_entry->ipv4_addr)
                break;
        }
    }

    return 0;
}

int mlacp_fsm_update_arp_info(struct CSM* csm, struct mLACPARPInfoTLV* tlv)
{
    int count = 0;
    int i;

    if (!csm || !tlv)
        return MCLAG_ERROR;
    count = ntohs(tlv->num_of_entry);
    ICCPD_LOG_INFO(__FUNCTION__, "Received ARP Info count  %d ", count );

    for (i = 0; i < count; i++)
    {
        mlacp_fsm_update_arp_entry(csm, &(tlv->ArpEntry[i]));
    }
}

/*****************************************
* NDISC-Info Update
* ***************************************/
int mlacp_fsm_update_ndisc_entry(struct CSM *csm, struct NDISCMsg *ndisc_entry)
{
    struct Msg *msg = NULL;
    struct NDISCMsg *ndisc_msg = NULL, ndisc_data;
    struct LocalInterface *local_if;
    struct LocalInterface *peer_link_if = NULL;
    struct VLAN_ID *vlan_id_list = NULL;
    int set_ndisc_flag = 0;
    char mac_str[18] = "";

    if (!csm || !ndisc_entry)
        return MCLAG_ERROR;

    sprintf(mac_str, "%02x:%02x:%02x:%02x:%02x:%02x", ndisc_entry->mac_addr[0], ndisc_entry->mac_addr[1], ndisc_entry->mac_addr[2],
            ndisc_entry->mac_addr[3], ndisc_entry->mac_addr[4], ndisc_entry->mac_addr[5]);

    ICCPD_LOG_NOTICE(__FUNCTION__,
                   "Received ND Info, intf[%s] IP[%s], MAC[%s]", ndisc_entry->ifname, show_ipv6_str((char *)ndisc_entry->ipv6_addr), mac_str);

    if (strncmp(ndisc_entry->ifname, "Vlan", 4) == 0)
    {
        peer_link_if = local_if_find_by_name(csm->peer_itf_name);

        if (peer_link_if && !local_if_is_l3_mode(peer_link_if))
        {
            /* Is peer-linlk itf belong to a vlan the same as peer? */
            LIST_FOREACH(vlan_id_list, &(peer_link_if->vlan_list), port_next)
            {
                if (!vlan_id_list->vlan_itf)
                    continue;
                if (strcmp(vlan_id_list->vlan_itf->name, ndisc_entry->ifname) != 0)
                    continue;
                if (!local_if_is_l3_mode(vlan_id_list->vlan_itf))
                    continue;

                ICCPD_LOG_DEBUG(__FUNCTION__,
                                "ND is learnt from intf %s, peer-link %s is the member of this vlan",
                                vlan_id_list->vlan_itf->name, peer_link_if->name);

                /* Peer-link belong to L3 vlan is alive, set the NDISC info */
                set_ndisc_flag = 1;

                break;
            }
        }
    }

    if (set_ndisc_flag == 0)
    {
        LIST_FOREACH(local_if, &(MLACP(csm).lif_list), mlacp_next)
        {
            if (local_if->type == IF_T_PORT_CHANNEL)
            {
                if (!local_if_is_l3_mode(local_if))
                {
                    /* Is the L2 MLAG itf belong to a vlan the same as peer? */
                    LIST_FOREACH(vlan_id_list, &(local_if->vlan_list), port_next)
                    {
                        if (!vlan_id_list->vlan_itf)
                            continue;
                        if (strcmp(vlan_id_list->vlan_itf->name, ndisc_entry->ifname) != 0)
                            continue;
                        if (!local_if_is_l3_mode(vlan_id_list->vlan_itf))
                            continue;

                        ICCPD_LOG_DEBUG(__FUNCTION__,
                                        "ND is learnt from intf %s, %s is the member of this vlan", vlan_id_list->vlan_itf->name, local_if->name);
                        break;
                    }

                    if (vlan_id_list && local_if->po_active == 1)
                    {
                        /* Any po of L3 vlan is alive, set the NDISC info */
                        set_ndisc_flag = 1;
                        break;
                    }
                }
                else
                {
                    /* Is the ARP belong to a L3 mode MLAG itf? */
                    if (strcmp(local_if->name, ndisc_entry->ifname) == 0)
                    {
                        ICCPD_LOG_DEBUG(__FUNCTION__, "ND is learnt from mclag L3 intf %s", local_if->name);
                        if (local_if->po_active == 1)
                        {
                            /* po is alive, set the NDISC info */
                            set_ndisc_flag = 1;
                            break;
                        }
                    }
                    else
                    {
                        continue;
                    }
                }
            }
        }
    }

    /* set dynamic Ndisc */
    if (set_ndisc_flag == 1)
    {
        if (ndisc_entry->op_type == NEIGH_SYNC_ADD)
        {
            if (iccp_netlink_neighbor_request(AF_INET6, (uint8_t *)ndisc_entry->ipv6_addr, 1, ndisc_entry->mac_addr, ndisc_entry->ifname) < 0)
            {
                ICCPD_LOG_WARN(__FUNCTION__, "Failed to add nd entry(%s %s %s) to kernel",
                                ndisc_entry->ifname, show_ipv6_str((char *)ndisc_entry->ipv6_addr), mac_str);
                return MCLAG_ERROR;
            }

        }
        else
        {
            if (iccp_netlink_neighbor_request(AF_INET6, (uint8_t *)ndisc_entry->ipv6_addr, 0, ndisc_entry->mac_addr, ndisc_entry->ifname) < 0)
            {
                ICCPD_LOG_WARN(__FUNCTION__, "Failed to delete nd entry(%s %s %s) from kernel",
                                ndisc_entry->ifname, show_ipv6_str((char *)ndisc_entry->ipv6_addr), mac_str);
                return MCLAG_ERROR;
            }

        }

        /* ICCPD_LOG_DEBUG(__FUNCTION__, "NDISC update for %s %s %s", ndisc_entry->ifname, show_ipv6_str((char *)ndisc_entry->ipv6_addr), mac_str); */
    }
    else
    {
        ICCPD_LOG_DEBUG(__FUNCTION__, "Failure: port-channel is not alive");
        /* TODO Set static route through peer-link or just skip it? */
    }

    /* update NDISC list */
    TAILQ_FOREACH(msg, &(MLACP(csm).ndisc_list), tail)
    {
        ndisc_msg = (struct NDISCMsg *)msg->buf;
        if (memcmp((char *)ndisc_msg->ipv6_addr, (char *)ndisc_entry->ipv6_addr, 16) == 0)
        {
            /* ndisc_msg->op_type = tlv->type; */
            sprintf(ndisc_msg->ifname, "%s", ndisc_entry->ifname);
            memcpy(ndisc_msg->mac_addr, ndisc_entry->mac_addr, ETHER_ADDR_LEN);
            break;
        }
    }

    /* delete/add NDISC list */
    if (msg && ndisc_entry->op_type == NEIGH_SYNC_DEL)
    {
        TAILQ_REMOVE(&(MLACP(csm).ndisc_list), msg, tail);
        free(msg->buf);
        free(msg);
        /* ICCPD_LOG_INFO(__FUNCTION__, "Del ndisc queue successfully"); */
    }
    else if (!msg && ndisc_entry->op_type == NEIGH_SYNC_ADD)
    {
        ndisc_msg = (struct NDISCMsg *)&ndisc_data;
        sprintf(ndisc_msg->ifname, "%s", ndisc_entry->ifname);
        memcpy((char *)ndisc_msg->ipv6_addr, (char *)ndisc_entry->ipv6_addr, 16);
        ndisc_msg->op_type = ndisc_entry->op_type;
        memcpy(ndisc_msg->mac_addr, ndisc_entry->mac_addr, ETHER_ADDR_LEN);
        if (iccp_csm_init_msg(&msg, (char *)ndisc_msg, sizeof(struct NDISCMsg)) == 0)
        {
            mlacp_enqueue_ndisc(csm, msg);
            /* ICCPD_LOG_INFO(__FUNCTION__, "Add ndisc queue successfully"); */
        }
    }

    /* remove all NDISC msg queue, when receive peer's NDISC list at the same time */
    TAILQ_FOREACH(msg, &(MLACP(csm).ndisc_msg_list), tail)
    {
        ndisc_msg = (struct NDISCMsg *)msg->buf;
        if (memcmp((char *)ndisc_msg->ipv6_addr, (char *)ndisc_entry->ipv6_addr, 16) == 0)
            break;
    }

    while (msg)
    {
        ndisc_msg = (struct NDISCMsg *)msg->buf;
        TAILQ_REMOVE(&(MLACP(csm).ndisc_msg_list), msg, tail);
        free(msg->buf);
        free(msg);
        TAILQ_FOREACH(msg, &(MLACP(csm).ndisc_msg_list), tail)
        {
            ndisc_msg = (struct NDISCMsg *)msg->buf;
            if (memcmp((char *)ndisc_msg->ipv6_addr, (char *)ndisc_entry->ipv6_addr, 16) == 0)
                break;
        }
    }

    return 0;
}

int mlacp_fsm_update_ndisc_info(struct CSM *csm, struct mLACPNDISCInfoTLV *tlv)
{
    int count = 0;
    int i;

    if (!csm || !tlv)
        return MCLAG_ERROR;
    count = ntohs(tlv->num_of_entry);
    ICCPD_LOG_INFO(__FUNCTION__, "Received NDISC Info count  %d ", count);

    for (i = 0; i < count; i++)
    {
        mlacp_fsm_update_ndisc_entry(csm, &(tlv->NdiscEntry[i]));
    }
}

/*****************************************
* Port-Channel-Info Update
* ***************************************/
int mlacp_fsm_update_port_channel_info(struct CSM* csm,
                                       struct mLACPPortChannelInfoTLV* tlv)
{
    struct PeerInterface* peer_if = NULL;
    struct VLAN_ID* peer_vlan_id = NULL;
    int i = 0;

    if (csm == NULL || tlv == NULL )
        return MCLAG_ERROR;

    LIST_FOREACH(peer_if, &(MLACP(csm).pif_list), mlacp_next)
    {
        if (peer_if->type != IF_T_PORT_CHANNEL)
            continue;

        if (peer_if->po_id != ntohs(tlv->agg_id))
            continue;

        LIST_FOREACH(peer_vlan_id, &(peer_if->vlan_list), port_next)
        {
            peer_vlan_id->vlan_removed = 1;
        }

        /* Record peer info*/
        peer_if->ipv4_addr = ntohl(tlv->ipv4_addr);
        peer_if->l3_mode = tlv->l3_mode;

        for (i = 0; i < ntohs(tlv->num_of_vlan_id); i++)
        {
            peer_if_add_vlan(peer_if, ntohs(tlv->vlanData[i].vlan_id));
        }

        peer_if_clean_unused_vlan(peer_if);

        iccp_consistency_check(peer_if->name);

        ICCPD_LOG_DEBUG(__FUNCTION__, "Peer intf %s info: ipv4 addr %s l3 mode %d", peer_if->name, show_ip_str( tlv->ipv4_addr), peer_if->l3_mode);
        break;
    }

    return 0;
}

/*****************************************
* Peerlink port Update
* ***************************************/
int mlacp_fsm_update_peerlink_info(struct CSM* csm,
                                   struct mLACPPeerLinkInfoTLV* tlv)
{
    if (csm == NULL || tlv == NULL )
        return MCLAG_ERROR;

    if (!csm->peer_link_if)
    {
        ICCPD_LOG_WARN(__FUNCTION__, "Peerlink port info recv from peer, local peerlink is not exist!");
        return 0;
    }

    if (csm->peer_link_if->type != tlv->port_type)
        ICCPD_LOG_NOTICE(__FUNCTION__, "Peerlink port type of peer %d is not same with local %d !", tlv->port_type, csm->peer_link_if->type);

    if (tlv->port_type == IF_T_VXLAN && strncmp(csm->peer_itf_name, tlv->if_name, strlen(csm->peer_itf_name)))
        ICCPD_LOG_NOTICE(__FUNCTION__, "Peerlink port is vxlan port, but peerlink port of peer %s is not same with local %s !", tlv->if_name, csm->peer_itf_name);

    return 0;
}

/*****************************************
* Heartbeat Update
*****************************************/
int mlacp_fsm_update_heartbeat(struct CSM* csm, struct mLACPHeartbeatTLV* tlv)
{
    if (!csm || !tlv)
        return MCLAG_ERROR;

    time(&csm->heartbeat_update_time);

    return 0;
}

/*****************************************
* warm-reboot flag Update
*****************************************/
int mlacp_fsm_update_warmboot(struct CSM* csm, struct mLACPWarmbootTLV* tlv)
{
    if (!csm || !tlv)
        return MCLAG_ERROR;

    time(&csm->peer_warm_reboot_time);
    ICCPD_LOG_NOTICE(__FUNCTION__, "Receive warm reboot notification from peer!");

    return 0;
}

