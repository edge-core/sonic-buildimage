/*
 * mlacp_link_handler.h
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

#ifndef __MLACP_LINK_HANDLER__
#define __MLACP_LINK_HANDLER__

#include "../include/iccp_csm.h"
#include "../include/mlacp_tlv.h"

/*****************************************
* Link Handler
*
* ***************************************/
void mlacp_portchannel_state_handler(struct CSM* csm, struct LocalInterface* local_if, int po_state);
void mlacp_peer_conn_handler(struct CSM* csm);
void mlacp_peer_disconn_handler(struct CSM* csm);
void mlacp_peerlink_up_handler(struct CSM* csm);
void mlacp_peerlink_down_handler(struct CSM* csm);
void update_stp_peer_link(struct CSM *csm, struct PeerInterface *peer_if, int po_state, int new_create);
void update_peerlink_isolate_from_pif(struct CSM *csm, struct PeerInterface *pif, int po_state, int new_create);
void mlacp_mlag_link_add_handler(struct CSM *csm, struct LocalInterface *lif);
void mlacp_mlag_link_del_handler(struct CSM *csm, struct LocalInterface *lif);
void set_peerlink_mlag_port_learn(struct LocalInterface *lif, int enable);
void peerlink_port_isolate_cleanup(struct CSM* csm);
void update_peerlink_isolate_from_all_csm_lif(struct CSM* csm);

void del_mac_from_chip(struct MACMsg *mac_msg);
void add_mac_to_chip(struct MACMsg *mac_msg, uint8_t mac_type);
uint8_t set_mac_local_age_flag(struct CSM *csm, struct MACMsg *mac_msg, uint8_t set);
void iccp_get_fdb_change_from_syncd(void);

extern int mclagd_ctl_sock_create();
extern int mclagd_ctl_sock_accept(int fd);
extern int mclagd_ctl_interactive_process(int client_fd);
extern int parseMacString(const char *str_mac, uint8_t *bin_mac);
char *show_ip_str(uint32_t ipv4_addr);
char *show_ipv6_str(char *ipv6_addr);

void syncd_info_close();
int iccp_connect_syncd();
#endif
