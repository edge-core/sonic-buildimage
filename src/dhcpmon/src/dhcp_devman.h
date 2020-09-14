/**
 * @file dhcp_devman.h
 *
 *  Device (interface) manager
 */

#ifndef DHCP_DEVMAN_H_
#define DHCP_DEVMAN_H_

#include <stdint.h>

#include "dhcp_device.h"

/**
 * @code dhcp_devman_init();
 *
 * @brief initializes device (interface) manager that keeps track of interfaces and assert that there is one south
 *        interface and as many north interfaces
 *
 * @return none
 */
void dhcp_devman_init();

/**
 * @code dhcp_devman_shutdown();
 *
 * @brief shuts down device (interface) manager. Also, stops packet capture on interface and cleans up any allocated
 *        memory
 *
 * @return none
 */
void dhcp_devman_shutdown();

/**
 * @code dhcp_devman_get_vlan_intf();
 *
 * @brief Accessor method
 *
 * @return pointer to vlan ip interface name
 */
const char* dhcp_devman_get_vlan_intf();

/**
 * @code dhcp_devman_add_intf(name, uplink);
 *
 * @brief adds interface to the device manager.
 *
 * @param name              interface name
 * @param is_uplink         true for uplink (north) interface
 *
 * @return 0 on success, nonzero otherwise
 */
int dhcp_devman_add_intf(const char *name, uint8_t is_uplink);

/**
 * @code dhcp_devman_start_capture(snaplen, base);
 *
 * @brief start packet capture on the devman interface list
 *
 * @param snaplen packet    packet capture snap length
 * @param base              libevent base
 *
 * @return 0 on success, nonzero otherwise
 */
int dhcp_devman_start_capture(size_t snaplen, struct event_base *base);

/**
 * @code dhcp_devman_get_status();
 *
 * @brief collects DHCP relay status info.
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
dhcp_mon_status_t dhcp_devman_get_status();

/**
 * @code dhcp_devman_print_status();
 *
 * @brief prints status counters to syslog
 *
 * @return none
 */
void dhcp_devman_print_status();

#endif /* DHCP_DEVMAN_H_ */
