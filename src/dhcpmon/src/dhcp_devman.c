/**
 * @file dhcp_devman.c
 *
 *  Device (interface) manager
 */
#include <assert.h>
#include <errno.h>
#include <string.h>
#include <syslog.h>
#include <sys/queue.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <stdbool.h>

#include "dhcp_devman.h"

/** Prefix appended to Aggregation device */
#define AGG_DEV_PREFIX  "Agg-"

/** struct for interface information */
struct intf
{
    const char *name;                   /** interface name */
    uint8_t is_uplink;                  /** is uplink (north) interface */
    dhcp_device_context_t *dev_context; /** device (interface_ context */
    LIST_ENTRY(intf) entry;             /** list link/pointers entries */
};

/** intfs list of interfaces */
static LIST_HEAD(intf_list, intf) intfs;
/** dhcp_num_south_intf number of south interfaces */
static uint32_t dhcp_num_south_intf = 0;
/** dhcp_num_north_intf number of north interfaces */
static uint32_t dhcp_num_north_intf = 0;
/** dhcp_num_mgmt_intf number of mgmt interfaces */
static uint32_t dhcp_num_mgmt_intf = 0;

/** On Device  vlan interface IP address corresponding vlan downlink IP
 *  This IP is used to filter Offer/Ack packet coming from DHCP server */
static in_addr_t v4_vlan_ip = 0;
static struct in6_addr v6_vlan_ip = {0};

/* Device loopback interface ip, which will be used as the giaddr in dual tor setup. */
static in_addr_t loopback_ip = 0;

/* Whether the device is in dual tor mode, 0 as default for single tor mode. */
static int dual_tor_mode = 0;

/** mgmt interface */
static struct intf *mgmt_intf = NULL;

/**
 * @code dhcp_devman_get_vlan_intf();
 *
 * Accessor method
 */
dhcp_device_context_t* dhcp_devman_get_agg_dev()
{
    return dhcp_device_get_aggregate_context();
}

/**
 * @code dhcp_devman_get_mgmt_dev();
 *
 * Accessor method
 */
dhcp_device_context_t* dhcp_devman_get_mgmt_dev()
{
    return mgmt_intf ? mgmt_intf->dev_context : NULL;
}

/**
 * @code dhcp_devman_init();
 *
 * initializes device (interface) manager that keeps track of interfaces and assert that there is one south
 * interface and as many north interfaces
 */
void dhcp_devman_init()
{
    LIST_INIT(&intfs);
}

/**
 * @code dhcp_devman_shutdown();
 *
 * shuts down device (interface) manager. Also, stops packet capture on interface and cleans up any allocated
 * memory
 */
void dhcp_devman_shutdown()
{
    struct intf *int_ptr, *prev_intf = NULL;

    LIST_FOREACH(int_ptr, &intfs, entry) {
        dhcp_device_shutdown(int_ptr->dev_context);
        if (prev_intf) {
            LIST_REMOVE(prev_intf, entry);
            free(prev_intf);
            prev_intf = int_ptr;
        }
    }

    if (prev_intf) {
        LIST_REMOVE(prev_intf, entry);
        free(prev_intf);
    }
}

/**
 * @code dhcp_devman_add_intf(name, is_uplink);
 *
 * @brief adds interface to the device manager.
 */
int dhcp_devman_add_intf(const char *name, char intf_type)
{
    int rv = -1;
    struct intf *dev = malloc(sizeof(struct intf));

    if (dev != NULL) {
        dev->name = name;
        dev->is_uplink = intf_type != 'd';

        switch (intf_type)
        {
        case 'u':
            dhcp_num_north_intf++;
            break;
        case 'd':
            dhcp_num_south_intf++;
            assert(dhcp_num_south_intf <= 1);
            break;
        case 'm':
            dhcp_num_mgmt_intf++;
            assert(dhcp_num_mgmt_intf <= 1);
            mgmt_intf = dev;
            break;
        default:
            break;
        }

        rv = dhcp_device_init(&dev->dev_context, dev->name, dev->is_uplink);
        if (rv == 0 && intf_type == 'd') {
            rv = dhcp_device_get_ipv4(dev->dev_context, &v4_vlan_ip);
            rv = dhcp_device_get_ipv6(dev->dev_context, &v6_vlan_ip);

            dhcp_device_context_t *agg_dev = dhcp_device_get_aggregate_context();

            strncpy(agg_dev->intf, AGG_DEV_PREFIX, sizeof(AGG_DEV_PREFIX));
            strncpy(agg_dev->intf + sizeof(AGG_DEV_PREFIX) - 1, name, sizeof(agg_dev->intf) - sizeof(AGG_DEV_PREFIX));
            agg_dev->intf[sizeof(agg_dev->intf) - 1] = '\0';
        }

        LIST_INSERT_HEAD(&intfs, dev, entry);
    }
    else {
        syslog(LOG_ALERT, "malloc: failed to allocate memory for intf '%s'\n", name);
    }

    return rv;
}

/**
 * @code dhcp_devman_setup_dual_tor_mode(name);
 *
 * @brief set up dual tor mode: 1) set dual_tor_mode flag and 2) retrieve loopback_ip.
 */
int dhcp_devman_setup_dual_tor_mode(const char *name)
{
    int rv = -1;

    dhcp_device_context_t loopback_intf_context;

    if (strlen(name) < sizeof(loopback_intf_context.intf)) {
        strncpy(loopback_intf_context.intf, name, sizeof(loopback_intf_context.intf) - 1);
        loopback_intf_context.intf[sizeof(loopback_intf_context.intf) - 1] = '\0';
    } else {
        syslog(LOG_ALERT, "loopback interface name (%s) is too long", name);
        return rv;
    }

    if (initialize_intf_mac_and_ip_addr(&loopback_intf_context) == 0 &&
        dhcp_device_get_ipv4(&loopback_intf_context, &loopback_ip) == 0) {
            dual_tor_mode = 1;
    } else {
        syslog(LOG_ALERT, "failed to retrieve ip addr for loopback interface (%s)", name);
        return rv;
    }

    rv = 0;
    return rv;
}

/**
 * @code dhcp_devman_start_capture(snaplen, base);
 *
 * @brief start packet capture on the devman interface list
 */
int dhcp_devman_start_capture(size_t snaplen, struct event_base *base)
{
    int rv = -1;
    struct intf *int_ptr;

    if ((dhcp_num_south_intf == 1) && (dhcp_num_north_intf >= 1)) {
        LIST_FOREACH(int_ptr, &intfs, entry) {
            rv = dhcp_device_start_capture(int_ptr->dev_context, snaplen, base, dual_tor_mode ? loopback_ip : v4_vlan_ip, v6_vlan_ip);
            if (rv == 0) {
                char ipv6_addr[INET6_ADDRSTRLEN];
                inet_ntop(AF_INET6, &int_ptr->dev_context->ipv6, ipv6_addr, sizeof(ipv6_addr));
                syslog(LOG_INFO,
                       "Capturing DHCP packets on interface %s, ipv4: 0x%08x, ipv6: %s, mac [%02x:%02x:%02x:%02x:%02x:%02x] \n",
                       int_ptr->name, int_ptr->dev_context->ipv4, ipv6_addr, int_ptr->dev_context->mac[0],
                       int_ptr->dev_context->mac[1], int_ptr->dev_context->mac[2], int_ptr->dev_context->mac[3],
                       int_ptr->dev_context->mac[4], int_ptr->dev_context->mac[5]);
            }
            else {
                break;
            }
        }
    }
    else {
        syslog(LOG_ERR, "Invalid number of interfaces, downlink/south %d, uplink/north %d\n",
               dhcp_num_south_intf, dhcp_num_north_intf);
    }

    return rv;
}

/**
 * @code dhcp_devman_get_status(check_type, context, type);
 *
 * @brief collects DHCP relay status info.
 */
dhcp_mon_status_t dhcp_devman_get_status(dhcp_mon_check_t check_type, dhcp_device_context_t *context, dhcp_type_t type)
{
    return dhcp_device_get_status(check_type, context, type);
}

/**
 * @code dhcp_devman_update_snapshot(context);
 *
 * @brief Update device/interface counters snapshot
 */
void dhcp_devman_update_snapshot(dhcp_device_context_t *context)
{
    if (context == NULL) {
        struct intf *int_ptr;

        LIST_FOREACH(int_ptr, &intfs, entry) {
            dhcp_device_update_snapshot(int_ptr->dev_context);
        }

        dhcp_device_update_snapshot(dhcp_devman_get_agg_dev());
    } else {
        dhcp_device_update_snapshot(context);
    }
}

/**
 * @code dhcp_devman_print_status(context, type);
 *
 * @brief prints status counters to syslog, if context is null, it prints status counters for all interfaces
 */
void dhcp_devman_print_status(dhcp_device_context_t *context, dhcp_counters_type_t type)
{
    if (context == NULL) {
        struct intf *int_ptr;

        LIST_FOREACH(int_ptr, &intfs, entry) {
            dhcp_device_print_status(int_ptr->dev_context, type);
        }

        dhcp_device_print_status(dhcp_devman_get_agg_dev(), type);
    } else {
        dhcp_device_print_status(context, type);
    }
}

/**
 * @code dhcp_devman_active_types(dhcpv4, dhcpv6);
 *
 * @brief update local variables with active protocols
 */
void dhcp_devman_active_types(bool dhcpv4, bool dhcpv6)
{
    dhcp_device_active_types(dhcpv4, dhcpv6);
}
