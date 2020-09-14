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


/** packet direction */
typedef enum
{
    DHCP_RX,    /** RX DHCP packet */
    DHCP_TX,    /** TX DHCP packet */

    DHCP_DIR_COUNT
} dhcp_packet_direction_t;

/** dhcp health status */
typedef enum
{
    DHCP_MON_STATUS_HEALTHY,        /** DHCP relay is healthy */
    DHCP_MON_STATUS_UNHEALTHY,      /** DHCP relay is unhealthy and is missing out on some packets */
    DHCP_MON_STATUS_INDETERMINATE,  /** DHCP relay health could not be determined */
} dhcp_mon_status_t;

/** DHCP device (interface) health counters */
typedef struct
{
    uint64_t discover;      /** DHCP discover packets */
    uint64_t offer;         /** DHCP offer packets */
    uint64_t request;       /** DHCP request packets */
    uint64_t ack;           /** DHCP ack packets */
} dhcp_device_counters_t;

/** DHCP device (interface) context */
typedef struct
{
    int sock;                       /** Raw socket associated with this device/interface */
    in_addr_t ip;                   /** network address of this device (interface) */
    uint8_t mac[ETHER_ADDR_LEN];    /** hardware address of this device (interface) */
    in_addr_t vlan_ip;              /** Vlan IP address */
    uint8_t is_uplink;              /** north interface? */
    char intf[IF_NAMESIZE];         /** device (interface) name */
    uint8_t *buffer;                /** buffer used to read socket data */
    size_t snaplen;                 /** snap length or buffer size */
    dhcp_device_counters_t counters[DHCP_DIR_COUNT];
                                    /** current coutners of DORA packets */
    dhcp_device_counters_t counters_snapshot[DHCP_DIR_COUNT];
                                    /** counter snapshot */
} dhcp_device_context_t;

/**
 * @code dhcp_device_get_ip(context, ip);
 *
 * @brief Accessor method
 *
 * @param context       pointer to device (interface) context
 * @param ip(out)       pointer to device IP
 *
 * @return 0 on success, otherwise for failure
 */
int dhcp_device_get_ip(dhcp_device_context_t *context, in_addr_t *ip);

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
 * @code dhcp_device_start_capture(context, snaplen, base, vlan_ip);
 *
 * @brief starts packet capture on this interface
 *
 * @param context           pointer to device (interface) context
 * @param snaplen           length of packet capture
 * @param base              pointer to libevent base
 * @param vlan_ip           vlan IP address
 *
 * @return 0 on success, otherwise for failure
 */
int dhcp_device_start_capture(dhcp_device_context_t *context,
                              size_t snaplen,
                              struct event_base *base,
                              in_addr_t vlan_ip);

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
 * @code dhcp_device_get_status(context);
 *
 * @brief collects DHCP relay status info for a given interface. If context is null, it will report aggregate
 *        status
 *
 * @param context   Device (interface) context
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
dhcp_mon_status_t dhcp_device_get_status(dhcp_device_context_t *context);

/**
 * @code dhcp_device_print_status();
 *
 * @brief prints status counters to syslog. If context is null, it will print aggregate status
 *
 * @return none
 */
void dhcp_device_print_status(dhcp_device_context_t *context);

#endif /* DHCP_DEVICE_H_ */
