/* Copyright(c) 2016-2019 Nephos/Estinet.
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

#ifndef ICCP_NETLINK_H
#define ICCP_NETLINK_H
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdarg.h>
#include <unistd.h>
#include <netlink/netlink.h>

#include <linux/types.h>

#include "../include/system.h"
#include "../include/port.h"

int iccp_get_port_member_list(struct LocalInterface* lif);
void iccp_event_handler_obj_input_newlink(struct nl_object *obj, void *arg);
void iccp_event_handler_obj_input_dellink(struct nl_object *obj, void *arg);
int iccp_system_init_netlink_socket();
void iccp_system_dinit_netlink_socket();
int iccp_init_netlink_event_fd(struct System *sys);
int iccp_handle_events(struct System * sys);
void update_if_ipmac_on_standby(struct LocalInterface* lif_po);
int iccp_sys_local_if_list_get_addr();
int iccp_check_if_addr_from_netlink(int family, uint8_t *addr, struct LocalInterface *lif);

#endif

