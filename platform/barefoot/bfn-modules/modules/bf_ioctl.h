/*******************************************************************************
 * BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
 *
 * Copyright (c) 2018-2018 Barefoot Networks, Inc.
 *
 * NOTICE: All information contained herein is, and remains the property of
 * Barefoot Networks, Inc. and its suppliers, if any. The intellectual and
 * technical concepts contained herein are proprietary to Barefoot Networks,
 * Inc.
 * and its suppliers and may be covered by U.S. and Foreign Patents, patents in
 * process, and are protected by trade secret or copyright law.
 * Dissemination of this information or reproduction of this material is
 * strictly forbidden unless prior written permission is obtained from
 * Barefoot Networks, Inc.
 *
 * No warranty, explicit or implicit is provided, unless granted under a
 * written agreement with Barefoot Networks, Inc.
 *
 * $Id: $
 *
 ******************************************************************************/

#ifndef _BF_IOCTL_H_
#define _BF_IOCTL_H_

#ifdef __KERNEL__
#include <linux/ioctl.h>
#else
#include <sys/ioctl.h>

#ifndef phys_addr_t
typedef uint64_t phys_addr_t;
#endif

#endif /* __KERNEL__ */

#define BF_IOC_MAGIC 'b'

typedef struct bf_dma_bus_map_s 
{
  phys_addr_t phy_addr;
  void *dma_addr;
  size_t size;
} bf_dma_bus_map_t;

#define BF_IOCMAPDMAADDR    _IOWR(BF_IOC_MAGIC, 0, bf_dma_bus_map_t)
#define BF_IOCUNMAPDMAADDR  _IOW(BF_IOC_MAGIC, 0, bf_dma_bus_map_t)

#endif /* _BF_IOCTL_H_ */
