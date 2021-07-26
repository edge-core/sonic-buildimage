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
 * @return pointer to aggregate device (interface) context
 */
dhcp_device_context_t* dhcp_devman_get_agg_dev();

/**
 * @code dhcp_devman_get_mgmt_intf_context();
 *
 * @brief Accessor method
 *
 * @return pointer to mgmt interface context
 */
dhcp_device_context_t* dhcp_devman_get_mgmt_dev();

/**
 * @code dhcp_devman_add_intf(name, uplink);
 *
 * @brief adds interface to the device manager.
 *
 * @param name              interface name
 * @param intf_type         'u' for uplink (north) interface
 *                          'd' for downlink (south) interface
 *                          'm' for mgmt interface
 *
 * @return 0 on success, nonzero otherwise
 */
int dhcp_devman_add_intf(const char *name, char intf_type);

/**
 * @code dhcp_devman_setup_dual_tor_mode(name);
 *
 * @brief set up dual tor mode: 1) set dual_tor_mode flag and 2) retrieve loopback_ip.
 *
 * @param name              interface name
 *
 * @return 0 on success, nonzero otherwise
 */
int dhcp_devman_setup_dual_tor_mode(const char *name);

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
 * @code dhcp_devman_get_status(check_type, context, type);
 *
 * @brief collects DHCP relay status info.
 *
 * @param check_type        Type of validation
 * @param context           pointer to device (interface) context
 * @param type              DHCP type
 *
 * @return DHCP_MON_STATUS_HEALTHY, DHCP_MON_STATUS_UNHEALTHY, or DHCP_MON_STATUS_INDETERMINATE
 */
dhcp_mon_status_t dhcp_devman_get_status(dhcp_mon_check_t check_type, dhcp_device_context_t *context, dhcp_type_t type);

/**
 * @code dhcp_devman_update_snapshot(context);
 *
 * @param context           Device (interface) context
 *
 * @brief Update device/interface counters snapshot
 */
void dhcp_devman_update_snapshot(dhcp_device_context_t *context);

/**
 * @code dhcp_devman_print_status(context, type);
 *
 * @brief prints status counters to syslog
 *
 * @param context       pointer to device (interface) context
 * @param type          Counter type to be printed
 *
 * @return none
 */
void dhcp_devman_print_status(dhcp_device_context_t *context, dhcp_counters_type_t type);

/**
 * @code dhcp_devman_active_types(dhcpv4, dhcpv6);
 *
 * @brief update local variables with active protocols
 *
 * @param dhcpv4       flag indicating dhcpv4 is enabled
 * @param dhcpv6       flag indicating dhcpv6 is enabled
 *
 * @return none
 */
void dhcp_devman_active_types(bool dhcpv4, bool dhcpv6);

#endif /* DHCP_DEVMAN_H_ */
