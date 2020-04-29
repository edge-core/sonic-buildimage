/*
 * system.c
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

#include "../include/iccp_csm.h"
#include "../include/logger.h"
#include "../include/iccp_netlink.h"
#include "../include/scheduler.h"

/* Singleton */
struct System* system_get_instance()
{
    static struct System* sys = NULL;

    if (sys == NULL )
    {
        sys = (struct System*)malloc(sizeof(struct System));
        if (sys == NULL )
        {
            ICCPD_LOG_WARN(__FUNCTION__, "Failed to obtain system instance.");
            return NULL;
        }
        system_init(sys);
    }

    return sys;
}

/* System instance initialization */
void system_init(struct System* sys)
{
    if (sys == NULL )
        return;

    sys->server_fd = -1;
    sys->sync_fd = -1;
    sys->sync_ctrl_fd = -1;
    sys->arp_receive_fd = -1;
    sys->ndisc_receive_fd = -1;
    sys->epoll_fd = -1;
    sys->family = -1;
    sys->warmboot_start = 0;
    sys->warmboot_exit = 0;
    LIST_INIT(&(sys->csm_list));
    LIST_INIT(&(sys->lif_list));
    LIST_INIT(&(sys->lif_purge_list));

    sys->log_file_path = strdup("/var/log/iccpd.log");
    sys->cmd_file_path = strdup("/var/run/iccpd/iccpd.vty");
    sys->config_file_path = strdup("/etc/iccpd/iccpd.conf");
    sys->mclagdctl_file_path = strdup("/var/run/iccpd/mclagdctl.sock");
    sys->pid_file_fd = 0;
    sys->telnet_port = 2015;
    FD_ZERO(&(sys->readfd));
    sys->readfd_count = 0;
    sys->csm_trans_time = 0;
    sys->need_sync_team_again = 0;
    sys->need_sync_netlink_again = 0;
    scheduler_server_sock_init();
    iccp_system_init_netlink_socket();
    iccp_init_netlink_event_fd(sys);
}

/* System instance tear down */
void system_finalize()
{
    struct System* sys = NULL;
    struct CSM* csm = NULL;
    struct LocalInterface* local_if = NULL;

    if ((sys = system_get_instance()) == NULL )
        return;

    ICCPD_LOG_INFO(__FUNCTION__, "System resource pool is destructing.");

    while (!LIST_EMPTY(&(sys->csm_list)))
    {
        csm = LIST_FIRST(&(sys->csm_list));
        iccp_csm_finalize(csm);
    }

    /* Release all port objects */
    while (!LIST_EMPTY(&(sys->lif_list)))
    {
        local_if = LIST_FIRST(&(sys->lif_list));
        LIST_REMOVE(local_if, system_next);
        local_if_finalize(local_if);
    }

    while (!LIST_EMPTY(&(sys->lif_purge_list)))
    {
        local_if = LIST_FIRST(&(sys->lif_purge_list));
        LIST_REMOVE(local_if, system_purge_next);
        local_if_finalize(local_if);
    }

    iccp_system_dinit_netlink_socket();

    if (sys->log_file_path != NULL )
        free(sys->log_file_path);
    if (sys->cmd_file_path != NULL )
        free(sys->cmd_file_path);
    if (sys->config_file_path != NULL )
        free(sys->config_file_path);
    if (sys->pid_file_fd > 0)
        close(sys->pid_file_fd);
    if (sys->server_fd > 0)
        close(sys->server_fd);
    if (sys->sync_fd > 0)
        close(sys->sync_fd);
    if (sys->sync_ctrl_fd > 0)
        close(sys->sync_ctrl_fd);
    if (sys->arp_receive_fd > 0)
        close(sys->arp_receive_fd);
    if (sys->ndisc_receive_fd > 0)
        close(sys->ndisc_receive_fd);
    if (sys->sig_pipe_r > 0)
        close(sys->sig_pipe_r);
    if (sys->sig_pipe_w > 0)
        close(sys->sig_pipe_w);

    if (sys->epoll_fd)
        close(sys->epoll_fd);

    free(sys);
    ICCPD_LOG_INFO(__FUNCTION__, "System resource pool destructed successfully...");
}

struct CSM* system_create_csm()
{
    struct System* sys = NULL;
    struct CSM* csm = NULL;

    if ((sys = system_get_instance()) == NULL )
        return NULL;

    /* Create a new csm */
    csm = (struct CSM*)malloc(sizeof(struct CSM));
    if (csm == NULL )
        return NULL;
    else
        memset(csm, 0, sizeof(struct CSM));
    iccp_csm_init(csm);
    LIST_INSERT_HEAD(&(sys->csm_list), csm, next);

    return csm;
}

/* Get connect state machine instance by peer ip */
struct CSM* system_get_csm_by_peer_ip(const char* peer_ip)
{
    struct System* sys = NULL;
    struct CSM* csm = NULL;

    if ((sys = system_get_instance()) == NULL )
        return NULL;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        if (strcmp(csm->peer_ip, peer_ip) == 0)
            return csm;
    }

    return NULL;
}

struct CSM* system_get_csm_by_mlacp_id(int id)
{
    struct System* sys = NULL;
    struct CSM* csm = NULL;

    if ((sys = system_get_instance()) == NULL )
        return NULL;

    LIST_FOREACH(csm, &(sys->csm_list), next)
    {
        if (csm->app_csm.mlacp.id == id)
            return csm;
    }

    return NULL;
}
