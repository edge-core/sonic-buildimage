/**
 * @file dhcp_device.h
 *
 *  device (interface) module
 */

#ifndef DHCP_DEVICE_H_
#define DHCP_DEVICE_H_

#include <stdint.h>
#include <net/if.h>
#include <netinet/in.h>
#include <net/ethernet.h>

#include <event2/listener.h>
#include <event2/bufferevent.h>
#include <event2/buffer.h>


/**
 * DHCPv4 message types
 **/
typedef enum
{
    DHCPv4_MESSAGE_TYPE_DISCOVER = 1,
    DHCPv4_MESSAGE_TYPE_OFFER    = 2,
    DHCPv4_MESSAGE_TYPE_REQUEST  = 3,
    DHCPv4_MESSAGE_TYPE_DECLINE  = 4,
    DHCPv4_MESSAGE_TYPE_ACK      = 5,
    DHCPv4_MESSAGE_TYPE_NAK      = 6,
    DHCPv4_MESSAGE_TYPE_RELEASE  = 7,
    DHCPv4_MESSAGE_TYPE_INFORM   = 8,

    DHCPv4_MESSAGE_TYPE_COUNT
} dhcpv4_message_type_t;

/**
 * DHCPv6 message types
 **/
typedef enum
{
    DHCPv6_MESSAGE_TYPE_SOLICIT             = 1,
    DHCPv6_MESSAGE_TYPE_ADVERTISE           = 2,
    DHCPv6_MESSAGE_TYPE_REQUEST             = 3,
    DHCPv6_MESSAGE_TYPE_CONFIRM             = 4,
    DHCPv6_MESSAGE_TYPE_RENEW               = 5,
    DHCPv6_MESSAGE_TYPE_REBIND              = 6,
    DHCPv6_MESSAGE_TYPE_REPLY               = 7,
    DHCPv6_MESSAGE_TYPE_RELEASE             = 8,
    DHCPv6_MESSAGE_TYPE_DECLINE             = 9,
    DHCPv6_MESSAGE_TYPE_RECONFIGURE         = 10,
    DHCPv6_MESSAGE_TYPE_INFORMATION_REQUEST = 11,
    DHCPv6_MESSAGE_TYPE_RELAY_FORWARD       = 12,
    DHCPv6_MESSAGE_TYPE_RELAY_REPLY         = 13,

    DHCPv6_MESSAGE_TYPE_COUNT
} dhcpv6_message_type_t;

/** packet direction */
typedef enum
{
    DHCP_RX,    /** RX DHCP packet */
    DHCP_TX,    /** TX DHCP packet */

    DHCP_DIR_COUNT
} dhcp_packet_direction_t;

/** counters type */
typedef enum
{
    DHCP_COUNTERS_CURRENT,      /** DHCP current counters */
    DHCP_COUNTERS_SNAPSHOT,     /** DHCP snapshot counters */

    DHCP_COUNTERS_COUNT
} dhcp_counters_type_t;

/** dhcp health status */
typedef enum
{
    DHCP_MON_STATUS_HEALTHY,        /** DHCP relay is healthy */
    DHCP_MON_STATUS_UNHEALTHY,      /** DHCP relay is unhealthy and is missing out on some packets */
    DHCP_MON_STATUS_INDETERMINATE,  /** DHCP relay health could not be determined */
} dhcp_mon_status_t;

/** dhcp type */
typedef enum
{
    DHCPv4_TYPE,
    DHCPv6_TYPE,
} dhcp_type_t;

/** dhcp check type */
typedef enum
{
    DHCP_MON_CHECK_NEGATIVE,    /** Presence of relayed DHCP packets activity is flagged as unhealthy state */
    DHCP_MON_CHECK_POSITIVE,    /** Validate that received DORA packets are relayed */
} dhcp_mon_check_t;

typedef struct
{
    uint64_t v4counters[DHCP_COUNTERS_COUNT][DHCP_DIR_COUNT][DHCPv4_MESSAGE_TYPE_COUNT];
                                    /** current/snapshot counters of DHCPv4 packets */
    uint64_t v6counters[DHCP_COUNTERS_COUNT][DHCP_DIR_COUNT][DHCPv6_MESSAGE_TYPE_COUNT];
                                    /** current/snapshot counters of DHCPv6 packets */
} counters_t;

/** DHCP device (interface) context */
typedef struct
{
    int sock;                       /** Raw socket associated with this device/interface */
    in_addr_t ipv4;                 /** ipv4 network address of this device (interface) */
    struct in6_addr ipv6;           /** ipv6 network address of this device (interface) */
    uint8_t mac[ETHER_ADDR_LEN];    /** hardware address of this device (interface) */
    in_addr_t giaddr_ip;            /** Gateway IPv4 address */
    struct in6_addr v6_vlan_ip;     /** Vlan IPv6 address */
    uint8_t is_uplink;              /** north interface? */
    char intf[IF_NAMESIZE];         /** device (interface) name */
    uint8_t *buffer;                /** buffer used to read socket data */
    size_t snaplen;                 /** snap length or buffer size */
    counters_t counters;            /** counters for DHCPv4/6 packets */
} dhcp_device_context_t;

/**
 * @code initialize_intf_mac_and_ip_addr(context);
 *
 * @brief initializes device (interface) mac/ip addresses
 *
 * @param context           pointer to device (interface) context
 *
 * @return 0 on success, otherwise for failure
 */
int initialize_intf_mac_and_ip_addr(dhcp_device_context_t *context);

/**
 * @code dhcp_device_get_ipv4(context, ip);
 *
 * @brief Accessor method
 *
 * @param context       pointer to device (interface) context
 * @param ip(out)       pointer to device IPv4
 *
 * @return 0 on success, otherwise for failure
 */
int dhcp_device_get_ipv4(dhcp_device_context_t *context, in_addr_t *ip);

/**
 * @code dhcp_device_get_ipv6(context, ip);
 *
 * @brief Accessor method
 *
 * @param context       pointer to device (interface) context
 * @param ip(out)       pointer to device IPv6
 *
 * @return 0 on success, otherwise for failure
 */
int dhcp_device_get_ipv6(dhcp_device_context_t *context, struct in6_addr *ip);

/**
 * @code dhcp_device_get_aggregate_context();
 *
 * @brief Accessor method
 *
 * @return pointer to aggregate device (interface) context
 */
dhcp_device_context_t* dhcp_device_get_aggregate_context();

/**
 * @code dhcp_device_init(context, intf, is_uplink);
 *
 * @brief initializes device (interface) that handles packet capture per interface.
 *
 * @param context(inout)    pointer to device (interface) context
 * @param intf              interface name
 * @param is_uplink         uplink interface
 *
 * @return 0 on success, otherwise for failure
 */
int dhcp_device_init(dhcp_device_context_t **context,
                     const char *intf,
                     uint8_t is_uplink);

/**
 * @code dhcp_device_start_capture(context, snaplen, base, giaddr_ip, v6_vlan_ip);
 *
 * @brief starts packet capture on this interface
 *
 * @param context           pointer to device (interface) context
 * @param snaplen           length of packet capture
 * @param base              pointer to libevent base
 * @param giaddr_ip         gateway IP address
 * @param v6_vlan_ip        vlan IPv6 address
 *
 * @return 0 on success, otherwise for failure
 */
int dhcp_device_start_capture(dhcp_device_context_t *context,
                              size_t snaplen,
                              struct event_base *base,
                              in_addr_t giaddr_ip,
                              struct in6_addr v6_vlan_ip);

/**
 * @code dhcp_device_shutdown(context);
 *
 * @brief shuts down device (interface). Also, stops packet capture on interface and cleans up any allocated memory
 *
 * @param context   Device (interface) context
 *
 * @return nonedhcp_device_shutdown
 */
void dhcp_device_shutdown(dhcp_device_context_t *context);

/**
 * @code dhcp_device_get_status(check_type, context, type);
 *
 * @brief collects DHCP relay status info for a given interface. If context is null, it will report aggregate
 *        status
 *
 * @param check_type        Type of validation
 * @param context           Device (interface) context
 * @param type              DHCP type
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
dhcp_mon_status_t dhcp_device_get_status(dhcp_mon_check_t check_type, dhcp_device_context_t *context, dhcp_type_t type);

/**
 * @code dhcp_device_update_snapshot(context);
 *
 * @param context   Device (interface) context
 *
 * @brief Update device/interface counters snapshot
 */
void dhcp_device_update_snapshot(dhcp_device_context_t *context);

/**
 * @code dhcp_device_print_status(context, type);
 *
 * @brief prints status counters to syslog. If context is null, it will print aggregate status
 *
 * @param context       Device (interface) context
 * @param type          Counter type to be printed
 *
 * @return none
 */
void dhcp_device_print_status(dhcp_device_context_t *context, dhcp_counters_type_t type);

/**
 * @code dhcp_device_active_types(dhcpv4, dhcpv6);
 *
 * @brief update local variables with active protocols
 *
 * @param dhcpv4       DHCPv4 enable flag
 * @param dhcpv6       DHCPv6 enable flag
 *
 * @return none
 */
void dhcp_device_active_types(bool dhcpv4, bool dhcpv6);
#endif /* DHCP_DEVICE_H_ */
