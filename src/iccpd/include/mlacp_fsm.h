/*
 *  mlacp_fsm.h
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

#ifndef _MLACP_FSM_H
#define _MLACP_FSM_H

#include "../include/port.h"

#define MLCAP_SYNC_PHY_DEV_SEC     1     /*every 1 sec*/

#define MLACP(csm_ptr)  (csm_ptr->app_csm.mlacp)

struct CSM;

enum MLACP_APP_STATE
{
    MLACP_STATE_INIT,
    MLACP_STATE_STAGE1,
    MLACP_STATE_STAGE2,
    MLACP_STATE_EXCHANGE,
    MLACP_STATE_ERROR,
};

typedef enum MLACP_APP_STATE MLACP_APP_STATE_E;

/* for sender only*/
enum MLACP_SYNC_STATE
{
    MLACP_SYNC_SYSCONF=0,
    MLACP_SYNC_AGGCONF,
    MLACP_SYNC_AGGSTATE,
    MLACP_SYNC_AGGINFO,
    MLACP_SYNC_PEERLINKINFO,
    MLACP_SYNC_ARP_INFO,
    MLACP_SYNC_NDISC_INFO,
    MLACP_SYNC_DONE,
};

typedef enum MLACP_SYNC_STATE MLACP_SYNC_STATE_E;

struct Remote_System
{
    uint8_t system_id[ETHER_ADDR_LEN];
    uint16_t system_priority;
    uint32_t node_id;
};

struct mLACP
{
    int id;
    int sync_req_num;

    MLACP_APP_STATE_E current_state;
    MLACP_SYNC_STATE_E sync_state;

    uint8_t wait_for_sync_data;
    uint8_t need_to_sync;
    uint8_t node_id;
    uint8_t system_id[ETHER_ADDR_LEN];
    uint16_t system_priority;
    uint8_t system_config_changed;

    struct Remote_System remote_system;
    const char* error_msg;
    TAILQ_HEAD(mlacp_msg_list, Msg) mlacp_msg_list;
    TAILQ_HEAD(arp_msg_list, Msg) arp_msg_list;
    TAILQ_HEAD(arp_info_list, Msg) arp_list;
    TAILQ_HEAD(ndisc_msg_list, Msg) ndisc_msg_list;
    TAILQ_HEAD(ndisc_info_list, Msg) ndisc_list;
    TAILQ_HEAD(mac_msg_list, Msg) mac_msg_list;
    TAILQ_HEAD(mac_info_list, Msg) mac_list;

    LIST_HEAD(lif_list, LocalInterface) lif_list;
    LIST_HEAD(lif_purge_list, LocalInterface) lif_purge_list;
    LIST_HEAD(pif_list, PeerInterface) pif_list;
};

void mlacp_init(struct CSM* csm, int all);
void mlacp_finalize(struct CSM* csm);
void mlacp_fsm_transit(struct CSM* csm);
void mlacp_enqueue_msg(struct CSM*, struct Msg*);
struct Msg* mlacp_dequeue_msg(struct CSM*);

/* from app_csm*/
extern int mlacp_bind_local_if(struct CSM* csm, struct LocalInterface* local_if);
extern int mlacp_unbind_local_if(struct LocalInterface* local_if);

#endif /* _MLACP_HANDLER_H */
