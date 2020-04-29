/*
 *  mlacp_fsm.c
 *  mLACP finite state machine handler.
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
#include <stdlib.h>
#include <time.h>

#include <sys/queue.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <msg_format.h>
#include <system.h>
#include <logger.h>
#include "../include/mlacp_tlv.h"
#include "../include/mlacp_sync_prepare.h"
#include "../include/mlacp_link_handler.h"
#include "../include/mlacp_sync_update.h"

#include <signal.h>

/*****************************************
* Define
*
* ***************************************/
#define MLACP_MSG_QUEUE_REINIT(list) \
    { \
        struct Msg* msg = NULL; \
        while (!TAILQ_EMPTY(&(list))) { \
            msg = TAILQ_FIRST(&(list)); \
            TAILQ_REMOVE(&(list), msg, tail); \
            free(msg->buf); \
            free(msg); \
        } \
        TAILQ_INIT(&(list)); \
    }

#define PIF_QUEUE_REINIT(list) \
    { \
        while (!LIST_EMPTY(&(list))) { \
            struct PeerInterface* peer_if = NULL; \
            peer_if = LIST_FIRST(&(list)); \
            LIST_REMOVE(peer_if, mlacp_next); \
            free(peer_if); \
        } \
        LIST_INIT(&(list)); \
    }

#define LIF_QUEUE_REINIT(list) \
    { \
        while (!LIST_EMPTY(&(list))) { \
            struct LocalInterface* lif = NULL; \
            lif = LIST_FIRST(&(list)); \
            if (lif->type == IF_T_PORT_CHANNEL && lif->is_arp_accept) { \
                if ((set_sys_arp_accept_flag(lif->name, 0)) == 0) \
                lif->is_arp_accept = 0; \
            } \
            LIST_REMOVE (lif, mlacp_next); \
        } \
        LIST_INIT(&(list)); \
    }

#define LIF_PURGE_QUEUE_REINIT(list) \
    { \
        while (!LIST_EMPTY(&(list))) { \
            struct LocalInterface* lif = NULL; \
            lif = LIST_FIRST(&(list)); \
            LIST_REMOVE(lif, mlacp_purge_next); \
        } \
        LIST_INIT(&(list)); \
    }

#define WARM_REBOOT_TIMEOUT 90

/*****************************************
* Static Function
*
* ***************************************/
static char *mlacp_state(struct CSM* csm);
static void mlacp_resync_arp(struct CSM* csm);
static void mlacp_resync_ndisc(struct CSM* csm);
static void mlacp_resync_mac(struct CSM* csm);
/* Sync Sender APIs*/
static void mlacp_sync_send_sysConf(struct CSM* csm);
static void mlacp_sync_send_aggConf(struct CSM* csm);
static void mlacp_sync_send_aggState(struct CSM* csm);
static void mlacp_sync_send_syncArpInfo(struct CSM* csm);
static void mlacp_sync_send_syncNdiscInfo(struct CSM* csm);
static void mlacp_sync_send_heartbeat(struct CSM* csm);
static void mlacp_sync_send_syncDoneData(struct CSM* csm);
/* Sync Reciever APIs*/
static void mlacp_sync_recv_sysConf(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_portConf(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_portPrio(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_portState(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_aggConf(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_aggState(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_syncData(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_syncReq(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_portChanInfo(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_peerLlinkInfo(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_arpInfo(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_recv_stpInfo(struct CSM* csm, struct Msg* msg);

/* Sync Handler*/
static void mlacp_sync_send_nak_handler(struct CSM* csm,  struct Msg* msg);
static void mlacp_sync_recv_nak_handler(struct CSM* csm,  struct Msg* msg);
static void mlacp_sync_sender_handler(struct CSM* csm);
static void mlacp_sync_receiver_handler(struct CSM* csm, struct Msg* msg);
static void mlacp_sync_send_all_info_handler(struct CSM* csm);

/* Sync State Handler*/
static void mlacp_stage_sync_send_handler(struct CSM* csm, struct Msg* msg);
static void mlacp_stage_sync_request_handler(struct CSM* csm, struct Msg* msg);
static void mlacp_stage_handler(struct CSM* csm, struct Msg* msg);
static void mlacp_exchange_handler(struct CSM* csm, struct Msg* msg);

/******************************************************************
 * Sync Sender APIs
 *
 *****************************************************************/
static void mlacp_sync_send_sysConf(struct CSM* csm)
{
    int msg_len = 0;

    memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
    msg_len = mlacp_prepare_for_sys_config(csm, g_csm_buf, CSM_BUFFER_SIZE);
    if (msg_len > 0)
        iccp_csm_send(csm, g_csm_buf, msg_len);
    else
        ICCPD_LOG_WARN(__FUNCTION__, "Invalid sysconf packet.");

    /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [SYNC_Send] SysConf, len=[%d]", msg_len);*/

    return;
}

static void mlacp_sync_send_aggConf(struct CSM* csm)
{
    struct System* sys = NULL;
    int msg_len = 0;
    struct LocalInterface* local_if = NULL;

    if ((sys = system_get_instance()) == NULL)
        return;

    LIST_FOREACH(local_if, &(MLACP(csm).lif_list), mlacp_next)
    {
        if (local_if->type == IF_T_PORT_CHANNEL)
        {
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
            msg_len = mlacp_prepare_for_Aggport_config(csm, g_csm_buf, CSM_BUFFER_SIZE, local_if, 0);
            iccp_csm_send(csm, g_csm_buf, msg_len);
            local_if->port_config_sync = 0;
            /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [SYNC_Send] PortChannel, csm-if-name=[%s], len=[%d]", local_if->name, msg_len);*/
        }
    }

    return;
}

static void mlacp_sync_send_aggState(struct CSM* csm)
{
    struct System* sys = NULL;
    int msg_len = 0;
    struct LocalInterface* local_if = NULL;

    if ((sys = system_get_instance()) == NULL)
        return;

    LIST_FOREACH(local_if, &(MLACP(csm).lif_list), mlacp_next)
    {
        if (local_if->type == IF_T_PORT_CHANNEL)
        {
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
            msg_len = mlacp_prepare_for_Aggport_state(csm, g_csm_buf, CSM_BUFFER_SIZE, local_if);
            iccp_csm_send(csm, g_csm_buf, msg_len);
            local_if->changed = 0;
            /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [SYNC_Send] PortChannel, csm-if-name=[%s], len=[%d]", local_if->name, msg_len);*/
        }
    }

    return;
}
#define MAX_MAC_ENTRY_NUM 30
#define MAX_NEIGH_ENTRY_NUM 40
static void mlacp_sync_send_syncMacInfo(struct CSM* csm)
{
    int msg_len = 0;
    struct Msg* msg = NULL;
    int count = 0;

    memset(g_csm_buf, 0, CSM_BUFFER_SIZE);

    while (!TAILQ_EMPTY(&(MLACP(csm).mac_msg_list)))
    {
        msg = TAILQ_FIRST(&(MLACP(csm).mac_msg_list));
        TAILQ_REMOVE(&(MLACP(csm).mac_msg_list), msg, tail);
        msg_len = mlacp_prepare_for_mac_info_to_peer(csm, g_csm_buf, CSM_BUFFER_SIZE, (struct MACMsg*)msg->buf, count);
        count++;
        free(msg->buf);
        free(msg);
        if (count >= MAX_MAC_ENTRY_NUM)
        {
            iccp_csm_send(csm, g_csm_buf, msg_len);
            count = 0;
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        }
        /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [SYNC_Send] MacInfo,len=[%d]", msg_len);*/
    }

    if (count)
        iccp_csm_send(csm, g_csm_buf, msg_len);

    return;
}

static void mlacp_sync_send_syncArpInfo(struct CSM* csm)
{
    int msg_len = 0;
    struct Msg* msg = NULL;
    int count = 0;

    memset(g_csm_buf, 0, CSM_BUFFER_SIZE);

    while (!TAILQ_EMPTY(&(MLACP(csm).arp_msg_list)))
    {
        msg = TAILQ_FIRST(&(MLACP(csm).arp_msg_list));
        TAILQ_REMOVE(&(MLACP(csm).arp_msg_list), msg, tail);

        msg_len = mlacp_prepare_for_arp_info(csm, g_csm_buf, CSM_BUFFER_SIZE, (struct ARPMsg*)msg->buf, count);
        count++;
        free(msg->buf);
        free(msg);
        if (count >= MAX_NEIGH_ENTRY_NUM)
        {
            iccp_csm_send(csm, g_csm_buf, msg_len);
            count = 0;
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        }
        /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [SYNC_Send] ArpInfo,len=[%d]", msg_len);*/
    }

    if (count)
        iccp_csm_send(csm, g_csm_buf, msg_len);

    return;
}

static void mlacp_sync_send_syncNdiscInfo(struct CSM *csm)
{
    int msg_len = 0;
    struct Msg *msg = NULL;
    int count = 0;

    memset(g_csm_buf, 0, CSM_BUFFER_SIZE);

    while (!TAILQ_EMPTY(&(MLACP(csm).ndisc_msg_list)))
    {
        msg = TAILQ_FIRST(&(MLACP(csm).ndisc_msg_list));
        TAILQ_REMOVE(&(MLACP(csm).ndisc_msg_list), msg, tail);

        msg_len = mlacp_prepare_for_ndisc_info(csm, g_csm_buf, CSM_BUFFER_SIZE, (struct NDISCMsg *)msg->buf, count);
        count++;
        free(msg->buf);
        free(msg);
        if (count >= MAX_NEIGH_ENTRY_NUM)
        {
            iccp_csm_send(csm, g_csm_buf, msg_len);
            count = 0;
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        }
        /* ICCPD_LOG_DEBUG("mlacp_fsm", " [SYNC_Send] NDInfo,len=[%d]", msg_len); */
    }

    if (count)
        iccp_csm_send(csm, g_csm_buf, msg_len);

    return;
}
static void mlacp_sync_send_syncPortChannelInfo(struct CSM* csm)
{
    struct System* sys = NULL;
    int msg_len = 0;
    struct LocalInterface* local_if = NULL;

    if ((sys = system_get_instance()) == NULL)
        return;

    LIST_FOREACH(local_if, &(MLACP(csm).lif_list), mlacp_next)
    {
        if (local_if->type == IF_T_PORT_CHANNEL)
        {
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
            msg_len = mlacp_prepare_for_port_channel_info(csm, g_csm_buf, CSM_BUFFER_SIZE, local_if);
            iccp_csm_send(csm, g_csm_buf, msg_len);
            local_if->changed = 0;
            /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [SYNC_Send] PortChannel, csm-if-name=[%s], len=[%d]", local_if->name, msg_len);*/
        }
    }

    return;
}

static void mlacp_sync_send_syncPeerLinkInfo(struct CSM* csm)
{
    struct System* sys = NULL;
    int msg_len = 0;

    if ((sys = system_get_instance()) == NULL)
        return;

    if (csm->peer_link_if)
    {
        memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        msg_len = mlacp_prepare_for_port_peerlink_info(csm, g_csm_buf, CSM_BUFFER_SIZE, csm->peer_link_if);
        iccp_csm_send(csm, g_csm_buf, msg_len);
    }

    return;
}

static void mlacp_sync_send_heartbeat(struct CSM* csm)
{
    int msg_len = 0;

    if ((csm->heartbeat_send_time == 0) ||
        ((time(NULL) - csm->heartbeat_send_time) > 1))
    {
        memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        msg_len = mlacp_prepare_for_heartbeat(csm, g_csm_buf, CSM_BUFFER_SIZE);
        iccp_csm_send(csm, g_csm_buf, msg_len);
        time(&csm->heartbeat_send_time);
    }

    return;
}

static void mlacp_sync_send_syncDoneData(struct CSM* csm)
{
    int msg_len = 0;

    /*Sync done & go to next stage*/
    MLACP(csm).wait_for_sync_data = 0;
    memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
    msg_len = mlacp_prepare_for_sync_data_tlv(csm, g_csm_buf, CSM_BUFFER_SIZE, 1);
    iccp_csm_send(csm, g_csm_buf, msg_len);
    /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [SYNC_Send] SyncDone, len=[%d]", msg_len);*/

    return;
}

/******************************************************************
 * Sync Receiver APIs
 *
 *****************************************************************/
static void mlacp_sync_recv_sysConf(struct CSM* csm, struct Msg* msg)
{
    mLACPSysConfigTLV* sysconf = NULL;

    sysconf = (mLACPSysConfigTLV*)&(msg->buf[sizeof(ICCHdr)]);

    if (mlacp_fsm_update_system_conf(csm, sysconf) == MCLAG_ERROR)
    {
        /*NOTE: we just change the node ID local side without sending NAK msg*/
        ICCPD_LOG_WARN(__FUNCTION__, "Same Node ID = %d, send NAK", MLACP(csm).remote_system.node_id);
        mlacp_sync_send_nak_handler(csm, msg);
    }

    return;
}

static void mlacp_sync_recv_portConf(struct CSM* csm, struct Msg* msg)
{
    /*Don't support currently*/
    return;
}

static void mlacp_sync_recv_portPrio(struct CSM* csm, struct Msg* msg)
{
    /*Don't support currently*/
    return;
}

static void mlacp_sync_recv_portState(struct CSM* csm, struct Msg* msg)
{
    /*Don't support currently*/
    return;
}

static void mlacp_sync_recv_aggConf(struct CSM* csm, struct Msg* msg)
{
    mLACPAggConfigTLV* portconf = NULL;

    portconf = (mLACPAggConfigTLV*)&(msg->buf[sizeof(ICCHdr)]);
    if (mlacp_fsm_update_Agg_conf(csm, portconf) == MCLAG_ERROR)
    {
        mlacp_sync_send_nak_handler(csm, msg);
    }

    return;
}

static void mlacp_sync_recv_aggState(struct CSM* csm, struct Msg* msg)
{
    mLACPAggPortStateTLV* portstate = NULL;

    portstate = (mLACPAggPortStateTLV*)&(msg->buf[sizeof(ICCHdr)]);
    if (mlacp_fsm_update_Aggport_state(csm, portstate) == MCLAG_ERROR)
    {
        mlacp_sync_send_nak_handler(csm, msg);
        /*MLACP(csm).error_msg = "Receive a port state update on an non-existed port. It is suggest to check the environment and re-initialize mLACP again.";*/
        return;
    }

    return;
}

static void mlacp_sync_recv_syncData(struct CSM* csm, struct Msg* msg)
{
    mLACPSyncDataTLV* syncdata = NULL;

    syncdata = (mLACPSyncDataTLV*)&(msg->buf[sizeof(ICCHdr)]);
    if (ntohs(syncdata->flags) == 1)
    {
        /* Sync done*/
        MLACP(csm).wait_for_sync_data = 0;
    }

    return;
}

static void mlacp_sync_recv_syncReq(struct CSM* csm, struct Msg* msg)
{
    mLACPSyncReqTLV* mlacp_sync_req = NULL;

    mlacp_sync_req = (mLACPSyncReqTLV*)&msg->buf[sizeof(ICCHdr)];
    MLACP(csm).sync_req_num = ntohs(mlacp_sync_req->req_num);

    /* Reply the peer all sync info*/
    mlacp_sync_send_all_info_handler(csm);

    return;
}

static void mlacp_sync_recv_portChanInfo(struct CSM* csm, struct Msg* msg)
{
    mLACPPortChannelInfoTLV* portconf = NULL;

    portconf = (mLACPPortChannelInfoTLV*)&(msg->buf[sizeof(ICCHdr)]);
    if (mlacp_fsm_update_port_channel_info(csm, portconf) == MCLAG_ERROR)
    {
        mlacp_sync_send_nak_handler(csm, msg);
    }

    return;
}

static void mlacp_sync_recv_peerLlinkInfo(struct CSM* csm, struct Msg* msg)
{
    mLACPPeerLinkInfoTLV* peerlink = NULL;

    peerlink = (mLACPPeerLinkInfoTLV*)&(msg->buf[sizeof(ICCHdr)]);
    mlacp_fsm_update_peerlink_info( csm, peerlink);

    return;
}

static void mlacp_sync_recv_macInfo(struct CSM* csm, struct Msg* msg)
{
    struct mLACPMACInfoTLV* mac_info = NULL;

    mac_info = (struct mLACPMACInfoTLV *)&(msg->buf[sizeof(ICCHdr)]);
    mlacp_fsm_update_mac_info_from_peer(csm, mac_info);

    return;
}

static void mlacp_sync_recv_arpInfo(struct CSM* csm, struct Msg* msg)
{
    struct mLACPARPInfoTLV* arp_info = NULL;

    arp_info = (struct mLACPARPInfoTLV *)&(msg->buf[sizeof(ICCHdr)]);
    mlacp_fsm_update_arp_info(csm, arp_info);

    return;
}

static void mlacp_sync_recv_ndiscInfo(struct CSM *csm, struct Msg *msg)
{
    struct mLACPNDISCInfoTLV *ndisc_info = NULL;

    ndisc_info = (struct mLACPNDISCInfoTLV *)&(msg->buf[sizeof(ICCHdr)]);
    mlacp_fsm_update_ndisc_info(csm, ndisc_info);

    return;
}
static void mlacp_sync_recv_stpInfo(struct CSM* csm, struct Msg* msg)
{
    /*Don't support currently*/
    return;
}

static void mlacp_sync_recv_heartbeat(struct CSM* csm, struct Msg* msg)
{
    struct mLACPHeartbeatTLV *tlv = NULL;

    tlv = (struct mLACPHeartbeatTLV *)(&msg->buf[sizeof(ICCHdr)]);
    mlacp_fsm_update_heartbeat(csm, tlv);

    return;
}

static void mlacp_sync_recv_warmboot(struct CSM* csm, struct Msg* msg)
{
    struct mLACPWarmbootTLV *tlv = NULL;

    tlv = (struct mLACPWarmbootTLV *)(&msg->buf[sizeof(ICCHdr)]);
    mlacp_fsm_update_warmboot(csm, tlv);

    return;
}

/*****************************************
* MLACP Init
*
* ***************************************/
void mlacp_init(struct CSM* csm, int all)
{
    if (csm == NULL)
        return;

    MLACP(csm).sync_req_num = -1;
    MLACP(csm).need_to_sync = 0;
    MLACP(csm).error_msg = NULL;

    MLACP(csm).current_state = MLACP_STATE_INIT;
    memset(MLACP(csm).remote_system.system_id, 0, ETHER_ADDR_LEN);

    MLACP_MSG_QUEUE_REINIT(MLACP(csm).mlacp_msg_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).arp_msg_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).ndisc_msg_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).mac_msg_list);
    PIF_QUEUE_REINIT(MLACP(csm).pif_list);
    LIF_PURGE_QUEUE_REINIT(MLACP(csm).lif_purge_list);

    if (all != 0)
    {
        /* if no clean all, keep the arp info & local interface info for next connection*/
        MLACP_MSG_QUEUE_REINIT(MLACP(csm).arp_list);
        MLACP_MSG_QUEUE_REINIT(MLACP(csm).ndisc_list);
        MLACP_MSG_QUEUE_REINIT(MLACP(csm).mac_list);
        LIF_QUEUE_REINIT(MLACP(csm).lif_list);

        MLACP(csm).node_id = MLACP_SYSCONF_NODEID_MSB_MASK;
        MLACP(csm).node_id |= (((inet_addr(csm->sender_ip) >> 24) << 4) & MLACP_SYSCONF_NODEID_NODEID_MASK);
        MLACP(csm).node_id |= rand() % MLACP_SYSCONF_NODEID_FREE_MASK;
    }

    return;
}

/*****************************************
* MLACP finalize
*
* ***************************************/
void mlacp_finalize(struct CSM* csm)
{
    if (csm == NULL)
        return;

    /* msg destroy*/
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).mlacp_msg_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).arp_msg_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).ndisc_msg_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).mac_msg_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).arp_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).ndisc_list);
    MLACP_MSG_QUEUE_REINIT(MLACP(csm).mac_list);

    /* remove lif & lif-purge queue */
    LIF_QUEUE_REINIT(MLACP(csm).lif_list);
    LIF_PURGE_QUEUE_REINIT(MLACP(csm).lif_purge_list);
    /* remove & destroy pif queue */
    PIF_QUEUE_REINIT(MLACP(csm).pif_list);

    return;
}

/*****************************************
* MLACP FSM Transit
*
* ***************************************/
void mlacp_fsm_transit(struct CSM* csm)
{
    struct System* sys = NULL;
    struct Msg* msg = NULL;
    static MLACP_APP_STATE_E prev_state = MLACP_SYNC_SYSCONF;
    ICCHdr* icc_hdr = NULL;
    ICCParameter* icc_param = NULL;
    int have_msg = 1;

    if (csm == NULL)
        return;
    if ((sys = system_get_instance()) == NULL)
        return;

    /* torn down event */
    if (csm->sock_fd <= 0 || csm->app_csm.current_state != APP_OPERATIONAL)
    {
        /* drop all legacy mlacp msg*/
        if (MLACP(csm).current_state != MLACP_STATE_INIT)
        {
            MLACP_MSG_QUEUE_REINIT(MLACP(csm).mlacp_msg_list);
            MLACP_MSG_QUEUE_REINIT(MLACP(csm).arp_msg_list);
            MLACP_MSG_QUEUE_REINIT(MLACP(csm).ndisc_msg_list);
            MLACP_MSG_QUEUE_REINIT(MLACP(csm).mac_msg_list);
            MLACP(csm).current_state = MLACP_STATE_INIT;
        }
        return;
    }

    if (csm->warm_reboot_disconn_time != 0)
    {
        /*After peer warm reboot and disconnect, if peer connection is not establised more than 90s, 
           recover peer disconnection to normal process, such as add peer age flag for MACs etc*/
        if ((time(NULL) - csm->warm_reboot_disconn_time) >= WARM_REBOOT_TIMEOUT)
        {
            csm->warm_reboot_disconn_time = 0;
            ICCPD_LOG_NOTICE(__FUNCTION__, "Peer warm reboot, reconnection timeout, recover to normal reboot!");
            mlacp_peer_disconn_handler(csm);
        }
    }

    mlacp_sync_send_heartbeat(csm);

    /* Dequeue msg if any*/
    while (have_msg)
    {
        if (MLACP(csm).current_state != MLACP_STATE_INIT)
        {
            /* Handler NAK First*/
            msg = mlacp_dequeue_msg(csm);
            if (msg != NULL)
            {
                have_msg = 1;
                icc_hdr = (ICCHdr*)msg->buf;
                icc_param = (ICCParameter*)&msg->buf[sizeof(ICCHdr)];
                /*ICCPD_LOG_DEBUG("mlacp_fsm", "  SYNC: Message Type = %X, TLV=%s, Len=%d", icc_hdr->ldp_hdr.msg_type, get_tlv_type_string(icc_param->type), msg->len);*/

                if (icc_hdr->ldp_hdr.msg_type == MSG_T_NOTIFICATION && icc_param->type == TLV_T_NAK)
                {
                    mlacp_sync_recv_nak_handler(csm, msg);
                    free(msg->buf);
                    free(msg);
                    continue;
                }
            }
            else
            {
                have_msg = 0;
            }
        }

        if (prev_state != MLACP(csm).current_state)
        {
            if (MLACP(csm).current_state == MLACP_STATE_EXCHANGE)
                mlacp_peer_conn_handler(csm);
            prev_state = MLACP(csm).current_state;
        }

        /* Sync State */
        if (MLACP(csm).current_state == MLACP_STATE_INIT)
        {
            MLACP(csm).wait_for_sync_data = 0;
            MLACP(csm).current_state = MLACP_STATE_STAGE1;
            mlacp_resync_arp(csm);
            mlacp_resync_ndisc(csm);
        }

        switch (MLACP(csm).current_state)
        {
            case MLACP_STATE_INIT:
            case MLACP_STATE_ERROR:
                /* should not be here*/
                break;

            case MLACP_STATE_STAGE1:
            case MLACP_STATE_STAGE2:
                mlacp_stage_handler(csm, msg);
                break;

            case MLACP_STATE_EXCHANGE:
                mlacp_exchange_handler(csm, msg);
                break;
        }

        /*ICCPD_LOG_DEBUG("mlacp_fsm", "  Next State = %s", mlacp_state(csm));*/
        if (msg)
        {
            free(msg->buf);
            free(msg);
        }
    }
}

/* Helper function for dumping application state machine */
static char* mlacp_state(struct CSM* csm)
{
    if (csm == NULL )
        return "MLACP_NULL";

    switch (MLACP(csm).current_state)
    {
        case MLACP_STATE_INIT:
            return "MLACP_STATE_INIT";

        case MLACP_STATE_STAGE1:
            return "MLACP_STATE_STAGE1";

        case MLACP_STATE_STAGE2:
            return "MLACP_STATE_STAGE2";

        case MLACP_STATE_EXCHANGE:
            return "MLACP_STATE_EXCHANGE";

        case MLACP_STATE_ERROR:
            return "MLACP_STATE_ERROR";
    }

    return "MLACP_UNKNOWN";
}

/* Add received message into message list */
void mlacp_enqueue_msg(struct CSM* csm, struct Msg* msg)
{
    if (csm == NULL )
    {
        if (msg != NULL )
            free(msg);
        return;
    }

    if (msg == NULL )
        return;

    #if 0
    icc_hdr = (ICCHdr*)msg->buf;
    icc_param = (ICCParameter*)&msg->buf[sizeof(ICCHdr)];
    ICCPD_LOG_DEBUG("mlacp_fsm", "  mLACP enqueue: tlv = 0x%04x", icc_param->type);
    #endif

    TAILQ_INSERT_TAIL(&(MLACP(csm).mlacp_msg_list), msg, tail);

    return;
}

/* Get received message from message list */
struct Msg* mlacp_dequeue_msg(struct CSM* csm)
{
    struct Msg* msg = NULL;

    if (!TAILQ_EMPTY(&(MLACP(csm).mlacp_msg_list)))
    {
        msg = TAILQ_FIRST(&(MLACP(csm).mlacp_msg_list));
        TAILQ_REMOVE(&(MLACP(csm).mlacp_msg_list), msg, tail);
    }

    return msg;
}

/******************************************
* When peerlink ready, prepare the MACMsg
*
******************************************/
static void mlacp_resync_mac(struct CSM* csm)
{
    struct Msg* msg = NULL;
    struct MACMsg* mac_msg = NULL;
    struct Msg *msg_send = NULL;

    /* recover MAC info sync from peer*/
    if (!TAILQ_EMPTY(&(MLACP(csm).mac_list)))
    {
        TAILQ_FOREACH(msg, &MLACP(csm).mac_list, tail)
        {
            mac_msg = (struct MACMsg*)msg->buf;
            mac_msg->op_type = MAC_SYNC_ADD;
            if (iccp_csm_init_msg(&msg_send, (char*)mac_msg, sizeof(struct MACMsg)) == 0)
            {
                mac_msg->age_flag &= ~MAC_AGE_PEER;
                TAILQ_INSERT_TAIL(&(MLACP(csm).mac_msg_list), msg_send, tail);
                ICCPD_LOG_DEBUG(__FUNCTION__, "MAC-msg-list enqueue: %s, add %s vlan-id %d, age_flag %d",
                                mac_msg->ifname, mac_msg->mac_str, mac_msg->vid, mac_msg->age_flag);
            }
        }
    }
}

/******************************************
* When peerlink ready, prepare the ARPMsg
*
******************************************/
static void mlacp_resync_arp(struct CSM* csm)
{
    struct Msg* msg = NULL;
    struct ARPMsg* arp_msg = NULL;
    struct Msg *msg_send = NULL;

    /* recover ARP info sync from peer*/
    if (!TAILQ_EMPTY(&(MLACP(csm).arp_list)))
    {
        TAILQ_FOREACH(msg, &MLACP(csm).arp_list, tail)
        {
            arp_msg = (struct ARPMsg*)msg->buf;
            arp_msg->op_type = NEIGH_SYNC_ADD;
            if (iccp_csm_init_msg(&msg_send, (char*)arp_msg, sizeof(struct ARPMsg)) == 0)
            {
                TAILQ_INSERT_TAIL(&(MLACP(csm).arp_msg_list), msg_send, tail);
            }
        }
    }
}

/******************************************
* When peerlink ready, prepare the NDISCMsg
*
******************************************/
static void mlacp_resync_ndisc(struct CSM *csm)
{
    struct Msg *msg = NULL;
    struct NDISCMsg *ndisc_msg = NULL;
    struct Msg *msg_send = NULL;

    /* recover ndisc info sync from peer */
    if (!TAILQ_EMPTY(&(MLACP(csm).ndisc_list)))
    {
        TAILQ_FOREACH(msg, &MLACP(csm).ndisc_list, tail)
        {
            ndisc_msg = (struct NDISCMsg *)msg->buf;
            ndisc_msg->op_type = NEIGH_SYNC_ADD;
            if (iccp_csm_init_msg(&msg_send, (char *)ndisc_msg, sizeof(struct NDISCMsg)) == 0)
            {
                TAILQ_INSERT_TAIL(&(MLACP(csm).ndisc_msg_list), msg_send, tail);
            }
        }
    }
}

/*****************************************
* NAK handler
*
* ***************************************/
static void mlacp_sync_send_nak_handler(struct CSM* csm,  struct Msg* msg)
{
    int msg_len;
    ICCHdr* icc_hdr = NULL;

    icc_hdr = (ICCHdr*)msg->buf;

    ICCPD_LOG_WARN(__FUNCTION__, "Send NAK");

    memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
    csm->app_csm.invalid_msg_id = ntohl(icc_hdr->ldp_hdr.msg_id);
    msg_len = app_csm_prepare_nak_msg(csm, g_csm_buf, CSM_BUFFER_SIZE);
    iccp_csm_send(csm, g_csm_buf, msg_len);
}

static void mlacp_sync_recv_nak_handler(struct CSM* csm,  struct Msg* msg)
{
    NAKTLV* naktlv = NULL;
    uint16_t tlvType = -1;
    int i;

    ICCPD_LOG_WARN(__FUNCTION__, "Receive NAK ");

    /* Dequeuq NAK*/
    naktlv = (NAKTLV*)&msg->buf[sizeof(ICCHdr)];

    /* Check NAK Type*/
    for (i = 0; i < MAX_MSG_LOG_SIZE; ++i)
    {
        if (ntohl(naktlv->rejected_msg_id) == csm->msg_log.msg[i].msg_id)
        {
            tlvType = csm->msg_log.msg[i].tlv;
            break;
        }
    }

    if (tlvType)
    {
        switch (tlvType)
        {
            case TLV_T_MLACP_SYSTEM_CONFIG:
                MLACP(csm).node_id--;
                MLACP(csm).system_config_changed = 1;
                ICCPD_LOG_WARN(__FUNCTION__, "[%X] change NodeID as %d", tlvType & 0x00FF, MLACP(csm).node_id);
                break;

            default:
                ICCPD_LOG_WARN(__FUNCTION__, "    [%X]", tlvType & 0x00FF);
                MLACP(csm).need_to_sync = 1;
                break;
        }
    }
    else
    {
        ICCPD_LOG_WARN(__FUNCTION__, "Unknow NAK");
        MLACP(csm).need_to_sync = 1;
    }

    return;
}

/*****************************************
* MLACP sync receiver
*
* ***************************************/
static void mlacp_sync_receiver_handler(struct CSM* csm, struct Msg* msg)
{
    ICCParameter *icc_param;

    /* No receive message...*/
    if (!csm || !msg)
        return;

    icc_param = (ICCParameter*)&(msg->buf[sizeof(ICCHdr)]);

    /*fprintf(stderr, " Recv Type [%d]\n", icc_param->type);*/
    switch (icc_param->type)
    {
        case TLV_T_MLACP_SYSTEM_CONFIG:
            mlacp_sync_recv_sysConf(csm, msg);
            break;

        case TLV_T_MLACP_PORT_CONFIG:
            mlacp_sync_recv_portConf(csm, msg);
            break;

        case TLV_T_MLACP_PORT_PRIORITY:
            mlacp_sync_recv_portPrio(csm, msg);
            break;

        case TLV_T_MLACP_PORT_STATE:
            mlacp_sync_recv_portState(csm, msg);
            break;

        case TLV_T_MLACP_AGGREGATOR_CONFIG:
            /* The following line will be uncommented when Aggregator related structures are supported. */
            mlacp_sync_recv_aggConf(csm, msg);
            break;

        case TLV_T_MLACP_AGGREGATOR_STATE:
            mlacp_sync_recv_aggState(csm, msg);
            break;

        case TLV_T_MLACP_SYNC_DATA:
            mlacp_sync_recv_syncData(csm, msg);
            break;

        case TLV_T_MLACP_SYNC_REQUEST:
            mlacp_sync_recv_syncReq(csm, msg);
            break;

        case TLV_T_MLACP_PORT_CHANNEL_INFO:
            mlacp_sync_recv_portChanInfo(csm, msg);
            break;

        case TLV_T_MLACP_PEERLINK_INFO:
            mlacp_sync_recv_peerLlinkInfo(csm, msg);
            break;

        case TLV_T_MLACP_MAC_INFO:
            mlacp_sync_recv_macInfo(csm, msg);
            break;

        case TLV_T_MLACP_ARP_INFO:
            mlacp_sync_recv_arpInfo(csm, msg);
            break;

        case TLV_T_MLACP_NDISC_INFO:
            mlacp_sync_recv_ndiscInfo(csm, msg);
            break;

        case TLV_T_MLACP_STP_INFO:
            mlacp_sync_recv_stpInfo(csm, msg);
            break;

        case TLV_T_MLACP_HEARTBEAT:
            mlacp_sync_recv_heartbeat(csm, msg);
            break;

        case TLV_T_MLACP_WARMBOOT_FLAG:
            mlacp_sync_recv_warmboot(csm, msg);
            break;
    }

    /*ICCPD_LOG_DEBUG("mlacp_fsm", "  [Sync Recv] %s... DONE", get_tlv_type_string(icc_param->type));*/

    return;
}

/*****************************************
* MLACP sync sender
*
* ***************************************/
static void mlacp_sync_sender_handler(struct CSM* csm)
{
    switch (MLACP(csm).sync_state)
    {
        case MLACP_SYNC_SYSCONF:
            mlacp_sync_send_sysConf(csm);
            break;

        case MLACP_SYNC_AGGCONF:
            /* Do nothing due to no support in this version. */
            mlacp_sync_send_aggConf(csm);
            break;

        case MLACP_SYNC_AGGSTATE:
            /* Do nothing due to no support in this version. */
            mlacp_sync_send_aggState(csm);
            break;

        case MLACP_SYNC_AGGINFO:
            mlacp_sync_send_syncPortChannelInfo(csm);
            break;

        case MLACP_SYNC_PEERLINKINFO:
            mlacp_sync_send_syncPeerLinkInfo(csm);
            break;

        case MLACP_SYNC_ARP_INFO:
            mlacp_sync_send_syncArpInfo(csm);
            break;

        case MLACP_SYNC_NDISC_INFO:
            mlacp_sync_send_syncNdiscInfo(csm);
            break;

        case MLACP_SYNC_DONE:
            mlacp_sync_send_syncDoneData(csm);
            break;

        default:
            break;
    }

    return;
}

static void mlacp_sync_send_all_info_handler(struct CSM* csm)
{
    size_t len = 0;

    /* Prepare for sync start reply*/
    memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
    len = mlacp_prepare_for_sync_data_tlv(csm, g_csm_buf, CSM_BUFFER_SIZE, 0);
    iccp_csm_send(csm, g_csm_buf, len);

    MLACP(csm).sync_state = MLACP_SYNC_SYSCONF;

    while (1)
    {
        mlacp_sync_sender_handler(csm);
        if (MLACP(csm).sync_state != MLACP_SYNC_DONE)
        {
            MLACP(csm).sync_state++;
        }
        else
        {
            /*Next stage*/
            MLACP(csm).wait_for_sync_data = 0;
            MLACP(csm).current_state++;
            break;
        }
    }

    return;
}

static void mlacp_stage_sync_send_handler(struct CSM* csm, struct Msg* msg)
{
    ICCHdr* icc_hdr = NULL;
    ICCParameter* icc_param = NULL;
    mLACPSyncReqTLV* mlacp_sync_req = NULL;

    if (MLACP(csm).wait_for_sync_data == 0)
    {
        /* Waiting the peer sync request*/
        if (msg)
        {
            icc_hdr = (ICCHdr*)msg->buf;
            icc_param = (ICCParameter*)&msg->buf[sizeof(ICCHdr)];

            if (icc_hdr->ldp_hdr.msg_type == MSG_T_RG_APP_DATA && icc_param->type == TLV_T_MLACP_SYNC_REQUEST)
            {
                mlacp_sync_req = (mLACPSyncReqTLV*)&msg->buf[sizeof(ICCHdr)];
                MLACP(csm).wait_for_sync_data = 1;
                MLACP(csm).sync_req_num = ntohs(mlacp_sync_req->req_num);

                /* Reply the peer all sync info*/
                mlacp_sync_send_all_info_handler(csm);
            }
        }
    }

    return;
}

static void mlacp_stage_sync_request_handler(struct CSM* csm, struct Msg* msg)
{
    int msg_len = 0;

    /* Socket server send sync request first*/
    if (MLACP(csm).wait_for_sync_data == 0)
    {
        // Send out the request for ALL
        memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        msg_len = mlacp_prepare_for_sync_request_tlv(csm, g_csm_buf, CSM_BUFFER_SIZE);
        iccp_csm_send(csm, g_csm_buf, msg_len);
        MLACP(csm).wait_for_sync_data = 1;
    }
    else
    {
        mlacp_sync_receiver_handler(csm, msg);
        if (MLACP(csm).wait_for_sync_data == 0)
        {
            MLACP(csm).current_state++;
        }
    }

    return;
}

static void mlacp_stage_handler(struct CSM* csm, struct Msg* msg)
{
    if (MLACP(csm).current_state == MLACP_STATE_STAGE1)
    {
        /*Stage 1, role active send info first*/
        if (csm->role_type == STP_ROLE_ACTIVE)
            mlacp_stage_sync_send_handler(csm, msg);
        else
            mlacp_stage_sync_request_handler(csm, msg);
    }
    else
    {
        /*Stage 2, role standby send info*/
        if (csm->role_type == STP_ROLE_ACTIVE)
            mlacp_stage_sync_request_handler(csm, msg);
        else
            mlacp_stage_sync_send_handler(csm, msg);
    }

    return;
}

static void mlacp_exchange_handler(struct CSM* csm, struct Msg* msg)
{
    int len;
    struct System* sys = NULL;
    struct LocalInterface* lif = NULL, *lif_purge = NULL;

    ICCHdr* icc_hdr = NULL;

    if ((sys = system_get_instance()) == NULL)
        return;

    /* update system id*/
    /*update_system_id(csm);*/

    /* Any msg?*/
    if (msg)
    {
        icc_hdr = (ICCHdr*)msg->buf;
        if (icc_hdr->ldp_hdr.msg_type == MSG_T_RG_APP_DATA)
        {
            /* Process receive APP info*/
            mlacp_sync_receiver_handler(csm, msg);
        }
    }

    if (MLACP(csm).need_to_sync != 0)
    {
        /* Send out the request for ALL info*/
        MLACP(csm).need_to_sync = 0;
        memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        len = mlacp_prepare_for_sync_request_tlv(csm, g_csm_buf, CSM_BUFFER_SIZE);
        iccp_csm_send(csm, g_csm_buf, len);
    }

    /* Send system config*/
    if (MLACP(csm).system_config_changed != 0)
    {
        memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        len = mlacp_prepare_for_sys_config(csm, g_csm_buf, CSM_BUFFER_SIZE);
        iccp_csm_send(csm, g_csm_buf, len);

        if (csm->peer_link_if)
        {
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
            len = mlacp_prepare_for_port_peerlink_info(csm, g_csm_buf, CSM_BUFFER_SIZE, csm->peer_link_if);
            iccp_csm_send(csm, g_csm_buf, len);
        }

        MLACP(csm).system_config_changed = 0;
    }

    /* Send mlag purge lif*/
    LIST_FOREACH(lif_purge, &(MLACP(csm).lif_purge_list), mlacp_purge_next)
    {
        /* Purge info*/
        memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
        len = mlacp_prepare_for_Aggport_config(csm, g_csm_buf, CSM_BUFFER_SIZE, lif_purge, 1);
        iccp_csm_send(csm, g_csm_buf, len);
        /* Destroy old interface*/
        if (lif_purge != NULL)
            LIST_REMOVE(lif_purge, mlacp_purge_next);
    }

    /* Send mlag lif*/
    LIST_FOREACH(lif, &(MLACP(csm).lif_list), mlacp_next)
    {
        if (lif->type == IF_T_PORT_CHANNEL && lif->port_config_sync)
        {
            /* Send port channel information*/
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
            len = mlacp_prepare_for_Aggport_config(csm, g_csm_buf, CSM_BUFFER_SIZE, lif, 0);
            iccp_csm_send(csm, g_csm_buf, len);

            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
            len = mlacp_prepare_for_port_channel_info(csm, g_csm_buf, CSM_BUFFER_SIZE, lif);
            iccp_csm_send(csm, g_csm_buf, len);

            lif->port_config_sync = 0;
        }

        /*send if portchannel state change */
        if (lif->type == IF_T_PORT_CHANNEL && lif->changed)
        {
            /* Send port channel state information*/
            memset(g_csm_buf, 0, CSM_BUFFER_SIZE);
            len = mlacp_prepare_for_Aggport_state(csm, g_csm_buf, CSM_BUFFER_SIZE, lif);
            iccp_csm_send(csm, g_csm_buf, len);
            lif->changed = 0;
        }
    }

    /* Send MAC info if any*/
    mlacp_sync_send_syncMacInfo(csm);

    /* Send ARP info if any*/
    mlacp_sync_send_syncArpInfo(csm);

    /* Send Ndisc info if any */
    mlacp_sync_send_syncNdiscInfo(csm);

    /*If peer is warm reboot*/
    if (csm->peer_warm_reboot_time != 0)
    {
        /*Peer warm reboot timeout(connection is not broken more than 90s), recover to normal reboot*/
        if ((time(NULL) - csm->peer_warm_reboot_time) >= WARM_REBOOT_TIMEOUT)
        {
            csm->peer_warm_reboot_time = 0;
            ICCPD_LOG_NOTICE(__FUNCTION__, "Peer warm reboot timeout, recover to normal reboot!");
        }
    }

    return;
}
