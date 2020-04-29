/*
 * system.h
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

#ifndef SYSTEM_H_
#define SYSTEM_H_

#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/select.h>

#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

#include <sys/socket.h>

#include "../include/port.h"

#define FRONT_PANEL_PORT_PREFIX "Ethernet"
#define PORTCHANNEL_PREFIX      "PortChannel"
#define VLAN_PREFIX             "Vlan"
#define VXLAN_TUNNEL_PREFIX     "VTTNL"

#define WARM_REBOOT 1

#define MCLAG_ERROR -1

struct CSM;

#ifndef MAX_BUFSIZE
    #define MAX_BUFSIZE 4096
#endif

struct System
{
    int server_fd;/* Peer-Link Socket*/
    int sync_fd;
    int sync_ctrl_fd;
    int arp_receive_fd;
    int ndisc_receive_fd;
    int epoll_fd;

    struct nl_sock * genric_sock;
    int genric_sock_seq;
    int family;
    struct nl_sock * route_sock;
    int route_sock_seq;
    struct nl_sock * genric_event_sock;
    struct nl_sock * route_event_sock;

    int sig_pipe_r;
    int sig_pipe_w;
    int warmboot_start;
    int warmboot_exit;

    /* Info List*/
    LIST_HEAD(csm_list, CSM) csm_list;
    LIST_HEAD(lif_all_list, LocalInterface) lif_list;
    LIST_HEAD(lif_purge_all_list, LocalInterface) lif_purge_list;

    /* Settings */
    char* log_file_path;
    char* cmd_file_path;
    char* config_file_path;
    char* mclagdctl_file_path;
    int pid_file_fd;
    int telnet_port;
    fd_set readfd; /*record socket need to listen*/
    int readfd_count;
    time_t csm_trans_time;
    int need_sync_team_again;
    int need_sync_netlink_again;
};

struct CSM* system_create_csm();
struct CSM* system_get_csm_by_peer_ip(const char*);
struct CSM* system_get_csm_by_mlacp_id(int id);
struct System* system_get_instance();
void system_finalize();
void system_init(struct System*);

#endif /* SYSTEM_H_ */
