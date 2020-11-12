/*
 * Copyright 2019 Broadcom.
 * The term “Broadcom” refers to Broadcom Inc. and/or its subsidiaries.
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * Description
 *  FAN driver api declarations
 */

#ifndef __PDDF_FAN_API_H__
#define __PDDF_FAN_API_H__

extern int pddf_fan_post_probe_default(struct i2c_client *client, const struct i2c_device_id *dev_id);

extern void get_fan_duplicate_sysfs(int idx, char *str);
extern ssize_t fan_show_default(struct device *dev, struct device_attribute *da, char *buf);
extern ssize_t fan_store_default(struct device *dev, struct device_attribute *da, const char *buf, size_t count);


extern int sonic_i2c_get_fan_present_default(void *client, FAN_DATA_ATTR *adata, void *data);
extern int sonic_i2c_get_fan_rpm_default(void *client, FAN_DATA_ATTR *adata, void *data);
extern int sonic_i2c_get_fan_direction_default(void *client, FAN_DATA_ATTR *adata, void *data);
extern int sonic_i2c_get_fan_pwm_default(void *client, FAN_DATA_ATTR *adata, void *data);
extern int sonic_i2c_get_fan_fault_default(void *client, FAN_DATA_ATTR *adata, void *data);
extern int sonic_i2c_set_fan_pwm_default(void *client, FAN_DATA_ATTR *adata, void *data);

#endif
