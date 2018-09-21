// Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
// Arista Networks, Inc. Confidential and Proprietary.

#ifndef DRIVER_SONICSUPPORTDRIVER_H
#define DRIVER_SONICSUPPORTDRIVER_H

#include <linux/printk.h>

#define sonic_err(fmt, ...) \
   pr_info("sonic: " fmt, ##__VA_ARGS__);
#define sonic_warn(fmt, ...) \
   pr_warn("sonic: " fmt, ##__VA_ARGS__);
#define sonic_info(fmt, ...) \
   pr_info("sonic: " fmt, ##__VA_ARGS__);
#define sonic_dbg(fmt, ...) \
   pr_debug("sonic: " fmt, ##__VA_ARGS__);

#endif // DRIVER_SOINCSUPPORTDRIVER_H

