/*
 * Copyright(c) 2016-2019 Nephos.
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
 *  Maintainer: Jim Jiang from nephos
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>
#include <string.h>
#include <stdbool.h>
#include <getopt.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/un.h>
#include "mclagdctl.h"

static int mclagdctl_sock_fd = -1;
char *mclagdctl_sock_path = "/var/run/iccpd/mclagdctl.sock";

/*
   Already implemented command:
   mclagdctl -i dump state
   mclagdctl -i dump arp
   mclagdctl -i dump mac
   mclagdctl -i dump portlist local
   mclagdctl -i dump portlist peer
 */

static struct command_type command_types[] =
{
    {
        .id = ID_CMDTYPE_D,
        .name = "dump",
        .enca_msg = NULL,
        .parse_msg = NULL,
    },
    {
        .id = ID_CMDTYPE_D_S,
        .parent_id = ID_CMDTYPE_D,
        .info_type = INFO_TYPE_DUMP_STATE,
        .name = "state",
        .enca_msg = mclagdctl_enca_dump_state,
        .parse_msg = mclagdctl_parse_dump_state,
    },
    {
        .id = ID_CMDTYPE_D_A,
        .parent_id = ID_CMDTYPE_D,
        .info_type = INFO_TYPE_DUMP_ARP,
        .name = "arp",
        .enca_msg = mclagdctl_enca_dump_arp,
        .parse_msg = mclagdctl_parse_dump_arp,
    },
    {
        .id = ID_CMDTYPE_D_A,
        .parent_id = ID_CMDTYPE_D,
        .info_type = INFO_TYPE_DUMP_NDISC,
        .name = "nd",
        .enca_msg = mclagdctl_enca_dump_ndisc,
        .parse_msg = mclagdctl_parse_dump_ndisc,
    },
    {
        .id = ID_CMDTYPE_D_A,
        .parent_id = ID_CMDTYPE_D,
        .info_type = INFO_TYPE_DUMP_MAC,
        .name = "mac",
        .enca_msg = mclagdctl_enca_dump_mac,
        .parse_msg = mclagdctl_parse_dump_mac,
    },
    {
        .id = ID_CMDTYPE_D_P,
        .parent_id = ID_CMDTYPE_D,
        .name = "portlist",
    },
    {
        .id = ID_CMDTYPE_D_P_L,
        .parent_id = ID_CMDTYPE_D_P,
        .info_type = INFO_TYPE_DUMP_LOCAL_PORTLIST,
        .name = "local",
        .enca_msg = mclagdctl_enca_dump_local_portlist,
        .parse_msg = mclagdctl_parse_dump_local_portlist,
    },
    {
        .id = ID_CMDTYPE_D_P_P,
        .parent_id = ID_CMDTYPE_D_P,
        .info_type = INFO_TYPE_DUMP_PEER_PORTLIST,
        .name = "peer",
        .enca_msg = mclagdctl_enca_dump_peer_portlist,
        .parse_msg = mclagdctl_parse_dump_peer_portlist,
    },
    {
        .id = ID_CMDTYPE_C,
        .name = "config",
        .enca_msg = NULL,
        .parse_msg = NULL,
    },
    {
        .id = ID_CMDTYPE_C_L,
        .parent_id = ID_CMDTYPE_C,
        .info_type = INFO_TYPE_CONFIG_LOGLEVEL,
        .name = "loglevel",
        .enca_msg = mclagdctl_enca_config_loglevel,
        .parse_msg = mclagdctl_parse_config_loglevel,
    },    
};

#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))
#define COMMAND_TYPE_COUNT ARRAY_SIZE(command_types)

int mclagdctl_sock_connect()
{
    struct sockaddr_un addr;
    int addrlen = 0;
    int ret = 0;

    if (mclagdctl_sock_fd >= 0)
        return 0;

    if (strlen(mclagdctl_sock_path) <= 0)
        return MCLAG_ERROR;

    mclagdctl_sock_fd = socket(AF_UNIX, SOCK_STREAM, 0);

    if (mclagdctl_sock_fd < 0)
    {
        return MCLAG_ERROR;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    snprintf(addr.sun_path, sizeof(addr.sun_path) - 1, "%s", mclagdctl_sock_path);
    addrlen = sizeof(addr.sun_family) + strlen(mclagdctl_sock_path);

    if ((ret = connect(mclagdctl_sock_fd, (struct sockaddr*)&addr, addrlen)) < 0)
    {
        close(mclagdctl_sock_fd);
        mclagdctl_sock_fd = -1;
        return MCLAG_ERROR;
    }

    return 0;
}

void mclagdctl_sock_close()
{
    if (mclagdctl_sock_fd > 0)
    {
        close(mclagdctl_sock_fd);
        mclagdctl_sock_fd = -1;
    }

    return;
}

int mclagdctl_sock_write(int fd, unsigned char *w_buf, int total_len)
{
    int write_len = 0;
    int ret = 0;

    while (write_len < total_len)
    {
        ret = write(fd, w_buf + write_len, total_len - write_len);
        if (ret <= 0)
        {
            return 0;
        }
        write_len += ret;
    }

    return write_len;
}

int mclagdctl_sock_read(int fd, unsigned char *r_buf, int total_len)
{
    int read_len = 0;
    int ret = 0;
    struct timeval tv = { 0 };
    fd_set read_fd;

    while (read_len < total_len)
    {
        FD_ZERO(&read_fd);
        FD_SET(fd, &read_fd);
        tv.tv_sec = 10;
        tv.tv_usec = 0;

        switch ((ret = select(fd + 1, &read_fd, NULL, NULL, &tv)))
        {
            case -1:    // error
                fprintf(stdout, "Mclagdctl:Select return error:%s\n", strerror(errno));
                return MCLAG_ERROR;

            case 0:    // timeout
                fprintf(stdout, "Mclagdctl:Select timeout:%s\n", strerror(errno));
                return MCLAG_ERROR;

            default:
                break;
        }

        ret = read(fd, r_buf + read_len, total_len - read_len);
        if (ret <= 0)
        {
            return MCLAG_ERROR;
        }
        read_len += ret;
    }

    return read_len;
}

int mclagdctl_enca_dump_state(char *msg, int mclag_id,  int argc, char **argv)
{
    struct mclagdctl_req_hdr req;

    memset(&req, 0, sizeof(struct mclagdctl_req_hdr));
    req.info_type = INFO_TYPE_DUMP_STATE;
    req.mclag_id = mclag_id;
    memcpy((struct mclagdctl_req_hdr *)msg, &req, sizeof(struct mclagdctl_req_hdr));

    return 1;
}

int mclagdctl_parse_dump_state(char *msg, int data_len)
{
    struct mclagd_state * state_info = NULL;
    int len = 0;
    int count = 0;
    int pos = 0;

    len = sizeof(struct mclagd_state);

    for (; data_len >= len; data_len -= len, count++)
    {
        state_info = (struct mclagd_state*)(msg + len * count);

        fprintf(stdout, "%s: %s\n", "The MCLAG's keepalive is", state_info->keepalive ? "OK" : "ERROR");

        if (state_info->mclag_id <= 0)
            fprintf(stdout, "%s: %s\n", "Domain id", "Unknown");
        else
            fprintf(stdout, "%s: %d\n", "Domain id", state_info->mclag_id);

        fprintf(stdout, "%s: %s\n", "Local Ip", state_info->local_ip);
        fprintf(stdout, "%s: %s\n", "Peer Ip", state_info->peer_ip);
        fprintf(stdout, "%s: %s\n", "Peer Link Interface", state_info->peer_link_if);

        fprintf(stdout, "%s: %02x:%02x:%02x:%02x:%02x:%02x \n",
                "Peer Link Mac",
                state_info->peer_link_mac[0], state_info->peer_link_mac[1],
                state_info->peer_link_mac[2], state_info->peer_link_mac[3],
                state_info->peer_link_mac[4], state_info->peer_link_mac[5]);

        if (state_info->role == 0)
            fprintf(stdout, "%s: %s\n", "Role", "None");
        else if (state_info->role == 1)
            fprintf(stdout, "%s: %s\n", "Role", "Active");
        else if (state_info->role == 2)
            fprintf(stdout, "%s: %s\n", "Role", "Standby");

        fprintf(stdout, "%s: %s\n", "MCLAG Interface", state_info->enabled_po);

        fprintf(stdout, "%s: %s\n", "Loglevel", state_info->loglevel);
    }

    return 0;
}

int mclagdctl_enca_dump_arp(char *msg, int mclag_id, int argc, char **argv)
{
    struct mclagdctl_req_hdr req;

    if (mclag_id <= 0)
    {
        fprintf(stderr, "Need to specify mclag-id through the parameter i !\n");
        return MCLAG_ERROR;
    }

    memset(&req, 0, sizeof(struct mclagdctl_req_hdr));
    req.info_type = INFO_TYPE_DUMP_ARP;
    req.mclag_id = mclag_id;
    memcpy((struct mclagdctl_req_hdr *)msg, &req, sizeof(struct mclagdctl_req_hdr));

    return 1;
}

int mclagdctl_enca_dump_ndisc(char *msg, int mclag_id, int argc, char **argv)
{
    struct mclagdctl_req_hdr req;

    if (mclag_id <= 0)
    {
        fprintf(stderr, "Need to specify mclag-id through the parameter i !\n");
        return MCLAG_ERROR;
    }

    memset(&req, 0, sizeof(struct mclagdctl_req_hdr));
    req.info_type = INFO_TYPE_DUMP_NDISC;
    req.mclag_id = mclag_id;
    memcpy((struct mclagdctl_req_hdr *)msg, &req, sizeof(struct mclagdctl_req_hdr));

    return 1;
}

int mclagdctl_parse_dump_arp(char *msg, int data_len)
{
    struct mclagd_arp_msg * arp_info = NULL;
    int len = 0;
    int count = 0;

    fprintf(stdout, "%-6s", "No.");
    fprintf(stdout, "%-20s", "IP");
    fprintf(stdout, "%-20s", "MAC");
    fprintf(stdout, "%-20s", "DEV");
    fprintf(stdout, "\n");

    len = sizeof(struct mclagd_arp_msg);

    for (; data_len >= len; data_len -= len, count++)
    {
        arp_info = (struct mclagd_arp_msg*)(msg + len * count);

        fprintf(stdout, "%-6d", count + 1);
        fprintf(stdout, "%-20s", arp_info->ipv4_addr);
        fprintf(stdout, "%02x:%02x:%02x:%02x:%02x:%02x",
                arp_info->mac_addr[0], arp_info->mac_addr[1],
                arp_info->mac_addr[2], arp_info->mac_addr[3],
                arp_info->mac_addr[4], arp_info->mac_addr[5]);
        fprintf(stdout, "   ");
        fprintf(stdout, "%-20s", arp_info->ifname);
        fprintf(stdout, "\n");
    }

    return 0;
}

int mclagdctl_parse_dump_ndisc(char *msg, int data_len)
{
    struct mclagd_ndisc_msg *ndisc_info = NULL;
    int len = 0;
    int count = 0;

    fprintf(stdout, "%-6s", "No.");
    fprintf(stdout, "%-52s", "IPv6");
    fprintf(stdout, "%-20s", "MAC");
    fprintf(stdout, "%-20s", "DEV");
    fprintf(stdout, "\n");

    len = sizeof(struct mclagd_ndisc_msg);

    for (; data_len >= len; data_len -= len, count++)
    {
        ndisc_info = (struct mclagd_ndisc_msg *)(msg + len * count);

        fprintf(stdout, "%-6d", count + 1);
        fprintf(stdout, "%-52s", ndisc_info->ipv6_addr);
        fprintf(stdout, "%02x:%02x:%02x:%02x:%02x:%02x",
                ndisc_info->mac_addr[0], ndisc_info->mac_addr[1],
                ndisc_info->mac_addr[2], ndisc_info->mac_addr[3],
                ndisc_info->mac_addr[4], ndisc_info->mac_addr[5]);
        fprintf(stdout, "   ");
        fprintf(stdout, "%-20s", ndisc_info->ifname);
        fprintf(stdout, "\n");
    }

    return 0;
}

int mclagdctl_enca_dump_mac(char *msg, int mclag_id, int argc, char **argv)
{
    struct mclagdctl_req_hdr req;

    if (mclag_id <= 0)
    {
        fprintf(stderr, "Need to specify mclag-id through the parameter i !\n");
        return MCLAG_ERROR;
    }

    memset(&req, 0, sizeof(struct mclagdctl_req_hdr));
    req.info_type = INFO_TYPE_DUMP_MAC;
    req.mclag_id = mclag_id;
    memcpy((struct mclagdctl_req_hdr *)msg, &req, sizeof(struct mclagdctl_req_hdr));

    return 1;
}

int mclagdctl_parse_dump_mac(char *msg, int data_len)
{
    struct mclagd_mac_msg * mac_info = NULL;
    int len = 0;
    int count = 0;

    fprintf(stdout, "%-60s\n", "TYPE: S-STATIC, D-DYNAMIC; AGE: L-Local age, P-Peer age");

    fprintf(stdout, "%-6s", "No.");
    fprintf(stdout, "%-5s", "TYPE");
    fprintf(stdout, "%-20s", "MAC");
    fprintf(stdout, "%-5s", "VID");
    fprintf(stdout, "%-20s", "DEV");
    fprintf(stdout, "%-20s", "ORIGIN-DEV");
    fprintf(stdout, "%-5s", "AGE");
    fprintf(stdout, "\n");

    len = sizeof(struct mclagd_mac_msg);

    for (; data_len >= len; data_len -= len, count++)
    {
        mac_info = (struct mclagd_mac_msg*)(msg + len * count);

        fprintf(stdout, "%-6d", count + 1);

        if (mac_info->fdb_type == MAC_TYPE_STATIC_CTL)
            fprintf(stdout, "%-5s", "S");
        else
            fprintf(stdout, "%-5s", "D");

        fprintf(stdout, "%-20s", mac_info->mac_str);
        fprintf(stdout, "%-5d", mac_info->vid);
        fprintf(stdout, "%-20s", mac_info->ifname);
        fprintf(stdout, "%-20s", mac_info->origin_ifname);

        if ((mac_info->age_flag & MAC_AGE_LOCAL_CTL) && (mac_info->age_flag & MAC_AGE_PEER_CTL))
            fprintf(stdout, "%-5s", "LP");
        else if (mac_info->age_flag & MAC_AGE_LOCAL_CTL)
            fprintf(stdout, "%-5s", "L");
        else if (mac_info->age_flag & MAC_AGE_PEER_CTL)
            fprintf(stdout, "%-5s", "P");
        else
            fprintf(stdout, "%-5s", " ");
        fprintf(stdout, "\n");
    }

    return 0;
}

int mclagdctl_enca_dump_local_portlist(char *msg, int mclag_id, int argc, char **argv)
{
    struct mclagdctl_req_hdr req;

    if (mclag_id <= 0)
    {
        fprintf(stderr, "Need to specify mclag-id through the parameter i !\n");
        return MCLAG_ERROR;
    }

    memset(&req, 0, sizeof(struct mclagdctl_req_hdr));
    req.info_type = INFO_TYPE_DUMP_LOCAL_PORTLIST;
    req.mclag_id = mclag_id;
    memcpy((struct mclagdctl_req_hdr *)msg, &req, sizeof(struct mclagdctl_req_hdr));

    return 1;
}

int mclagdctl_parse_dump_local_portlist(char *msg, int data_len)
{
    struct mclagd_local_if * lif_info = NULL;
    int len = 0;
    int count = 0;
    int pos = 0;

    len = sizeof(struct mclagd_local_if);

    for (; data_len >= len; data_len -= len, count++)
    {
        lif_info = (struct mclagd_local_if*)(msg + len * count);

        for (pos = 0; pos < 60; ++pos)
            fprintf(stdout, "-");

        fprintf(stdout, "\n");

        if (memcmp(lif_info->type, "PortChannel", 11) == 0)
        {
            fprintf(stdout, "%s: %d\n", "Ifindex", lif_info->ifindex);
            fprintf(stdout, "%s: %s\n", "Type", lif_info->type);
            fprintf(stdout, "%s: %s\n", "PortName", lif_info->name);
            fprintf(stdout, "%s: %02x:%02x:%02x:%02x:%02x:%02x \n",
                    "MAC",
                    lif_info->mac_addr[0], lif_info->mac_addr[1],
                    lif_info->mac_addr[2], lif_info->mac_addr[3],
                    lif_info->mac_addr[4], lif_info->mac_addr[5]);

            fprintf(stdout, "%s: %s\n", "IPv4Address", lif_info->ipv4_addr);
            fprintf(stdout, "%s: %d\n", "Prefixlen", lif_info->prefixlen);
            fprintf(stdout, "%s: %s\n", "State", lif_info->state);
            fprintf(stdout, "%s: %s\n", "IsL3Interface", lif_info->l3_mode ? "Yes" : "No");
            /*fprintf(stdout, "%s: %s\n", "IsPeerlink", lif_info->is_peer_link ? "Yes" : "No");*/
            fprintf(stdout, "%s: %s\n", "MemberPorts", lif_info->portchannel_member_buf);
            /*fprintf(stdout,"%s: %d\n" ,"PortchannelId", lif_info->po_id);
               fprintf(stdout,"%s: %d\n" ,"PortchannelIsUp", lif_info->po_active);
               fprintf(stdout,"%s: %s\n", "MlacpState", lif_info->mlacp_state);*/
            fprintf(stdout, "%s: %s\n", "IsIsolateWithPeerlink", lif_info->isolate_to_peer_link ? "Yes" : "No");
            fprintf(stdout, "%s: %s\n", "VlanList", lif_info->vlanlist);
        }
        else
        {
            fprintf(stdout, "%s: %d\n", "Ifindex", lif_info->ifindex);
            fprintf(stdout, "%s: %s\n", "Type", lif_info->type);
            fprintf(stdout, "%s: %s\n", "PortName", lif_info->name);
            fprintf(stdout, "%s: %s\n", "State", lif_info->state);
            /*fprintf(stdout,"%s: %d\n" ,"PortchannelId", lif_info->po_id);*/
        }

        for (pos = 0; pos < 60; ++pos)
            fprintf(stdout, "-");

        fprintf(stdout, "\n\n");
    }

    return 0;
}

int mclagdctl_enca_dump_peer_portlist(char *msg, int mclag_id,  int argc, char **argv)
{
    struct mclagdctl_req_hdr req;

    if (mclag_id <= 0)
    {
        fprintf(stderr, "Need to specify mclag-id through the parameter i !\n");
        return MCLAG_ERROR;
    }

    memset(&req, 0, sizeof(struct mclagdctl_req_hdr));
    req.info_type = INFO_TYPE_DUMP_PEER_PORTLIST;
    req.mclag_id = mclag_id;
    memcpy((struct mclagdctl_req_hdr *)msg, &req, sizeof(struct mclagdctl_req_hdr));

    return 1;
}

int mclagdctl_parse_dump_peer_portlist(char *msg, int data_len)
{
    struct mclagd_peer_if * pif_info = NULL;
    int len = 0;
    int count = 0;
    int pos = 0;

    len = sizeof(struct mclagd_peer_if);

    for (; data_len >= len; data_len -= len, count++)
    {
        pif_info = (struct mclagd_peer_if*)(msg + len * count);

        for (pos = 0; pos < 60; ++pos)
            fprintf(stdout, "-");

        fprintf(stdout, "\n");

        fprintf(stdout, "%s: %d\n", "Ifindex", pif_info->ifindex);
        fprintf(stdout, "%s: %s\n", "Type", pif_info->type);
        fprintf(stdout, "%s: %s\n", "PortName", pif_info->name);
        fprintf(stdout, "%s: %02x:%02x:%02x:%02x:%02x:%02x \n",
                "MAC",
                pif_info->mac_addr[0], pif_info->mac_addr[1],
                pif_info->mac_addr[2], pif_info->mac_addr[3],
                pif_info->mac_addr[4], pif_info->mac_addr[5]);

        fprintf(stdout, "%s: %s\n", "State", pif_info->state);
        /*fprintf(stdout,"%s: %d\n" ,"PortchannelId", pif_info->po_id);
           fprintf(stdout,"%s: %d\n" ,"PortchannelIsActive", pif_info->po_active);*/

        for (pos = 0; pos < 60; ++pos)
            fprintf(stdout, "-");

        fprintf(stdout, "\n\n");
    }

    return 0;
}

int mclagdctl_enca_config_loglevel(char *msg, int log_level,  int argc, char **argv)
{
    struct mclagdctl_req_hdr req;

    memset(&req, 0, sizeof(struct mclagdctl_req_hdr));
    req.info_type = INFO_TYPE_CONFIG_LOGLEVEL;
    req.mclag_id = log_level;
    memcpy((struct mclagdctl_req_hdr *)msg, &req, sizeof(struct mclagdctl_req_hdr));

    return 1;
}

int mclagdctl_parse_config_loglevel(char *msg, int data_len)
{

    int ret = *(int*)msg;

    if (ret == 0)
        fprintf(stdout, "%s\n", "Config loglevel success!");
    else
        fprintf(stdout, "%s\n", "Config loglevel failed!");

    return 0;
}

static bool __mclagdctl_cmd_executable(struct command_type *cmd_type)
{
    if (!cmd_type->enca_msg || !cmd_type->parse_msg)
        return 0;

    return 1;
}

static int __mclagdctl_cmd_param_cnt(struct command_type *cmd_type)
{
    int i = 0;

    while (cmd_type->params[i])
        i++;

    return i;
}

static struct command_type *__mclagdctl_get_cmd_by_parent(char *cmd_name,
                                                          enum id_command_type parent_id)
{
    int i;

    for (i = 0; i < COMMAND_TYPE_COUNT; i++)
    {
        if (!strncmp(command_types[i].name, cmd_name, strlen(cmd_name))
            && command_types[i].parent_id == parent_id)
            return &command_types[i];
    }

    return NULL;
}

static struct command_type *__mclagdctl_get_cmd_by_id(enum id_command_type id)
{
    int i;

    for (i = 0; i < COMMAND_TYPE_COUNT; i++)
    {
        if (command_types[i].id == id)
            return &command_types[i];
    }

    return NULL;
}

static int mclagdctl_find_cmd(struct command_type **pcmd_type, int *argc, char ***argv)
{
    char *cmd_name;
    enum id_command_type parent_id = ID_CMDTYPE_NONE;
    struct command_type *cmd_type;

    while (1)
    {
        if (!*argc)
        {
            fprintf(stderr, "None or incomplete command\n");
            return -EINVAL;
        }

        cmd_name = *argv[0];
        (*argc)--;
        (*argv)++;
        cmd_type = __mclagdctl_get_cmd_by_parent(cmd_name, parent_id);

        if (!cmd_type)
        {
            fprintf(stderr, "Unknown command \"%s\".\n", cmd_name);
            return -EINVAL;
        }

        if (__mclagdctl_cmd_executable(cmd_type) && __mclagdctl_cmd_param_cnt(cmd_type) >= *argc)
        {
            *pcmd_type = cmd_type;
            return 0;
        }

        parent_id = cmd_type->id;
    }
}

static int mclagdctl_check_cmd_params(struct command_type *cmd_type,
                                      int argc, char **argv)
{
    int i = 0;

    while (cmd_type->params[i])
    {
        if (i == argc)
        {
            fprintf(stderr, "Command line parameter \"%s\" expected.\n", cmd_type->params[i]);
            return -EINVAL;
        }
        i++;
    }

    return 0;
}

static void mclagdctl_print_cmd(struct command_type *cmd_type)
{
    if (cmd_type->parent_id != ID_CMDTYPE_NONE)
    {
        mclagdctl_print_cmd(__mclagdctl_get_cmd_by_id(cmd_type->parent_id));
        fprintf(stdout, " ");
    }
    fprintf(stdout, "%s", cmd_type->name);
}

static void mclagdctl_print_help(const char *argv0)
{
    int i, j;
    struct command_type *cmd_type;

    fprintf(stdout, "%s [options] command [command args]\n"
            "    -h --help                Show this help\n"
            "    -i --mclag-id            Specify one mclag id\n"
            "    -l --level               Specify log level     critical,err,warn,notice,info,debug\n",
            argv0);
    fprintf(stdout, "Commands:\n");

    for (i = 0; i < COMMAND_TYPE_COUNT; i++)
    {
        cmd_type = &command_types[i];
        if (!__mclagdctl_cmd_executable(cmd_type))
            continue;
        fprintf(stdout, "    ");
        mclagdctl_print_cmd(cmd_type);

        for (j = 0; cmd_type->params[j]; j++)
            fprintf(stdout, " %s", cmd_type->params[j]);

        fprintf(stdout, "\n");
    }
}

int main(int argc, char **argv)
{
    char buf[MCLAGDCTL_CMD_SIZE] = { 0 };
    char *argv0 = argv[0];
    char *rcv_buf = NULL;
    static const struct option long_options[] =
    {
        { "help",      no_argument,             NULL,        'h' },
        { "mclag id",  required_argument,       NULL,        'i' },
        { "log level", required_argument,       NULL,        'l' },
        { NULL,        0,                       NULL,        0   }
    };
    int opt;
    int err;
    struct command_type *cmd_type;
    int ret;
    unsigned para_int = 0;

    int len = 0;
    char *data;
    struct mclagd_reply_hdr *reply;

    while ((opt = getopt_long(argc, argv, "hi:l:", long_options, NULL)) >= 0)
    {
        switch (opt)
        {
            case 'h':
                mclagdctl_print_help(argv0);
                return EXIT_SUCCESS;

        case 'i':
            para_int = atoi(optarg);
            break;

        case 'l':
            switch (tolower(optarg[0]))
            {
                case 'c':
                    para_int = CRITICAL;
                    break;

                case 'e':
                    para_int = ERR;
                    break;

                case 'w':
                    para_int = WARN;
                    break;

                case 'n':
                    para_int = NOTICE;
                    break;

                case 'i':
                    para_int = INFO;
                    break;

                case 'd':
                    para_int = DEBUG;
                    break;

                default:
                    fprintf(stderr, "unknown option \"%c\".\n", opt);
                    mclagdctl_print_help(argv0);
                    return EXIT_FAILURE;
            }
            break;

            case '?':
                fprintf(stderr, "unknown option.\n");
                mclagdctl_print_help(argv0);
                return EXIT_FAILURE;

            default:
                fprintf(stderr, "unknown option \"%c\".\n", opt);
                mclagdctl_print_help(argv0);
                return EXIT_FAILURE;
        }
    }

    argv += optind;
    argc -= optind;

    err = mclagdctl_find_cmd(&cmd_type, &argc, &argv);
    if (err)
    {
        mclagdctl_print_help(argv0);
        return EXIT_FAILURE;
    }

    err = mclagdctl_check_cmd_params(cmd_type, argc, argv);
    if (err)
    {
        mclagdctl_print_help(argv0);
        return EXIT_FAILURE;
    }

    if (mclagdctl_sock_fd <= 0)
    {
        ret = mclagdctl_sock_connect();
        if (ret < 0)
            return EXIT_FAILURE;
    }

    if (cmd_type->enca_msg(buf, para_int, argc, argv) < 0)
    {
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    ret = mclagdctl_sock_write(mclagdctl_sock_fd, buf, sizeof(struct mclagdctl_req_hdr));

    if (ret <= 0)
    {
        fprintf(stderr, "Failed to send command to mclagd\n");
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    /*read data length*/
    memset(buf, 0, MCLAGDCTL_CMD_SIZE);
    ret = mclagdctl_sock_read(mclagdctl_sock_fd, buf, sizeof(int));
    if (ret <= 0)
    {
        fprintf(stderr, "Failed to read data length from mclagd\n");
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    /*cont length*/
    len = *((int*)buf);
    if (len <= 0)
    {
        ret = EXIT_FAILURE;
        fprintf(stderr, "pkt len = %d, error\n", len);
        goto mclagdctl_disconnect;
    }

    rcv_buf = (char *)malloc(len);
    if (!rcv_buf)
    {
        fprintf(stderr, "Failed to malloc rcv_buf for mclagdctl\n");
        goto mclagdctl_disconnect;
    }

    /*read data*/
    ret = mclagdctl_sock_read(mclagdctl_sock_fd, rcv_buf, len);
    if (ret <= 0)
    {
        fprintf(stderr, "Failed to read data from mclagd\n");
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    reply = (struct mclagd_reply_hdr *)rcv_buf;
    if (reply->info_type != cmd_type->info_type)
    {
        fprintf(stderr, "Reply info type from mclagd error\n");
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    if (reply->exec_result == EXEC_TYPE_NO_EXIST_SYS)
    {
        fprintf(stderr, "No exist sys in iccpd!\n");
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    if (reply->exec_result == EXEC_TYPE_NO_EXIST_MCLAGID)
    {
        fprintf(stderr, "Mclag-id %d hasn't been configured in iccpd!\n", para_int);
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    if (reply->exec_result == EXEC_TYPE_FAILED)
    {
        fprintf(stderr, "exec error in iccpd!\n");
        ret = EXIT_FAILURE;
        goto mclagdctl_disconnect;
    }

    cmd_type->parse_msg((char *)(rcv_buf + sizeof(struct mclagd_reply_hdr)), len - sizeof(struct mclagd_reply_hdr));

    ret = EXIT_SUCCESS;

 mclagdctl_disconnect:
    mclagdctl_sock_close();

    if (rcv_buf)
        free(rcv_buf);

    return ret;
}

