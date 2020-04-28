/**
 * @file dhcp_device.c
 *
 *  device (interface) module
 */

#include <err.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
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

#include "dhcp_device.h"

/** Start of Ether header of a captured frame */
#define ETHER_START_OFFSET  0
/** Start of IP header of a captured frame */
#define IP_START_OFFSET (ETHER_START_OFFSET + ETHER_HDR_LEN)
/** Start of UDP header of a captured frame */
#define UDP_START_OFFSET (IP_START_OFFSET + sizeof(struct ip))
/** Start of DHCP header of a captured frame */
#define DHCP_START_OFFSET (UDP_START_OFFSET + sizeof(struct udphdr))
/** Start of DHCP Options segment of a captured frame */
#define DHCP_OPTIONS_HEADER_SIZE 240
/** Offset of DHCP GIADDR */
#define DHCP_GIADDR_OFFSET 24

/**
 * DHCP message types
 **/
typedef enum
{
    DHCP_MESSAGE_TYPE_DISCOVER = 1,
    DHCP_MESSAGE_TYPE_OFFER    = 2,
    DHCP_MESSAGE_TYPE_REQUEST  = 3,
    DHCP_MESSAGE_TYPE_DECLINE  = 4,
    DHCP_MESSAGE_TYPE_ACK      = 5,
    DHCP_MESSAGE_TYPE_NAK      = 6,
    DHCP_MESSAGE_TYPE_RELEASE  = 7,
    DHCP_MESSAGE_TYPE_INFORM   = 8
} dhcp_message_type;

#define OP_LDHA     (BPF_LD  | BPF_H   | BPF_ABS)   /** bpf ldh Abs */
#define OP_LDHI     (BPF_LD  | BPF_H   | BPF_IND)   /** bpf ldh Ind */
#define OP_LDB      (BPF_LD  | BPF_B   | BPF_ABS)   /** bpf ldb Abs*/
#define OP_JEQ      (BPF_JMP | BPF_JEQ | BPF_K)     /** bpf jeq */
#define OP_JGT      (BPF_JMP | BPF_JGT | BPF_K)     /** bpf jgt */
#define OP_RET      (BPF_RET | BPF_K)               /** bpf ret */
#define OP_JSET     (BPF_JMP | BPF_JSET | BPF_K)    /** bpf jset */
#define OP_LDXB     (BPF_LDX | BPF_B    | BPF_MSH)  /** bpf ldxb */

/** Berkeley Packet Filter program for "udp and (port 67 or port 68)".
 * This program is obtained using the following command tcpdump:
 * `tcpdump -dd "udp and (port 67 or port 68)"`
 */
static struct sock_filter dhcp_bpf_code[] = {
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x0000000c}, // (000) ldh      [12]
    {.code = OP_JEQ,  .jt = 0,  .jf = 7,  .k = 0x000086dd}, // (001) jeq      #0x86dd          jt 2	jf 9
    {.code = OP_LDB,  .jt = 0,  .jf = 0,  .k = 0x00000014}, // (002) ldb      [20]
    {.code = OP_JEQ,  .jt = 0,  .jf = 18, .k = 0x00000011}, // (003) jeq      #0x11            jt 4	jf 22
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x00000036}, // (004) ldh      [54]
    {.code = OP_JEQ,  .jt = 15, .jf = 0,  .k = 0x00000043}, // (005) jeq      #0x43            jt 21	jf 6
    {.code = OP_JEQ,  .jt = 14, .jf = 0,  .k = 0x00000044}, // (006) jeq      #0x44            jt 21	jf 7
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x00000038}, // (007) ldh      [56]
    {.code = OP_JEQ,  .jt = 12, .jf = 11, .k = 0x00000043}, // (008) jeq      #0x43            jt 21	jf 20
    {.code = OP_JEQ,  .jt = 0,  .jf = 12, .k = 0x00000800}, // (009) jeq      #0x800           jt 10	jf 22
    {.code = OP_LDB,  .jt = 0,  .jf = 0,  .k = 0x00000017}, // (010) ldb      [23]
    {.code = OP_JEQ,  .jt = 0,  .jf = 10, .k = 0x00000011}, // (011) jeq      #0x11            jt 12	jf 22
    {.code = OP_LDHA, .jt = 0,  .jf = 0,  .k = 0x00000014}, // (012) ldh      [20]
    {.code = OP_JSET, .jt = 8,  .jf = 0,  .k = 0x00001fff}, // (013) jset     #0x1fff          jt 22	jf 14
    {.code = OP_LDXB, .jt = 0,  .jf = 0,  .k = 0x0000000e}, // (014) ldxb     4*([14]&0xf)
    {.code = OP_LDHI, .jt = 0,  .jf = 0,  .k = 0x0000000e}, // (015) ldh      [x + 14]
    {.code = OP_JEQ,  .jt = 4,  .jf = 0,  .k = 0x00000043}, // (016) jeq      #0x43            jt 21	jf 17
    {.code = OP_JEQ,  .jt = 3,  .jf = 0,  .k = 0x00000044}, // (017) jeq      #0x44            jt 21	jf 18
    {.code = OP_LDHI, .jt = 0,  .jf = 0,  .k = 0x00000010}, // (018) ldh      [x + 16]
    {.code = OP_JEQ,  .jt = 1,  .jf = 0,  .k = 0x00000043}, // (019) jeq      #0x43            jt 21	jf 20
    {.code = OP_JEQ,  .jt = 0,  .jf = 1,  .k = 0x00000044}, // (020) jeq      #0x44            jt 21	jf 22
    {.code = OP_RET,  .jt = 0,  .jf = 0,  .k = 0x00040000}, // (021) ret      #262144
    {.code = OP_RET,  .jt = 0,  .jf = 0,  .k = 0x00000000}, // (022) ret      #0
};

/** Filter program socket struct */
static struct sock_fprog dhcp_sock_bfp = {
    .len = sizeof(dhcp_bpf_code) / sizeof(*dhcp_bpf_code), .filter = dhcp_bpf_code
};

/** global aggregate counter for DHCP interfaces */
static dhcp_device_counters_t glob_counters[DHCP_DIR_COUNT] = {
    [DHCP_RX] = {.discover = 0, .offer = 0, .request = 0, .ack = 0},
    [DHCP_TX] = {.discover = 0, .offer = 0, .request = 0, .ack = 0},
};

/** global aggregate counter snapshot for DHCP interfaces */
static dhcp_device_counters_t glob_counters_snapshot[DHCP_DIR_COUNT] = {
    [DHCP_RX] = {.discover = 0, .offer = 0, .request = 0, .ack = 0},
    [DHCP_TX] = {.discover = 0, .offer = 0, .request = 0, .ack = 0},
};

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
    case DHCP_MESSAGE_TYPE_DISCOVER:
        giaddr = ntohl(dhcphdr[DHCP_GIADDR_OFFSET] << 24 | dhcphdr[DHCP_GIADDR_OFFSET + 1] << 16 |
                       dhcphdr[DHCP_GIADDR_OFFSET + 2] << 8 | dhcphdr[DHCP_GIADDR_OFFSET + 3]);
        context->counters[dir].discover++;
        if ((context->vlan_ip == giaddr && context->is_uplink && dir == DHCP_TX) ||
            (!context->is_uplink && dir == DHCP_RX && iphdr->ip_dst.s_addr == INADDR_BROADCAST)) {
            glob_counters[dir].discover++;
        }
        break;
    case DHCP_MESSAGE_TYPE_OFFER:
        context->counters[dir].offer++;
        if ((context->vlan_ip == iphdr->ip_dst.s_addr && context->is_uplink && dir == DHCP_RX) ||
            (!context->is_uplink && dir == DHCP_TX)) {
            glob_counters[dir].offer++;
        }
        break;
    case DHCP_MESSAGE_TYPE_REQUEST:
        giaddr = ntohl(dhcphdr[DHCP_GIADDR_OFFSET] << 24 | dhcphdr[DHCP_GIADDR_OFFSET + 1] << 16 |
                       dhcphdr[DHCP_GIADDR_OFFSET + 2] << 8 | dhcphdr[DHCP_GIADDR_OFFSET + 3]);
        context->counters[dir].request++;
        if ((context->vlan_ip == giaddr && context->is_uplink && dir == DHCP_TX) ||
            (!context->is_uplink && dir == DHCP_RX && iphdr->ip_dst.s_addr == INADDR_BROADCAST)) {
            glob_counters[dir].request++;
        }
        break;
    case DHCP_MESSAGE_TYPE_ACK:
        context->counters[dir].ack++;
        if ((context->vlan_ip == iphdr->ip_dst.s_addr && context->is_uplink && dir == DHCP_RX) ||
            (!context->is_uplink && dir == DHCP_TX)) {
            glob_counters[dir].ack++;
        }
        break;
    case DHCP_MESSAGE_TYPE_DECLINE:
    case DHCP_MESSAGE_TYPE_NAK:
    case DHCP_MESSAGE_TYPE_RELEASE:
    case DHCP_MESSAGE_TYPE_INFORM:
        break;
    default:
        syslog(LOG_WARNING, "handle_dhcp_option_53(%s): Unknown DHCP option 53 type %d", context->intf, dhcp_option[2]);
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
        struct ip *iphdr = (struct ip*) (context->buffer + IP_START_OFFSET);
        struct udphdr *udp = (struct udphdr*) (context->buffer + UDP_START_OFFSET);
        uint8_t *dhcphdr = context->buffer + DHCP_START_OFFSET;
        int dhcp_option_offset = DHCP_START_OFFSET + DHCP_OPTIONS_HEADER_SIZE;

        if ((buffer_sz > UDP_START_OFFSET + sizeof(struct udphdr) + DHCP_OPTIONS_HEADER_SIZE) &&
            (ntohs(udp->len) > DHCP_OPTIONS_HEADER_SIZE)) {
            int dhcp_sz = ntohs(udp->len) < buffer_sz - UDP_START_OFFSET - sizeof(struct udphdr) ?
                          ntohs(udp->len) : buffer_sz - UDP_START_OFFSET - sizeof(struct udphdr);
            int dhcp_option_sz = dhcp_sz - DHCP_OPTIONS_HEADER_SIZE;
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
        } else {
            syslog(LOG_WARNING, "read_callback(%s): read length (%ld) is too small to capture DHCP options",
                   context->intf, buffer_sz);
        }
    }
}

/**
 * @code dhcp_device_validate(counters, counters_snapshot);
 *
 * @brief validate current interface counters by comparing aggregate counter with snapshot counters.
 *
 * @param counters              recent interface counter
 * @param counters_snapshot     snapshot counters
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
static dhcp_mon_status_t dhcp_device_validate(dhcp_device_counters_t *counters,
                                              dhcp_device_counters_t *counters_snapshot)
{
    dhcp_mon_status_t rv = DHCP_MON_STATUS_HEALTHY;

    if ((counters[DHCP_RX].discover == counters_snapshot[DHCP_RX].discover) &&
        (counters[DHCP_RX].offer    == counters_snapshot[DHCP_RX].offer   ) &&
        (counters[DHCP_RX].request  == counters_snapshot[DHCP_RX].request ) &&
        (counters[DHCP_RX].ack      == counters_snapshot[DHCP_RX].ack     )    ) {
        rv = DHCP_MON_STATUS_INDETERMINATE;
    } else {
        // if we have rx DORA then we should have corresponding tx DORA (DORA being relayed)
        if (((counters[DHCP_RX].discover >  counters_snapshot[DHCP_RX].discover) &&
             (counters[DHCP_TX].discover <= counters_snapshot[DHCP_TX].discover)    ) ||
            ((counters[DHCP_RX].offer    > counters_snapshot[DHCP_RX].offer    ) &&
             (counters[DHCP_TX].offer    <= counters_snapshot[DHCP_TX].offer   )    ) ||
            ((counters[DHCP_RX].request  > counters_snapshot[DHCP_RX].request  ) &&
             (counters[DHCP_TX].request  <= counters_snapshot[DHCP_TX].request )    ) ||
            ((counters[DHCP_RX].ack      > counters_snapshot[DHCP_RX].ack      ) &&
             (counters[DHCP_TX].ack      <= counters_snapshot[DHCP_TX].ack     )    )    ) {
            rv = DHCP_MON_STATUS_UNHEALTHY;
        }
    }

    return rv;
}

/**
 * @code dhcp_print_counters(counters);
 *
 * @brief prints DHCP counters to sylsog.
 *
 * @param counters  interface counter
 */
static void dhcp_print_counters(dhcp_device_counters_t *counters)
{
    syslog(LOG_NOTICE, "DHCP Discover rx: %lu, tx:%lu, Offer rx: %lu, tx:%lu, Request rx: %lu, tx:%lu, ACK rx: %lu, tx:%lu\n",
           counters[DHCP_RX].discover, counters[DHCP_TX].discover,
           counters[DHCP_RX].offer, counters[DHCP_TX].offer,
           counters[DHCP_RX].request, counters[DHCP_TX].request,
           counters[DHCP_RX].ack, counters[DHCP_TX].ack);
}

/**
 * @code init_socket(context, intf);
 *
 * @brief initializes socket, bind it to interface and bpf prgram, and
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
static int initialize_intf_mac_and_ip_addr(dhcp_device_context_t *context)
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

        // Get network address
        if (ioctl(fd, SIOCGIFADDR, &ifr) == -1) {
            syslog(LOG_ALERT, "ioctl: %s", explain_ioctl(fd, SIOCGIFADDR, &ifr));
            break;
        }
        context->ip = ((struct sockaddr_in*) &ifr.ifr_addr)->sin_addr.s_addr;

        // Get mac address
        if (ioctl(fd, SIOCGIFHWADDR, &ifr) == -1) {
            syslog(LOG_ALERT, "ioctl: %s", explain_ioctl(fd, SIOCGIFHWADDR, &ifr));
            break;
        }
        memcpy(context->mac, ifr.ifr_hwaddr.sa_data, sizeof(context->mac));

        close(fd);

        rv = 0;
    } while (0);

    return rv;
}

/**
 * @code dhcp_device_get_ip(context);
 *
 * @brief Accessor method
 *
 * @param context       pointer to device (interface) context
 *
 * @return interface IP
 */
int dhcp_device_get_ip(dhcp_device_context_t *context, in_addr_t *ip)
{
    int rv = -1;

    if (context != NULL && ip != NULL) {
        *ip = context->ip;
        rv = 0;
    }

    return rv;
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

                memset(&dev_context->counters, 0, sizeof(dev_context->counters));
                memset(&dev_context->counters_snapshot, 0, sizeof(dev_context->counters_snapshot));

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
 * @code dhcp_device_start_capture(context, snaplen, base, vlan_ip);
 *
 * @brief starts packet capture on this interface
 */
int dhcp_device_start_capture(dhcp_device_context_t *context,
                              size_t snaplen,
                              struct event_base *base,
                              in_addr_t vlan_ip)
{
    int rv = -1;

    do {
        if (context == NULL) {
            syslog(LOG_ALERT, "NULL interface context pointer'\n");
            break;
        }

        if (snaplen < UDP_START_OFFSET + sizeof(struct udphdr) + DHCP_OPTIONS_HEADER_SIZE) {
            syslog(LOG_ALERT, "dhcp_device_start_capture(%s): snap length is too low to capture DHCP options", context->intf);
            break;
        }

        context->vlan_ip = vlan_ip;

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
 * @code dhcp_device_get_status(context);
 *
 * @brief collects DHCP relay status info for a given interface. If context is null, it will report aggregate
 *        status
 */
dhcp_mon_status_t dhcp_device_get_status(dhcp_device_context_t *context)
{
    dhcp_mon_status_t rv = 0;

    if (context != NULL) {
        rv = dhcp_device_validate(context->counters, context->counters_snapshot);
        memcpy(context->counters_snapshot, context->counters, sizeof(context->counters_snapshot));
    } else {
        rv = dhcp_device_validate(glob_counters, glob_counters_snapshot);
        memcpy(glob_counters_snapshot, glob_counters, sizeof(glob_counters_snapshot));
    }

    return rv;
}

/**
 * @code dhcp_device_print_status();
 *
 * @brief prints status counters to syslog. If context is null, it will print aggregate status
 */
void dhcp_device_print_status(dhcp_device_context_t *context)
{
    if (context != NULL) {
        dhcp_print_counters(context->counters);
    } else {
        dhcp_print_counters(glob_counters);
    }
}
