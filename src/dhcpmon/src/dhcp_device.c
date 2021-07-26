/**
 * @file dhcp_device.c
 *
 *  device (interface) module
 */

#include <err.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <net/ethernet.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <netinet/ether.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <syslog.h>
#include <libexplain/ioctl.h>
#include <linux/filter.h>
#include <netpacket/packet.h>
#include <sys/types.h>
#include <ifaddrs.h>
#include <netinet/ip6.h>

#include "dhcp_device.h"

/** DHCP versions flags */
static bool dhcpv4_enabled;
static bool dhcpv6_enabled;

/** Counter print width */
#define DHCP_COUNTER_WIDTH  9

/** Start of Ether header of a captured frame */
#define ETHER_START_OFFSET  0
/** EtherType field offset from Ether header of a captured frame */
#define ETHER_TYPE_OFFSET (ETHER_START_OFFSET + 12)
/** Start of IP header of a captured frame */
#define IP_START_OFFSET (ETHER_START_OFFSET + ETHER_HDR_LEN)
/** Start of UDP header on IPv4 packet of a captured frame */
#define UDPv4_START_OFFSET (IP_START_OFFSET + sizeof(struct ip))
/** Start of DHCPv4 header of a captured frame */
#define DHCPv4_START_OFFSET (UDPv4_START_OFFSET + sizeof(struct udphdr))
/** Start of DHCPv4 Options segment of a captured frame */
#define DHCPv4_OPTIONS_HEADER_SIZE 240
/** Offset of DHCP GIADDR */
#define DHCP_GIADDR_OFFSET 24

/** IPv6 link-local prefix */
#define IPV6_LINK_LOCAL_PREFIX 0x80fe
/** Start of UDP header on IPv6 packet of a captured frame */
#define UDPv6_START_OFFSET (IP_START_OFFSET + sizeof(struct ip6_hdr))
/** Start of DHCPv6 header of a captured frame */
#define DHCPv6_START_OFFSET (UDPv6_START_OFFSET + sizeof(struct udphdr))
/** Size of 'type' field on DHCPv6 header */
#define DHCPv6_TYPE_LENGTH 1
/** Size of DHCPv6 relay message header to first option */
#define DHCPv6_RELAY_MSG_OPTIONS_OFFSET 34
/** Size of 'option' field on DHCPv6 header */
#define DHCPv6_OPTION_LENGTH 2
/** Size of 'option length' field on DHCPv6 header */
#define DHCPv6_OPTION_LEN_LENGTH 2
/** DHCPv6 OPTION_RELAY_MSG */
#define DHCPv6_OPTION_RELAY_MSG 9

#define OP_LDHA     (BPF_LD  | BPF_H   | BPF_ABS)   /** bpf ldh Abs */
#define OP_LDHI     (BPF_LD  | BPF_H   | BPF_IND)   /** bpf ldh Ind */
#define OP_LDB      (BPF_LD  | BPF_B   | BPF_ABS)   /** bpf ldb Abs*/
#define OP_JEQ      (BPF_JMP | BPF_JEQ | BPF_K)     /** bpf jeq */
#define OP_JGT      (BPF_JMP | BPF_JGT | BPF_K)     /** bpf jgt */
#define OP_RET      (BPF_RET | BPF_K)               /** bpf ret */
#define OP_JSET     (BPF_JMP | BPF_JSET | BPF_K)    /** bpf jset */
#define OP_LDXB     (BPF_LDX | BPF_B    | BPF_MSH)  /** bpf ldxb */

/** Berkeley Packet Filter program for "udp and (port 546 or port 547 or port 67 or port 68)".
 * This program is obtained using the following command tcpdump:
 * `tcpdump -dd "udp and (port 546 or port 547 or port 67 or port 68)"`
 */
static struct sock_filter dhcp_bpf_code[] = {
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x0000000c},   // (000) ldh      [12]
    {.code = OP_JEQ,  .jt = 0,  .jf = 9,  .k = 0x000086dd},   // (001) jeq      #0x86dd          jt 2	jf 11
    {.code = OP_LDB,  .jt = 0,  .jf = 0,  .k = 0x00000014},   // (002) ldb      [20]
    {.code = OP_JEQ,  .jt = 0,  .jf = 24, .k = 0x00000011},   // (003) jeq      #0x11            jt 4	jf 28
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x00000036},   // (004) ldh      [54]
    {.code = OP_JEQ,  .jt = 21, .jf = 0,  .k = 0x00000222},   // (005) jeq      #0x222           jt 27	jf 6
    {.code = OP_JEQ,  .jt = 20, .jf = 0,  .k = 0x00000223},   // (006) jeq      #0x223           jt 27	jf 7
    {.code = OP_JEQ,  .jt = 19, .jf = 0,  .k = 0x00000043},   // (007) jeq      #0x43            jt 27	jf 8
    {.code = OP_JEQ,  .jt = 18, .jf = 0,  .k = 0x00000044},   // (008) jeq      #0x44            jt 27	jf 9
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x00000038},   // (009) ldh      [56]
    {.code = OP_JEQ,  .jt = 16, .jf = 13, .k = 0x00000222},   // (010) jeq      #0x222           jt 27	jf 24
    {.code = OP_JEQ,  .jt = 0,  .jf = 16, .k = 0x00000800},   // (011) jeq      #0x800           jt 12	jf 28
    {.code = OP_LDB,  .jt = 0,  .jf = 0,  .k = 0x00000017},   // (012) ldb      [23]
    {.code = OP_JEQ,  .jt = 0,  .jf = 14, .k = 0x00000011},   // (013) jeq      #0x11            jt 14	jf 28
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x00000014},   // (014) ldh      [20]
    {.code = OP_JSET, .jt = 12, .jf = 0,  .k = 0x00001fff},   // (015) jset     #0x1fff          jt 28	jf 16
    {.code = OP_LDXB, .jt = 0,  .jf = 0,  .k = 0x0000000e},   // (016) ldxb     4*([14]&0xf)
    {.code = OP_LDHI, .jt = 0,  .jf = 0,  .k = 0x0000000e},   // (017) ldh      [x + 14]
    {.code = OP_JEQ,  .jt = 8,  .jf = 0,  .k = 0x00000222},   // (018) jeq      #0x222           jt 27	jf 19
    {.code = OP_JEQ,  .jt = 7,  .jf = 0,  .k = 0x00000223},   // (019) jeq      #0x223           jt 27	jf 20
    {.code = OP_JEQ,  .jt = 6,  .jf = 0,  .k = 0x00000043},   // (020) jeq      #0x43            jt 27	jf 21
    {.code = OP_JEQ,  .jt = 5,  .jf = 0,  .k = 0x00000044},   // (021) jeq      #0x44            jt 27	jf 22
    {.code = OP_LDHI, .jt = 0,  .jf = 0,  .k = 0x00000010},   // (022) ldh      [x + 16]
    {.code = OP_JEQ,  .jt = 3,  .jf = 0,  .k = 0x00000222},   // (023) jeq      #0x222           jt 27	jf 24
    {.code = OP_JEQ,  .jt = 2,  .jf = 0,  .k = 0x00000223},   // (024) jeq      #0x223           jt 27	jf 25
    {.code = OP_JEQ,  .jt = 1,  .jf = 0,  .k = 0x00000043},   // (025) jeq      #0x43            jt 27	jf 26
    {.code = OP_JEQ,  .jt = 0,  .jf = 1,  .k = 0x00000044},   // (026) jeq      #0x44            jt 27	jf 28
    {.code = OP_RET,  .jt = 0,  .jf = 0,  .k = 0x00040000},   // (027) ret      #262144
    {.code = OP_RET,  .jt = 0,  .jf = 0,  .k = 0x00000000},   // (028) ret
};

/** Filter program socket struct */
static struct sock_fprog dhcp_sock_bfp = {
    .len = sizeof(dhcp_bpf_code) / sizeof(*dhcp_bpf_code), .filter = dhcp_bpf_code
};

/** Aggregate device of DHCP interfaces. It contains aggregate counters from
    all interfaces
 */
static dhcp_device_context_t aggregate_dev = {0};

/** Monitored DHCPv4 message type */
static dhcpv4_message_type_t v4_monitored_msgs[] = {
    DHCPv4_MESSAGE_TYPE_DISCOVER,
    DHCPv4_MESSAGE_TYPE_OFFER,
    DHCPv4_MESSAGE_TYPE_REQUEST,
    DHCPv4_MESSAGE_TYPE_ACK
};

/** Monitored DHCPv6 message type */
static dhcpv6_message_type_t v6_monitored_msgs[] = {
    DHCPv6_MESSAGE_TYPE_SOLICIT,
    DHCPv6_MESSAGE_TYPE_ADVERTISE,
    DHCPv6_MESSAGE_TYPE_REQUEST,
    DHCPv6_MESSAGE_TYPE_REPLY
};

/** Number of monitored DHCPv4 message type */
static uint8_t v4_monitored_msg_sz = sizeof(v4_monitored_msgs) / sizeof(*v4_monitored_msgs);

/** Number of monitored DHCPv6 message type */
static uint8_t v6_monitored_msg_sz = sizeof(v6_monitored_msgs) / sizeof(*v6_monitored_msgs);

/**
 * @code handle_dhcp_option_53(context, dhcp_option, dir, iphdr, dhcphdr);
 *
 * @brief handle the logic related to DHCP option 53
 *
 * @param context       Device (interface) context
 * @param dhcp_option   pointer to DHCP option buffer space
 * @param dir           packet direction
 * @param iphdr         pointer to packet IP header
 * @param dhcphdr       pointer to DHCP header
 *
 * @return none
 */
static void handle_dhcp_option_53(dhcp_device_context_t *context,
                                  const u_char *dhcp_option,
                                  dhcp_packet_direction_t dir,
                                  struct ip *iphdr,
                                  uint8_t *dhcphdr)
{
    in_addr_t giaddr;
    switch (dhcp_option[2])
    {
    // DHCP messages send by client
    case DHCPv4_MESSAGE_TYPE_DISCOVER:
    case DHCPv4_MESSAGE_TYPE_REQUEST:
    case DHCPv4_MESSAGE_TYPE_DECLINE:
    case DHCPv4_MESSAGE_TYPE_RELEASE:
    case DHCPv4_MESSAGE_TYPE_INFORM:
        giaddr = ntohl(dhcphdr[DHCP_GIADDR_OFFSET] << 24 | dhcphdr[DHCP_GIADDR_OFFSET + 1] << 16 |
                       dhcphdr[DHCP_GIADDR_OFFSET + 2] << 8 | dhcphdr[DHCP_GIADDR_OFFSET + 3]);
        if ((context->giaddr_ip == giaddr && context->is_uplink && dir == DHCP_TX) ||
            (!context->is_uplink && dir == DHCP_RX && iphdr->ip_dst.s_addr == INADDR_BROADCAST)) {
            context->counters.v4counters[DHCP_COUNTERS_CURRENT][dir][dhcp_option[2]]++;
            aggregate_dev.counters.v4counters[DHCP_COUNTERS_CURRENT][dir][dhcp_option[2]]++;
        }
        break;
    // DHCP messages send by server
    case DHCPv4_MESSAGE_TYPE_OFFER:
    case DHCPv4_MESSAGE_TYPE_ACK:
    case DHCPv4_MESSAGE_TYPE_NAK:
        if ((context->giaddr_ip == iphdr->ip_dst.s_addr && context->is_uplink && dir == DHCP_RX) ||
            (!context->is_uplink && dir == DHCP_TX)) {
            context->counters.v4counters[DHCP_COUNTERS_CURRENT][dir][dhcp_option[2]]++;
            aggregate_dev.counters.v4counters[DHCP_COUNTERS_CURRENT][dir][dhcp_option[2]]++;
        }
        break;
    default:
        syslog(LOG_WARNING, "handle_dhcp_option_53(%s): Unknown DHCP option 53 type %d", context->intf, dhcp_option[2]);
        break;
    }
}

/**
 * @code handle_dhcpv6_option(context, dhcp_option, dir);
 *
 * @brief handle the logic related to DHCPv6 option
 *
 * @param context       Device (interface) context
 * @param dhcp_option   pointer to DHCP option buffer space
 * @param dir           packet direction
 *
 * @return none
 */
static void handle_dhcpv6_option(dhcp_device_context_t *context,
                                  const u_char dhcp_option,
                                  dhcp_packet_direction_t dir)
{
    switch (dhcp_option)
    {
    case DHCPv6_MESSAGE_TYPE_SOLICIT:
    case DHCPv6_MESSAGE_TYPE_REQUEST:
    case DHCPv6_MESSAGE_TYPE_CONFIRM:
    case DHCPv6_MESSAGE_TYPE_RENEW:
    case DHCPv6_MESSAGE_TYPE_REBIND:
    case DHCPv6_MESSAGE_TYPE_RELEASE:
    case DHCPv6_MESSAGE_TYPE_DECLINE:
    case DHCPv6_MESSAGE_TYPE_ADVERTISE:
    case DHCPv6_MESSAGE_TYPE_REPLY:
    case DHCPv6_MESSAGE_TYPE_RECONFIGURE:
    case DHCPv6_MESSAGE_TYPE_INFORMATION_REQUEST:
        context->counters.v6counters[DHCP_COUNTERS_CURRENT][dir][dhcp_option]++;
        aggregate_dev.counters.v6counters[DHCP_COUNTERS_CURRENT][dir][dhcp_option]++;
        break;
    default:
        syslog(LOG_WARNING, "handle_dhcpv6_option(%s): Unknown DHCPv6 option type %d", context->intf, dhcp_option);
        break;
    }
}

/**
 * @code read_callback(fd, event, arg);
 *
 * @brief callback for libevent which is called every time out in order to read queued packet capture
 *
 * @param fd            socket to read from
 * @param event         libevent triggered event
 * @param arg           user provided argument for callback (interface context)
 *
 * @return none
 */
static void read_callback(int fd, short event, void *arg)
{
    dhcp_device_context_t *context = (dhcp_device_context_t*) arg;
    ssize_t buffer_sz;

    while ((event == EV_READ) &&
           ((buffer_sz = recv(fd, context->buffer, context->snaplen, MSG_DONTWAIT)) > 0)) {
        struct ether_header *ethhdr = (struct ether_header*) context->buffer;
        struct ip *iphdr;
        struct ip6_hdr *ipv6hdr;
        struct udphdr *udp;
        uint8_t *dhcphdr;
        int dhcp_option_offset;

        bool is_ipv4 = (ntohs(ethhdr->ether_type) == ETHERTYPE_IP);
        if (is_ipv4) {
            iphdr = (struct ip*) (context->buffer + IP_START_OFFSET);
            udp = (struct udphdr*) (context->buffer + UDPv4_START_OFFSET);
            dhcphdr = context->buffer + DHCPv4_START_OFFSET;
            dhcp_option_offset = DHCPv4_START_OFFSET + DHCPv4_OPTIONS_HEADER_SIZE;
        } else {
            ipv6hdr = (struct ip6_hdr*) (context->buffer + IP_START_OFFSET);
            udp = (struct udphdr*) (context->buffer + UDPv6_START_OFFSET);
            dhcphdr = context->buffer + DHCPv6_START_OFFSET;
            dhcp_option_offset = DHCPv6_START_OFFSET;
        }
        if (is_ipv4 && dhcpv4_enabled && (buffer_sz > UDPv4_START_OFFSET + sizeof(struct udphdr) + DHCPv4_OPTIONS_HEADER_SIZE) &&
            (ntohs(udp->len) > DHCPv4_OPTIONS_HEADER_SIZE)) {
            int dhcp_sz = ntohs(udp->len) < buffer_sz - UDPv4_START_OFFSET - sizeof(struct udphdr) ?
                          ntohs(udp->len) : buffer_sz - UDPv4_START_OFFSET - sizeof(struct udphdr);
            int dhcp_option_sz = dhcp_sz - DHCPv4_OPTIONS_HEADER_SIZE;
            const u_char *dhcp_option = context->buffer + dhcp_option_offset;
            dhcp_packet_direction_t dir = (ethhdr->ether_shost[0] == context->mac[0] &&
                                           ethhdr->ether_shost[1] == context->mac[1] &&
                                           ethhdr->ether_shost[2] == context->mac[2] &&
                                           ethhdr->ether_shost[3] == context->mac[3] &&
                                           ethhdr->ether_shost[4] == context->mac[4] &&
                                           ethhdr->ether_shost[5] == context->mac[5]) ?
                                           DHCP_TX : DHCP_RX;
            int offset = 0;
            int stop_dhcp_processing = 0;
            while ((offset < (dhcp_option_sz + 1)) && dhcp_option[offset] != 255) {
                switch (dhcp_option[offset])
                {
                case 53:
                    if (offset < (dhcp_option_sz + 2)) {
                        handle_dhcp_option_53(context, &dhcp_option[offset], dir, iphdr, dhcphdr);
                    }
                    stop_dhcp_processing = 1; // break while loop since we are only interested in Option 53
                    break;
                default:
                    break;
                }

                if (stop_dhcp_processing == 1) {
                    break;
                }

                if (dhcp_option[offset] == 0) { // DHCP Option Padding
                    offset++;
                } else {
                    offset += dhcp_option[offset + 1] + 2;
                }
            }
        }
        else if (!is_ipv4 && dhcpv6_enabled && (buffer_sz > UDPv6_START_OFFSET + sizeof(struct udphdr) + DHCPv6_TYPE_LENGTH)) {
            const u_char* dhcp_option = context->buffer + dhcp_option_offset;
            dhcp_packet_direction_t dir = (ethhdr->ether_shost[0] == context->mac[0] &&
                                           ethhdr->ether_shost[1] == context->mac[1] &&
                                           ethhdr->ether_shost[2] == context->mac[2] &&
                                           ethhdr->ether_shost[3] == context->mac[3] &&
                                           ethhdr->ether_shost[4] == context->mac[4] &&
                                           ethhdr->ether_shost[5] == context->mac[5]) ?
                                           DHCP_TX : DHCP_RX;
            int offset = 0;
            uint16_t option = 0;
            // Get to inner DHCP header from encapsulated RELAY_FORWARD or RELAY_REPLY header
            while (dhcp_option[offset] == DHCPv6_MESSAGE_TYPE_RELAY_FORWARD || dhcp_option[offset] == DHCPv6_MESSAGE_TYPE_RELAY_REPLY)
            {
                // Get to DHCPv6_OPTION_RELAY_MSG from all options
                offset += DHCPv6_RELAY_MSG_OPTIONS_OFFSET;
                option = htons(*((uint16_t*)(&(dhcp_option[offset]))));

                while (option != DHCPv6_OPTION_RELAY_MSG)
                {
                    offset += DHCPv6_OPTION_LENGTH;
                    // Add to offset the option length and get the next option ID
                    offset += htons(*((uint16_t*)(&(dhcp_option[offset]))));
                    option = htons(*((uint16_t*)(&(dhcp_option[offset]))));
                }
                offset += DHCPv6_OPTION_LENGTH + DHCPv6_OPTION_LEN_LENGTH;
            }
            handle_dhcpv6_option(context, dhcp_option[offset], dir);
        } else {
            syslog(LOG_WARNING, "read_callback(%s): read length (%ld) is too small to capture DHCP options",
                   context->intf, buffer_sz);
        }
    }
}

/**
 * @code dhcp_device_is_dhcp_inactive(v4counters, v6counters, type);
 *
 * @brief Check if there were no DHCP activity
 *
 * @param v4counters  current/snapshot v4counter
 *
 * @param v6counters  current/snapshot v6counter
 *
 * @param type        DHCP type
 *
 * @return true if there were no DHCP activity, false otherwise
 */
static bool dhcp_device_is_dhcp_inactive(uint64_t v4counters[][DHCP_DIR_COUNT][DHCPv4_MESSAGE_TYPE_COUNT],
                                         uint64_t v6counters[][DHCP_DIR_COUNT][DHCPv6_MESSAGE_TYPE_COUNT],
                                         dhcp_type_t type)
{
    bool rv = true;
    uint64_t *rx_counters;
    uint64_t *rx_counter_snapshot;

    switch (type)
    {
    case DHCPv4_TYPE:
        rx_counters = v4counters[DHCP_COUNTERS_CURRENT][DHCP_RX];
        rx_counter_snapshot = v4counters[DHCP_COUNTERS_SNAPSHOT][DHCP_RX];
        for (uint8_t i = 0; (i < v4_monitored_msg_sz) && rv; i++) {
            rv = rx_counters[v4_monitored_msgs[i]] == rx_counter_snapshot[v4_monitored_msgs[i]];
        }
        break;

    case DHCPv6_TYPE:
        rx_counters = v6counters[DHCP_COUNTERS_CURRENT][DHCP_RX];
        rx_counter_snapshot = v6counters[DHCP_COUNTERS_SNAPSHOT][DHCP_RX];
        for (uint8_t i = 0; (i < v6_monitored_msg_sz) && rv; i++) {
            rv = rx_counters[v6_monitored_msgs[i]] == rx_counter_snapshot[v6_monitored_msgs[i]];
        }
        break;

    default:
        syslog(LOG_ERR, "Unknown DHCP type %d\n", type);
        break;
    }

    return rv;
}

/**
 * @code dhcp_device_is_dhcpv4_msg_unhealthy(type, counters);
 *
 * @brief Check if DHCP relay is functioning properly for message of type 'type'.
 *        For every rx of message 'type', there should be increment of the same message type.
 *
 * @param type      DHCP message type
 * @param counters  current/snapshot counter
 *
 * @return true if DHCP message 'type' is transmitted,false otherwise
 */
static bool dhcp_device_is_dhcpv4_msg_unhealthy(dhcpv4_message_type_t type,
                                                uint64_t v4counters[][DHCP_DIR_COUNT][DHCPv4_MESSAGE_TYPE_COUNT])
{
    // check if DHCP message 'type' is being relayed
    return ((v4counters[DHCP_COUNTERS_CURRENT][DHCP_RX][type] >  v4counters[DHCP_COUNTERS_SNAPSHOT][DHCP_RX][type]) &&
            (v4counters[DHCP_COUNTERS_CURRENT][DHCP_TX][type] <= v4counters[DHCP_COUNTERS_SNAPSHOT][DHCP_TX][type])    );
}

/**
 * @code dhcp_device_is_dhcpv6_msg_unhealthy(type, counters);
 *
 * @brief Check if DHCP relay is functioning properly for message of type 'type'.
 *        For every rx of message 'type', there should be increment of the same message type.
 *
 * @param type      DHCP message type
 * @param counters  current/snapshot counter
 *
 * @return true if DHCP message 'type' is transmitted,false otherwise
 */
static bool dhcp_device_is_dhcpv6_msg_unhealthy(dhcpv6_message_type_t type,
                                                uint64_t v6counters[][DHCP_DIR_COUNT][DHCPv6_MESSAGE_TYPE_COUNT])
{
    // check if DHCP message 'type' is being relayed
    return ((v6counters[DHCP_COUNTERS_CURRENT][DHCP_RX][type] >  v6counters[DHCP_COUNTERS_SNAPSHOT][DHCP_RX][type]) &&
            (v6counters[DHCP_COUNTERS_CURRENT][DHCP_TX][type] <= v6counters[DHCP_COUNTERS_SNAPSHOT][DHCP_TX][type])    );
}

/**
 * @code dhcp_device_check_positive_health(v4counters, v6counters, type);
 *
 * @brief Check if DHCPv4/6 relay is functioning properly for monitored messages.
 *        DHCPv4 (Discover, Offer, Request, ACK.) and DHCPv6 (Solicit, Advertise, Request, Reply).
 *        For every rx of monitored messages, there should be increment of the same message type.
 *
 * @param v4counters  current/snapshot counter
 *
 * @param v6counters  current/snapshot counter
 *
 * @param type        DHCP type
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
static dhcp_mon_status_t dhcp_device_check_positive_health(uint64_t v4counters[][DHCP_DIR_COUNT][DHCPv4_MESSAGE_TYPE_COUNT],
                                                           uint64_t v6counters[][DHCP_DIR_COUNT][DHCPv6_MESSAGE_TYPE_COUNT],
                                                           dhcp_type_t type)
{
    dhcp_mon_status_t rv = DHCP_MON_STATUS_HEALTHY;

    bool is_dhcp_unhealthy = false;

    switch (type)
    {
    case DHCPv4_TYPE:
        for (uint8_t i = 0; (i < v4_monitored_msg_sz) && !is_dhcp_unhealthy; i++) {
            is_dhcp_unhealthy = dhcp_device_is_dhcpv4_msg_unhealthy(v4_monitored_msgs[i], v4counters);
        }
        break;

    case DHCPv6_TYPE:
        for (uint8_t i = 0; (i < v6_monitored_msg_sz) && !is_dhcp_unhealthy; i++) {
            is_dhcp_unhealthy = dhcp_device_is_dhcpv6_msg_unhealthy(v6_monitored_msgs[i], v6counters);
        }
        break;

    default:
        syslog(LOG_ERR, "Unknown DHCP type %d\n", type);
            break;
    }

    // if we have rx DORA/SARR then we should have corresponding tx DORA/SARR (DORA/SARR being relayed)
    if (is_dhcp_unhealthy) {
        rv = DHCP_MON_STATUS_UNHEALTHY;
    }

    return rv;
}

/**
 * @code dhcp_device_check_negative_health(v4counters, v6counters, type);
 *
 * @brief Check that DHCP relayed messages are not being transmitted out of this interface/dev
 *        using its counters. The interface is negatively healthy if there are not DHCP message
 *        travelling through it.
 *
 * @param v4counters            current/snapshot counter
 * @param v6counters            current/snapshot counter
 * @param type                  DHCP type
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
static dhcp_mon_status_t dhcp_device_check_negative_health(uint64_t v4counters[][DHCP_DIR_COUNT][DHCPv4_MESSAGE_TYPE_COUNT],
                                                           uint64_t v6counters[][DHCP_DIR_COUNT][DHCPv6_MESSAGE_TYPE_COUNT],
                                                           dhcp_type_t type)
{
    dhcp_mon_status_t rv = DHCP_MON_STATUS_HEALTHY;
    bool is_dhcp_unhealthy = false;

    uint64_t *tx_counters;
    uint64_t *tx_counter_snapshot;

    switch (type)
    {
    case DHCPv4_TYPE:
        tx_counters = v4counters[DHCP_COUNTERS_CURRENT][DHCP_TX];
        tx_counter_snapshot = v4counters[DHCP_COUNTERS_SNAPSHOT][DHCP_TX];
        for (uint8_t i = 0; (i < v4_monitored_msg_sz) && !is_dhcp_unhealthy; i++) {
            is_dhcp_unhealthy = tx_counters[v4_monitored_msgs[i]] > tx_counter_snapshot[v4_monitored_msgs[i]];
        }
        break;
    case DHCPv6_TYPE:
        tx_counters = v6counters[DHCP_COUNTERS_CURRENT][DHCP_TX];
        tx_counter_snapshot = v6counters[DHCP_COUNTERS_SNAPSHOT][DHCP_TX];
        for (uint8_t i = 0; (i < v6_monitored_msg_sz) && !is_dhcp_unhealthy; i++) {
            is_dhcp_unhealthy = tx_counters[v6_monitored_msgs[i]] > tx_counter_snapshot[v6_monitored_msgs[i]];
        }
        break;
    default:
        syslog(LOG_ERR, "Unknown DHCP type %d\n", type);
            break;
    }

    // for negative validation, return unhealthy if DHCP packet are being
    // transmitted out of the device/interface
    if (is_dhcp_unhealthy) {
        rv = DHCP_MON_STATUS_UNHEALTHY;
    }

    return rv;
}

/**
 * @code dhcp_device_check_health(check_type, v4counters, v6counters, type);
 *
 * @brief Check that DHCP relay is functioning properly given a check type. Positive check
 *        indicates for every rx of DHCP message of type 'type', there would increment of
 *        the corresponding TX of the same message type. While negative check indicates the
 *        device should not be actively transmitting any DHCP messages. If it does, it is
 *        considered unhealthy.
 *
 * @param check_type    type of health check
 * @param v4counters    current/snapshot counters
 * @param v6counters    current/snapshot counters
 * @param type          DHCP type
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
static dhcp_mon_status_t dhcp_device_check_health(dhcp_mon_check_t check_type,
                                                  uint64_t v4counters[][DHCP_DIR_COUNT][DHCPv4_MESSAGE_TYPE_COUNT],
                                                  uint64_t v6counters[][DHCP_DIR_COUNT][DHCPv6_MESSAGE_TYPE_COUNT],
                                                  dhcp_type_t type)
{
    dhcp_mon_status_t rv = DHCP_MON_STATUS_HEALTHY;

    if (dhcp_device_is_dhcp_inactive(aggregate_dev.counters.v4counters, aggregate_dev.counters.v6counters, type)) {
        rv = DHCP_MON_STATUS_INDETERMINATE;
    } else if (check_type == DHCP_MON_CHECK_POSITIVE) {
        rv = dhcp_device_check_positive_health(v4counters, v6counters, type);
    } else if (check_type == DHCP_MON_CHECK_NEGATIVE) {
        rv = dhcp_device_check_negative_health(v4counters, v6counters, type);
    }

    return rv;
}

/**
 * @code dhcp_print_counters(vlan_intf, type, v4counters, v6counters);
 *
 * @brief prints DHCP counters to sylsog.
 *
 * @param vlan_intf     vlan interface name
 * @param type          counter type
 * @param v4counters    interface counter
 * @param v6counters    interface counter
 *
 * @return none
 */
static void dhcp_print_counters(const char *vlan_intf,
                                dhcp_counters_type_t type,
                                uint64_t v4counters[][DHCPv4_MESSAGE_TYPE_COUNT],
                                uint64_t v6counters[][DHCPv6_MESSAGE_TYPE_COUNT])
{
    static const char *v4_counter_desc[DHCP_COUNTERS_COUNT] = {
        [DHCP_COUNTERS_CURRENT] = " Current",
        [DHCP_COUNTERS_SNAPSHOT] = "Snapshot"
    };
    static const char *v6_counter_desc[DHCP_COUNTERS_COUNT] = {
        [DHCP_COUNTERS_CURRENT] = " Current",
        [DHCP_COUNTERS_SNAPSHOT] = "Snapshot"
    };

    syslog(
        LOG_NOTICE,
        "DHCPv4 [%*s-%*s rx/tx] Discover: %*lu/%*lu, Offer: %*lu/%*lu, Request: %*lu/%*lu, ACK: %*lu/%*lu\n\
         DHCPv6 [%*s-%*s rx/tx] Solicit: %*lu/%*lu, Advertise: %*lu/%*lu, Request: %*lu/%*lu, Reply: %*lu/%*lu\n",
        IF_NAMESIZE, vlan_intf,
        (int) strlen(v4_counter_desc[type]), v4_counter_desc[type],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_RX][DHCPv4_MESSAGE_TYPE_DISCOVER],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_TX][DHCPv4_MESSAGE_TYPE_DISCOVER],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_RX][DHCPv4_MESSAGE_TYPE_OFFER],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_TX][DHCPv4_MESSAGE_TYPE_OFFER],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_RX][DHCPv4_MESSAGE_TYPE_REQUEST],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_TX][DHCPv4_MESSAGE_TYPE_REQUEST],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_RX][DHCPv4_MESSAGE_TYPE_ACK],
        DHCP_COUNTER_WIDTH, v4counters[DHCP_TX][DHCPv4_MESSAGE_TYPE_ACK],
        IF_NAMESIZE, vlan_intf,
        (int) strlen(v6_counter_desc[type]), v6_counter_desc[type],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_RX][DHCPv6_MESSAGE_TYPE_SOLICIT],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_TX][DHCPv6_MESSAGE_TYPE_SOLICIT],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_RX][DHCPv6_MESSAGE_TYPE_ADVERTISE],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_TX][DHCPv6_MESSAGE_TYPE_ADVERTISE],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_RX][DHCPv6_MESSAGE_TYPE_REQUEST],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_TX][DHCPv6_MESSAGE_TYPE_REQUEST],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_RX][DHCPv6_MESSAGE_TYPE_REPLY],
        DHCP_COUNTER_WIDTH, v6counters[DHCP_TX][DHCPv6_MESSAGE_TYPE_REPLY]
    );
}

/**
 * @code init_socket(context, intf);
 *
 * @brief initializes socket, bind it to interface and bpf program, and
 *        associate with libevent base
 *
 * @param context           pointer to device (interface) context
 * @param intf              interface name
 *
 * @return 0 on success, otherwise for failure
 */
static int init_socket(dhcp_device_context_t *context, const char *intf)
{
    int rv = -1;

    do {
        context->sock = socket(AF_PACKET, SOCK_RAW | SOCK_NONBLOCK, htons(ETH_P_ALL));
        if (context->sock < 0) {
            syslog(LOG_ALERT, "socket: failed to open socket with '%s'\n", strerror(errno));
            break;
        }

        struct sockaddr_ll addr;
        memset(&addr, 0, sizeof(addr));
        addr.sll_ifindex = if_nametoindex(intf);
        addr.sll_family = AF_PACKET;
        addr.sll_protocol = htons(ETH_P_ALL);
        if (bind(context->sock, (struct sockaddr *) &addr, sizeof(addr))) {
            syslog(LOG_ALERT, "bind: failed to bind to interface '%s' with '%s'\n", intf, strerror(errno));
            break;
        }

        strncpy(context->intf, intf, sizeof(context->intf) - 1);
        context->intf[sizeof(context->intf) - 1] = '\0';

        rv = 0;
    } while (0);

    return rv;
}

/**
 * @code initialize_intf_mac_and_ip_addr(context);
 *
 * @brief initializes device (interface) mac/ip addresses
 *
 * @param context           pointer to device (interface) context
 *
 * @return 0 on success, otherwise for failure
 */
int initialize_intf_mac_and_ip_addr(dhcp_device_context_t *context)
{
    int rv = -1;

    do {
        int fd;
        struct ifreq ifr;
        if ((fd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
            syslog(LOG_ALERT, "socket: %s", strerror(errno));
            break;
        }

        ifr.ifr_addr.sa_family = AF_INET;
        strncpy(ifr.ifr_name, context->intf, sizeof(ifr.ifr_name) - 1);
        ifr.ifr_name[sizeof(ifr.ifr_name) - 1] = '\0';

        // Get v4 network address
        if (ioctl(fd, SIOCGIFADDR, &ifr) == -1) {
            syslog(LOG_ALERT, "ioctl: %s", explain_ioctl(fd, SIOCGIFADDR, &ifr));
            break;
        }
        context->ipv4 = ((struct sockaddr_in*) &ifr.ifr_addr)->sin_addr.s_addr;

        // Get mac address
        if (ioctl(fd, SIOCGIFHWADDR, &ifr) == -1) {
            syslog(LOG_ALERT, "ioctl: %s", explain_ioctl(fd, SIOCGIFHWADDR, &ifr));
            break;
        }
        memcpy(context->mac, ifr.ifr_hwaddr.sa_data, sizeof(context->mac));

        close(fd);

        // Get v6 network address
        memset(&context->ipv6, 0, sizeof(context->ipv6));
        struct ifaddrs *ifa, *ifa_tmp;

        if (getifaddrs(&ifa) == -1) {
            syslog(LOG_ALERT, "getifaddrs failed");
            break;
        }

        ifa_tmp = ifa;
        while (ifa_tmp) {
            // Check if current interface has a valid IPv6 address (not link local address)
            if ((strncmp(ifa_tmp->ifa_name, context->intf, sizeof(context->intf)) == 0) &&
                (ifa_tmp->ifa_addr) &&
                (ifa_tmp->ifa_addr->sa_family == AF_INET6) &&
                (((struct sockaddr_in6*)(ifa_tmp->ifa_addr))->sin6_addr.__in6_u.__u6_addr16[0] != IPV6_LINK_LOCAL_PREFIX)) {

                struct sockaddr_in6 *in6 = (struct sockaddr_in6*) ifa_tmp->ifa_addr;
                memcpy(&context->ipv6, &in6->sin6_addr, sizeof(context->ipv6));
            }
            ifa_tmp = ifa_tmp->ifa_next;
        }
        freeifaddrs(ifa);

        rv = 0;
    } while (0);

    return rv;
}

/**
 * @code dhcp_device_get_ipv4(context);
 *
 * @brief Accessor method
 *
 * @param context       pointer to device (interface) context
 *
 * @return interface IPv4
 */
int dhcp_device_get_ipv4(dhcp_device_context_t *context, in_addr_t *ip)
{
    int rv = -1;

    if (context != NULL && ip != NULL) {
        *ip = context->ipv4;
        rv = 0;
    }

    return rv;
}

/**
 * @code dhcp_device_get_ipv6(context);
 *
 * @brief Accessor method
 *
 * @param context       pointer to device (interface) context
 *
 * @return interface IPv6
 */
int dhcp_device_get_ipv6(dhcp_device_context_t *context, struct in6_addr *ip)
{
    int rv = -1;

    if (context != NULL && ip != NULL) {
        *ip = context->ipv6;
        rv = 0;
    }

    return rv;
}

/**
 * @code dhcp_device_get_aggregate_context();
 *
 * @brief Accessor method
 *
 * @return pointer to aggregate device (interface) context
 */
dhcp_device_context_t* dhcp_device_get_aggregate_context()
{
    return &aggregate_dev;
}

/**
 * @code dhcp_device_init(context, intf, is_uplink);
 *
 * @brief initializes device (interface) that handles packet capture per interface.
 */
int dhcp_device_init(dhcp_device_context_t **context, const char *intf, uint8_t is_uplink)
{
    int rv = -1;
    dhcp_device_context_t *dev_context = NULL;

    if ((context != NULL) && (strlen(intf) < sizeof(dev_context->intf))) {

        dev_context = (dhcp_device_context_t *) malloc(sizeof(dhcp_device_context_t));
        if (dev_context != NULL) {
            if ((init_socket(dev_context, intf) == 0) &&
                (initialize_intf_mac_and_ip_addr(dev_context) == 0)) {

                dev_context->is_uplink = is_uplink;

                memset(dev_context->counters.v4counters, 0, sizeof(dev_context->counters.v4counters));
                memset(dev_context->counters.v6counters, 0, sizeof(dev_context->counters.v6counters));

                *context = dev_context;
                rv = 0;
            }
        }
        else {
            syslog(LOG_ALERT, "malloc: failed to allocated device context memory for '%s'", dev_context->intf);
        }
    }

    return rv;
}

/**
 * @code dhcp_device_start_capture(context, snaplen, base, giaddr_ip, v6_vlan_ip);
 *
 * @brief starts packet capture on this interface
 */
int dhcp_device_start_capture(dhcp_device_context_t *context,
                              size_t snaplen,
                              struct event_base *base,
                              in_addr_t giaddr_ip,
                              struct in6_addr v6_vlan_ip)
{
    int rv = -1;

    do {
        if (context == NULL) {
            syslog(LOG_ALERT, "NULL interface context pointer'\n");
            break;
        }

        // snaplen check for DHCPv4 size
        if (dhcpv4_enabled && snaplen < UDPv4_START_OFFSET + sizeof(struct udphdr) + DHCPv4_OPTIONS_HEADER_SIZE) {
            syslog(LOG_ALERT, "dhcp_device_start_capture(%s): snap length is too low to capture DHCPv4 options", context->intf);
            break;
        }

        // snaplen check for DHCPv6 size - DHCPv6 message type is the first byte of the udp payload
        if (dhcpv6_enabled && snaplen < DHCPv6_START_OFFSET + 1) {
            syslog(LOG_ALERT, "dhcp_device_start_capture(%s): snap length is too low to capture DHCPv6 option", context->intf);
            break;
        }

        context->giaddr_ip = giaddr_ip;
        context->v6_vlan_ip = v6_vlan_ip;

        context->buffer = (uint8_t *) malloc(snaplen);
        if (context->buffer == NULL) {
            syslog(LOG_ALERT, "malloc: failed to allocate memory for socket buffer '%s'\n", strerror(errno));
            break;
        }
        context->snaplen = snaplen;

        if (setsockopt(context->sock, SOL_SOCKET, SO_ATTACH_FILTER, &dhcp_sock_bfp, sizeof(dhcp_sock_bfp)) != 0) {
            syslog(LOG_ALERT, "setsockopt: failed to attach filter with '%s'\n", strerror(errno));
            break;
        }

        struct event *ev = event_new(base, context->sock, EV_READ | EV_PERSIST, read_callback, context);
        if (ev == NULL) {
            syslog(LOG_ALERT, "event_new: failed to allocate memory for libevent event '%s'\n", strerror(errno));
            break;
        }
        event_add(ev, NULL);

        rv = 0;
    } while (0);

    return rv;
}

/**
 * @code dhcp_device_shutdown(context);
 *
 * @brief shuts down device (interface). Also, stops packet capture on interface and cleans up any allocated memory
 */
void dhcp_device_shutdown(dhcp_device_context_t *context)
{
    free(context);
}

/**
 * @code dhcp_device_get_status(check_type, context, type);
 *
 * @brief collects DHCP relay status info for a given interface. If context is null, it will report aggregate
 *        status
 */
dhcp_mon_status_t dhcp_device_get_status(dhcp_mon_check_t check_type, dhcp_device_context_t *context, dhcp_type_t type)
{
    dhcp_mon_status_t rv = DHCP_MON_STATUS_HEALTHY;

    if (context != NULL) {
        rv = dhcp_device_check_health(check_type, context->counters.v4counters, context->counters.v6counters, type);
    }

    return rv;
}

/**
 * @code dhcp_device_update_snapshot(context);
 *
 * @brief Update device/interface counters snapshot
 */
void dhcp_device_update_snapshot(dhcp_device_context_t *context)
{
    if (context != NULL) {
        if (dhcpv4_enabled) {
            memcpy(context->counters.v4counters[DHCP_COUNTERS_SNAPSHOT],
                context->counters.v4counters[DHCP_COUNTERS_CURRENT],
                sizeof(context->counters.v4counters[DHCP_COUNTERS_SNAPSHOT]));
        }

        if (dhcpv6_enabled) {
            memcpy(context->counters.v6counters[DHCP_COUNTERS_SNAPSHOT],
                context->counters.v6counters[DHCP_COUNTERS_CURRENT],
                sizeof(context->counters.v6counters[DHCP_COUNTERS_SNAPSHOT]));
        }
    }
}

/**
 * @code dhcp_device_print_status(context, type);
 *
 * @brief prints status counters to syslog.
 */
void dhcp_device_print_status(dhcp_device_context_t *context, dhcp_counters_type_t type)
{
    if (context != NULL) {
        dhcp_print_counters(context->intf, type, context->counters.v4counters[type], context->counters.v6counters[type]);
    }
}

/**
 * @code dhcp_device_active_types(dhcpv4, dhcpv6);
 *
 * @brief update local variables with active protocols
 */
void dhcp_device_active_types(bool dhcpv4, bool dhcpv6)
{
    dhcpv4_enabled = dhcpv4;
    dhcpv6_enabled = dhcpv6;
}