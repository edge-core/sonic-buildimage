#ifndef _LINUX_DRIVER_SCD_HWMON_H_
#define _LINUX_DRIVER_SCD_HWMON_H_

#include <linux/printk.h>

#define scd_err(fmt, ...) \
   pr_err("scd-hwmon: " fmt, ##__VA_ARGS__);
#define scd_warn(fmt, ...) \
   pr_warn("scd-hwmon: " fmt, ##__VA_ARGS__);
#define scd_info(fmt, ...) \
   pr_info("scd-hwmon: " fmt, ##__VA_ARGS__);
#define scd_dbg(fmt, ...) \
   pr_debug("scd-hwmon: " fmt, ##__VA_ARGS__);

#endif /* !_LINUX_DRIVER_SCD_HWMON_H_ */
