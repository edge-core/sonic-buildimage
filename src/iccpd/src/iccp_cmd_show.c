/*
 * iccp_cmd_show.c
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
#include <ctype.h>
#include <net/if.h>
#include <sys/queue.h>

#include "../include/iccp_csm.h"
#include "../include/mlacp_tlv.h"
#include "../include/system.h"
#include "../include/logger.h"
#include "mclagdctl/mclagdctl.h"
#include "../include/iccp_cmd_show.h"
#include "../include/mlacp_link_handler.h"

int iccp_mclag_config_dump(char * *buf,  int *num, int mclag_id)
{
    struct mclagd_state state_info;
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct LocalInterface *peer_link_if = NULL;
    struct LocalInterface *lif_po = NULL;
    struct LoggerConfig* logconfig;
    char unknown[] = { "Unknown" };
    int mclag_num = 0;
    int id_exist = 0;
    int str_size = 0;
    int len = 0;
    char *state_buf = NULL;
    int state_buf_size = MCLAGDCTL_CMD_SIZE;

    if (!(sys = system_get_instance()))
    {
        return EXEC_TYPE_NO_EXIST_SYS;
    }

    state_buf = (char*)malloc(state_buf_size);
    if (!state_buf)
        return EXEC_TYPE_FAILED;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        memset(&state_info, 0, sizeof(struct mclagd_state));

        if (csm->current_state == ICCP_OPERATIONAL)
            state_info.keepalive = 1;
        else
            state_info.keepalive = 0;

        if (mclag_id > 0)
        {
            if (csm->mlag_id == mclag_id)
                id_exist = 1;
            else
                continue;
        }

        peer_link_if = local_if_find_by_name(csm->peer_itf_name);

        if (csm->mlag_id <= 0)
            state_info.mclag_id = -1;
        else
            state_info.mclag_id = csm->mlag_id;

        memcpy(state_info.local_ip, csm->sender_ip, ICCP_MAX_IP_STR_LEN);
        memcpy(state_info.peer_ip, csm->peer_ip, ICCP_MAX_IP_STR_LEN);

        if (peer_link_if)
            memcpy(state_info.peer_link_if, peer_link_if->name, ICCP_MAX_PORT_NAME);
        else
            memcpy(state_info.peer_link_if, unknown, strlen(unknown));

        if (peer_link_if)
            memcpy(state_info.peer_link_mac, peer_link_if->mac_addr, 6);

        logconfig = logger_get_configuration();
        memcpy(state_info.loglevel, log_level_to_string(logconfig->log_level), strlen( log_level_to_string(logconfig->log_level)));

        state_info.role = csm->role_type;

        str_size = MCLAGDCTL_PORT_MEMBER_BUF_LEN;

        LIST_FOREACH(lif_po, &(MLACP(csm).lif_list), mlacp_next)
        {

            if (str_size - len < ICCP_MAX_PORT_NAME)
                break;

            if (lif_po->type == IF_T_PORT_CHANNEL)
                len += snprintf(state_info.enabled_po + len, str_size - len, "%s,", lif_po->name);
        }

        /*Skip the last ','*/
        len = strlen(state_info.enabled_po);
        if (len > 0)
        {
            state_info.enabled_po[len - 1] = '\0';
        }

        memcpy(state_buf + MCLAGD_REPLY_INFO_HDR + mclag_num * sizeof(struct mclagd_state),
               &state_info, sizeof(struct mclagd_state));
        mclag_num++;

        if ((mclag_num + 1) * sizeof(struct mclagd_state) > (state_buf_size - MCLAGD_REPLY_INFO_HDR))
        {
            state_buf_size += MCLAGDCTL_CMD_SIZE;
            state_buf = (char*)realloc(state_buf, state_buf_size);
            if (!state_buf)
                return EXEC_TYPE_FAILED;
        }
    }

    *buf = state_buf;
    *num = mclag_num;

    if (mclag_id > 0 && !id_exist)
        return EXEC_TYPE_NO_EXIST_MCLAGID;

    return EXEC_TYPE_SUCCESS;
}

int iccp_arp_dump(char * *buf, int *num, int mclag_id)
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct Msg *msg = NULL;
    struct ARPMsg *iccpd_arp = NULL;
    struct mclagd_arp_msg mclagd_arp;
    int arp_num = 0;
    int id_exist = 0;
    char * arp_buf = NULL;
    int arp_buf_size = MCLAGDCTL_CMD_SIZE;

    if (!(sys = system_get_instance()))
    {
        return EXEC_TYPE_NO_EXIST_SYS;
    }

    arp_buf = (char*)malloc(arp_buf_size);
    if (!arp_buf)
        return EXEC_TYPE_FAILED;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        if (mclag_id > 0)
        {
            if (csm->mlag_id == mclag_id)
                id_exist = 1;
            else
                continue;
        }

        TAILQ_FOREACH(msg, &MLACP(csm).arp_list, tail)
        {
            memset(&mclagd_arp, 0, sizeof(struct mclagd_arp_msg));
            iccpd_arp = (struct ARPMsg*)msg->buf;

            mclagd_arp.op_type = iccpd_arp->op_type;
            memcpy(mclagd_arp.ifname, iccpd_arp->ifname, strlen(iccpd_arp->ifname));
            memcpy(mclagd_arp.ipv4_addr, show_ip_str(iccpd_arp->ipv4_addr), 16);
            memcpy(mclagd_arp.mac_addr, iccpd_arp->mac_addr, 6);

            memcpy(arp_buf + MCLAGD_REPLY_INFO_HDR + arp_num * sizeof(struct mclagd_arp_msg),
                   &mclagd_arp, sizeof(struct mclagd_arp_msg));

            arp_num++;

            if ((arp_num + 1) * sizeof(struct mclagd_arp_msg) > (arp_buf_size - MCLAGD_REPLY_INFO_HDR))
            {
                arp_buf_size += MCLAGDCTL_CMD_SIZE;
                arp_buf = (char*)realloc(arp_buf, arp_buf_size);
                if (!arp_buf)
                    return EXEC_TYPE_FAILED;
            }
        }
    }

    *buf = arp_buf;
    *num = arp_num;

    if (mclag_id > 0 && !id_exist)
        return EXEC_TYPE_NO_EXIST_MCLAGID;

    return EXEC_TYPE_SUCCESS;
}

int iccp_ndisc_dump(char * *buf, int *num, int mclag_id)
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct Msg *msg = NULL;
    struct NDISCMsg *iccpd_ndisc = NULL;
    struct mclagd_ndisc_msg mclagd_ndisc;
    int ndisc_num = 0;
    int id_exist = 0;
    char *ndisc_buf = NULL;
    int ndisc_buf_size = MCLAGDCTL_CMD_SIZE;

    if (!(sys = system_get_instance()))
    {
        ICCPD_LOG_INFO(__FUNCTION__, "cannot find sys!\n");
        return EXEC_TYPE_NO_EXIST_SYS;
    }

    ndisc_buf = (char *)malloc(ndisc_buf_size);
    if (!ndisc_buf)
        return EXEC_TYPE_FAILED;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        if (mclag_id > 0)
        {
            if (csm->mlag_id == mclag_id)
                id_exist = 1;
            else
                continue;
        }

        TAILQ_FOREACH(msg, &MLACP(csm).ndisc_list, tail)
        {
            memset(&mclagd_ndisc, 0, sizeof(struct mclagd_ndisc_msg));
            iccpd_ndisc = (struct NDISCMsg *)msg->buf;

            mclagd_ndisc.op_type = iccpd_ndisc->op_type;
            memcpy(mclagd_ndisc.ifname, iccpd_ndisc->ifname, strlen(iccpd_ndisc->ifname));
            memcpy(mclagd_ndisc.ipv6_addr, show_ipv6_str((char *)iccpd_ndisc->ipv6_addr), 46);
            memcpy(mclagd_ndisc.mac_addr, iccpd_ndisc->mac_addr, 6);

            memcpy(ndisc_buf + MCLAGD_REPLY_INFO_HDR + ndisc_num * sizeof(struct mclagd_ndisc_msg),
                   &mclagd_ndisc, sizeof(struct mclagd_ndisc_msg));

            ndisc_num++;

            if ((ndisc_num + 1) * sizeof(struct mclagd_ndisc_msg) > (ndisc_buf_size - MCLAGD_REPLY_INFO_HDR))
            {
                ndisc_buf_size += MCLAGDCTL_CMD_SIZE;
                ndisc_buf = (char *)realloc(ndisc_buf, ndisc_buf_size);
                if (!ndisc_buf)
                    return EXEC_TYPE_FAILED;
            }
        }
    }

    *buf = ndisc_buf;
    *num = ndisc_num;

    if (mclag_id > 0 && !id_exist)
        return EXEC_TYPE_NO_EXIST_MCLAGID;

    return EXEC_TYPE_SUCCESS;
}

int iccp_mac_dump(char * *buf, int *num, int mclag_id)
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct Msg *msg = NULL;
    struct MACMsg *iccpd_mac = NULL;
    struct mclagd_mac_msg mclagd_mac;
    int mac_num = 0;
    int id_exist = 0;
    char * mac_buf = NULL;
    int mac_buf_size = MCLAGDCTL_CMD_SIZE;

    if (!(sys = system_get_instance()))
    {
        return EXEC_TYPE_NO_EXIST_SYS;
    }

    mac_buf = (char*)malloc(mac_buf_size);
    if (!mac_buf)
        return EXEC_TYPE_FAILED;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        if (mclag_id > 0)
        {
            if (csm->mlag_id == mclag_id)
                id_exist = 1;
            else
                continue;
        }

        TAILQ_FOREACH(msg, &MLACP(csm).mac_list, tail)
        {
            memset(&mclagd_mac, 0, sizeof(struct mclagd_mac_msg));
            iccpd_mac = (struct MACMsg*)msg->buf;

            mclagd_mac.op_type = iccpd_mac->op_type;
            mclagd_mac.fdb_type = iccpd_mac->fdb_type;
            memcpy(mclagd_mac.mac_str, iccpd_mac->mac_str, ETHER_ADDR_STR_LEN);
            mclagd_mac.vid = iccpd_mac->vid;
            memcpy(mclagd_mac.ifname, iccpd_mac->ifname, strlen(iccpd_mac->ifname));
            memcpy(mclagd_mac.origin_ifname, iccpd_mac->origin_ifname, strlen(iccpd_mac->origin_ifname));
            mclagd_mac.age_flag = iccpd_mac->age_flag;

            memcpy(mac_buf + MCLAGD_REPLY_INFO_HDR + mac_num * sizeof(struct mclagd_mac_msg),
                   &mclagd_mac, sizeof(struct mclagd_mac_msg));

            mac_num++;

            if ((mac_num + 1) * sizeof(struct mclagd_mac_msg) > (mac_buf_size - MCLAGD_REPLY_INFO_HDR))
            {
                mac_buf_size += MCLAGDCTL_CMD_SIZE;
                mac_buf = (char*)realloc(mac_buf, mac_buf_size);
                if (!mac_buf)
                    return EXEC_TYPE_FAILED;
            }
        }
    }

    *buf = mac_buf;
    *num = mac_num;

    if (mclag_id > 0 && !id_exist)
        return EXEC_TYPE_NO_EXIST_MCLAGID;

    return EXEC_TYPE_SUCCESS;
}

int iccp_local_if_dump(char * *buf,  int *num, int mclag_id)
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct LocalInterface *lif_po = NULL;
    struct mclagd_local_if mclagd_lif;
    struct VLAN_ID* vlan_id = NULL;
    char * str_buf = NULL;
    int str_size = MCLAGDCTL_PARA3_LEN - 1;
    int len = 0;
    int lif_num = 0;
    int id_exist = 0;
    int lif_buf_size = MCLAGDCTL_CMD_SIZE;
    char * lif_buf = NULL;

    if (!(sys = system_get_instance()))
    {
        return EXEC_TYPE_NO_EXIST_SYS;
    }

    lif_buf = (char*)malloc(lif_buf_size);
    if (!lif_buf)
        return EXEC_TYPE_FAILED;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        if (mclag_id > 0)
        {
            if (csm->mlag_id == mclag_id)
                id_exist = 1;
            else
                continue;
        }

        LIST_FOREACH(lif_po, &(MLACP(csm).lif_list), mlacp_next)
        {
            memset(&mclagd_lif, 0, sizeof(struct mclagd_local_if));

            mclagd_lif.ifindex = lif_po->ifindex;

            if (lif_po->type == IF_T_UNKNOW)
                memcpy(mclagd_lif.type, "Unknown", 6);
            else if (lif_po->type == IF_T_PORT)
                memcpy(mclagd_lif.type, "Ethernet", 8);
            else if (lif_po->type == IF_T_PORT_CHANNEL)
                memcpy(mclagd_lif.type, "PortChannel", 11);

            memcpy(mclagd_lif.name, lif_po->name, MAX_L_PORT_NAME);
            memcpy(mclagd_lif.mac_addr, lif_po->mac_addr, ETHER_ADDR_LEN);

            if (lif_po->state == PORT_STATE_UP)
                memcpy(mclagd_lif.state, "Up", 2);
            else if (lif_po->state == PORT_STATE_DOWN)
                memcpy(mclagd_lif.state, "Down", 4);
            else if (lif_po->state == PORT_STATE_ADMIN_DOWN)
                memcpy(mclagd_lif.state, "Admin-down", 10);
            else if (lif_po->state == PORT_STATE_TEST)
                memcpy(mclagd_lif.state, "Test", 4);

            memcpy(mclagd_lif.ipv4_addr, show_ip_str(htonl(lif_po->ipv4_addr)), 16);
            mclagd_lif.prefixlen = lif_po->prefixlen;

            mclagd_lif.l3_mode = local_if_is_l3_mode(lif_po);

            mclagd_lif.is_peer_link = lif_po->is_peer_link;

            memcpy(mclagd_lif.portchannel_member_buf, lif_po->portchannel_member_buf, 512);

            mclagd_lif.po_id = lif_po->po_id;
            mclagd_lif.po_active = lif_po->po_active;
            /*mlacp_state*/
            if (lif_po->mlacp_state == MLACP_STATE_INIT)
                memcpy(mclagd_lif.mlacp_state, "INIT", 4);
            else if (lif_po->mlacp_state == MLACP_STATE_STAGE1)
                memcpy(mclagd_lif.mlacp_state, "STAGE1", 6);
            else if (lif_po->mlacp_state == MLACP_STATE_STAGE2)
                memcpy(mclagd_lif.mlacp_state, "STAGE2", 6);
            else if (lif_po->mlacp_state == MLACP_STATE_EXCHANGE)
                memcpy(mclagd_lif.mlacp_state, "EXCHANGE", 8);
            else if (lif_po->mlacp_state == MLACP_STATE_ERROR)
                memcpy(mclagd_lif.mlacp_state, "ERROR", 5);

            mclagd_lif.isolate_to_peer_link = lif_po->isolate_to_peer_link;

            str_buf = mclagd_lif.vlanlist;

            len = 0;
            LIST_FOREACH(vlan_id, &(lif_po->vlan_list), port_next)
            {
                if (vlan_id != NULL )
                {
                    if (str_size - len < 4)
                        break;
                    len += snprintf(str_buf + len, str_size - len, "%d ", vlan_id->vid);
                }
            }

            memcpy(lif_buf + MCLAGD_REPLY_INFO_HDR + lif_num * sizeof(struct mclagd_local_if),
                   &mclagd_lif, sizeof(struct mclagd_local_if));

            lif_num++;

            if ((lif_num + 1) * sizeof(struct mclagd_local_if) > (lif_buf_size - MCLAGD_REPLY_INFO_HDR))
            {
                lif_buf_size += MCLAGDCTL_CMD_SIZE;
                lif_buf = (char*)realloc(lif_buf, lif_buf_size);
                if (!lif_buf)
                    return EXEC_TYPE_FAILED;
            }
        }
    }

    *buf = lif_buf;
    *num = lif_num;

    if (mclag_id > 0 && !id_exist)
        return EXEC_TYPE_NO_EXIST_MCLAGID;

    return EXEC_TYPE_SUCCESS;
}

int iccp_peer_if_dump(char * *buf, int *num, int mclag_id)
{
    struct System *sys = NULL;
    struct CSM *csm = NULL;
    struct PeerInterface *pif_po = NULL;
    struct mclagd_peer_if mclagd_pif;
    int pif_num = 0;
    int id_exist = 0;
    int pif_buf_size = MCLAGDCTL_CMD_SIZE;
    char *pif_buf = NULL;

    if (!(sys = system_get_instance()))
    {
        return EXEC_TYPE_NO_EXIST_SYS;
    }

    pif_buf = (char*)malloc(pif_buf_size);
    if (!pif_buf)
        return EXEC_TYPE_FAILED;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        if (mclag_id > 0)
        {
            if (csm->mlag_id == mclag_id)
                id_exist = 1;
            else
                continue;
        }

        LIST_FOREACH(pif_po, &(MLACP(csm).pif_list), mlacp_next)
        {
            memset(&mclagd_pif, 0, sizeof(struct mclagd_peer_if));

            mclagd_pif.ifindex = pif_po->ifindex;

            if (pif_po->type == IF_T_UNKNOW)
                memcpy(mclagd_pif.type, "Unknown", 6);
            else if (pif_po->type == IF_T_PORT)
                memcpy(mclagd_pif.type, "Ethernet", 8);
            else if (pif_po->type == IF_T_PORT_CHANNEL)
                memcpy(mclagd_pif.type, "PortChannel", 11);

            memcpy(mclagd_pif.name, pif_po->name, MAX_L_PORT_NAME);
            memcpy(mclagd_pif.mac_addr, pif_po->mac_addr, ETHER_ADDR_LEN);

            if (pif_po->state == PORT_STATE_UP)
                memcpy(mclagd_pif.state, "Up", 2);
            else if (pif_po->state == PORT_STATE_DOWN)
                memcpy(mclagd_pif.state, "Down", 4);
            else if (pif_po->state == PORT_STATE_ADMIN_DOWN)
                memcpy(mclagd_pif.state, "Admin-down", 10);
            else if (pif_po->state == PORT_STATE_TEST)
                memcpy(mclagd_pif.state, "Test", 4);

            mclagd_pif.po_id = pif_po->po_id;
            mclagd_pif.po_active = pif_po->po_active;

            memcpy(pif_buf + MCLAGD_REPLY_INFO_HDR + pif_num * sizeof(struct mclagd_peer_if),
                   &mclagd_pif, sizeof(struct mclagd_peer_if));

            pif_num++;

            if ((pif_num + 1) * sizeof(struct mclagd_peer_if) > (pif_buf_size - MCLAGD_REPLY_INFO_HDR))
            {
                pif_buf_size += MCLAGDCTL_CMD_SIZE;
                pif_buf = (char*)realloc(pif_buf, pif_buf_size);
                if (!pif_buf)
                    return EXEC_TYPE_FAILED;
            }
        }
    }

    *buf = pif_buf;
    *num = pif_num;

    if (mclag_id > 0 && !id_exist)
        return EXEC_TYPE_NO_EXIST_MCLAGID;

    return EXEC_TYPE_SUCCESS;
}

