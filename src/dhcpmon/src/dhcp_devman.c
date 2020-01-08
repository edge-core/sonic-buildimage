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

#include "dhcp_devman.h"

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
 * @code dhcp_devman_add_intf(name, uplink);
 *
 * @brief adds interface to the device manager.
 */
int dhcp_devman_add_intf(const char *name, uint8_t is_uplink)
{
    int rv = -1;
    struct intf *dev = malloc(sizeof(struct intf));

    if (dev != NULL) {
        dev->name = name;
        dev->is_uplink = is_uplink;
        if (is_uplink) {
            dhcp_num_north_intf++;
        } else {
            dhcp_num_south_intf++;
            assert(dhcp_num_south_intf <= 1);
        }

        LIST_INSERT_HEAD(&intfs, dev, entry);

        rv = 0;
    }
    else {
        syslog(LOG_ALERT, "malloc: failed to allocate memory for intf '%s'\n", name);
    }

    return rv;
}

/**
 * @code dhcp_devman_start_capture(snaplen, base);
 *
 * @brief start packet capture on the devman interface list
 */
int dhcp_devman_start_capture(int snaplen, struct event_base *base)
{
    int rv = -1;
    struct intf *int_ptr;

    if ((dhcp_num_south_intf == 1) && (dhcp_num_north_intf >= 1)) {
        LIST_FOREACH(int_ptr, &intfs, entry) {
            rv = dhcp_device_init(&int_ptr->dev_context, int_ptr->name, snaplen, int_ptr->is_uplink, base);
            if (rv == 0) {
                syslog(LOG_INFO,
                       "Capturing DHCP packets on interface %s, ip: 0x%08x, mac [%02x:%02x:%02x:%02x:%02x:%02x] \n",
                       int_ptr->name, int_ptr->dev_context->ip, int_ptr->dev_context->mac[0],
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
 * @code dhcp_devman_get_status();
 *
 * @brief collects DHCP relay status info.
 */
dhcp_mon_status_t dhcp_devman_get_status()
{
    return dhcp_device_get_status(NULL);
}

/**
 * @code dhcp_devman_print_status();
 *
 * @brief prints status counters to syslog
 */
void dhcp_devman_print_status()
{
    dhcp_device_print_status(NULL);
}
