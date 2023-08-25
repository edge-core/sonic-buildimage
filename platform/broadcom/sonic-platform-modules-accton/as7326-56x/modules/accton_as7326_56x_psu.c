/*
 * An hwmon driver for accton as7326_56x Power Module
 *
 * Copyright (C) 2014 Accton Technology Corporation.
 * Brandon Chuang <brandon_chuang@accton.com.tw>
 *
 * Based on ad7414.c
 * Copyright 2006 Stefan Roese <sr at denx.de>, DENX Software Engineering
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
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <linux/module.h>
#include <linux/jiffies.h>
#include <linux/i2c.h>
#include <linux/hwmon.h>
#include <linux/hwmon-sysfs.h>
#include <linux/err.h>
#include <linux/mutex.h>
#include <linux/sysfs.h>
#include <linux/slab.h>
#include <linux/delay.h>
#include <linux/dmi.h>

#define MAX_MODEL_NAME          16
#define MAX_SERIAL_NUMBER       18
static ssize_t show_status(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t show_string(struct device *dev, struct device_attribute *da, char *buf);
static int as7326_56x_psu_read_block(struct i2c_client *client, u8 command, u8 *data,int data_len);
extern int as7326_56x_cpld_read(unsigned short cpld_addr, u8 reg);

/* Addresses scanned
 */
static const unsigned short normal_i2c[] = { 0x50, 0x53, I2C_CLIENT_END };

/* Each client has this additional data
 */
struct as7326_56x_psu_data {
    struct device      *hwmon_dev;
    struct mutex        update_lock;
    char                valid;           /* !=0 if registers are valid */
    unsigned long       last_updated;    /* In jiffies */
    u8  index;           /* PSU index */
    u8  status;          /* Status(present/power_good) register read from CPLD */
    char model_name[MAX_MODEL_NAME+1]; /* Model name, read from eeprom */
    char serial_number[MAX_SERIAL_NUMBER+1];
};

static struct as7326_56x_psu_data *as7326_56x_psu_update_device(struct device *dev);

enum as7326_56x_psu_sysfs_attributes {
    PSU_PRESENT,
    PSU_MODEL_NAME,
    PSU_SERIAL_NUMBER,
    PSU_POWER_GOOD
};

/* sysfs attributes for hwmon
 */
static SENSOR_DEVICE_ATTR(psu_present,    S_IRUGO, show_status,    NULL, PSU_PRESENT);
static SENSOR_DEVICE_ATTR(psu_model_name, S_IRUGO, show_string,    NULL, PSU_MODEL_NAME);
static SENSOR_DEVICE_ATTR(psu_serial_number, S_IRUGO, show_string,    NULL, PSU_SERIAL_NUMBER);
static SENSOR_DEVICE_ATTR(psu_power_good, S_IRUGO, show_status,    NULL, PSU_POWER_GOOD);

static struct attribute *as7326_56x_psu_attributes[] = {
    &sensor_dev_attr_psu_present.dev_attr.attr,
    &sensor_dev_attr_psu_model_name.dev_attr.attr,
    &sensor_dev_attr_psu_serial_number.dev_attr.attr,
    &sensor_dev_attr_psu_power_good.dev_attr.attr,
    NULL
};

static ssize_t show_status(struct device *dev, struct device_attribute *da,
                           char *buf)
{
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct as7326_56x_psu_data *data = as7326_56x_psu_update_device(dev);
    u8 status = 0;

    if (!data->valid) {
        return -EIO;
    }

    if (attr->index == PSU_PRESENT) {
        status = !(data->status >> (1-data->index) & 0x1);
    }
    else { /* PSU_POWER_GOOD */
        status = (data->status >> (3-data->index) & 0x1);
    }

    return sprintf(buf, "%d\n", status);
}

static ssize_t show_string(struct device *dev, struct device_attribute *da,
             char *buf)
{
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct as7326_56x_psu_data *data = as7326_56x_psu_update_device(dev);
    char *ptr = NULL;

    if (!data->valid) {
        return -EIO;
    }

    if (attr->index == PSU_MODEL_NAME) {
        ptr = data->model_name;
    }
    else if (attr->index == PSU_SERIAL_NUMBER) {
        ptr = data->serial_number;
    }
    else {
        return -EIO;
    }
    return sprintf(buf, "%s\n", ptr);
}

static const struct attribute_group as7326_56x_psu_group = {
    .attrs = as7326_56x_psu_attributes,
};

static int as7326_56x_psu_probe(struct i2c_client *client,
                                const struct i2c_device_id *dev_id)
{
    struct as7326_56x_psu_data *data;
    int status;

    if (!i2c_check_functionality(client->adapter, I2C_FUNC_SMBUS_I2C_BLOCK)) {
        status = -EIO;
        goto exit;
    }

    data = kzalloc(sizeof(struct as7326_56x_psu_data), GFP_KERNEL);
    if (!data) {
        status = -ENOMEM;
        goto exit;
    }

    i2c_set_clientdata(client, data);
    data->valid = 0;
    data->index = dev_id->driver_data;
    mutex_init(&data->update_lock);

    dev_info(&client->dev, "chip found\n");

    /* Register sysfs hooks */
    status = sysfs_create_group(&client->dev.kobj, &as7326_56x_psu_group);
    if (status) {
        goto exit_free;
    }

    data->hwmon_dev = hwmon_device_register(&client->dev);
    if (IS_ERR(data->hwmon_dev)) {
        status = PTR_ERR(data->hwmon_dev);
        goto exit_remove;
    }

    dev_info(&client->dev, "%s: psu '%s'\n",
             dev_name(data->hwmon_dev), client->name);

    return 0;

exit_remove:
    sysfs_remove_group(&client->dev.kobj, &as7326_56x_psu_group);
exit_free:
    kfree(data);
exit:

    return status;
}

static int as7326_56x_psu_remove(struct i2c_client *client)
{
    struct as7326_56x_psu_data *data = i2c_get_clientdata(client);

    hwmon_device_unregister(data->hwmon_dev);
    sysfs_remove_group(&client->dev.kobj, &as7326_56x_psu_group);
    kfree(data);

    return 0;
}

enum psu_index
{
    as7326_56x_psu1,
    as7326_56x_psu2
};

static const struct i2c_device_id as7326_56x_psu_id[] = {
    { "as7326_56x_psu1", as7326_56x_psu1 },
    { "as7326_56x_psu2", as7326_56x_psu2 },
    {}
};
MODULE_DEVICE_TABLE(i2c, as7326_56x_psu_id);

static struct i2c_driver as7326_56x_psu_driver = {
    .class        = I2C_CLASS_HWMON,
    .driver = {
        .name     = "as7326_56x_psu",
    },
    .probe        = as7326_56x_psu_probe,
    .remove       = as7326_56x_psu_remove,
    .id_table     = as7326_56x_psu_id,
    .address_list = normal_i2c,
};

static int as7326_56x_psu_read_block(struct i2c_client *client, u8 command, u8 *data,
                                     int data_len)
{
    int result = 0;
    int retry_count = 5;

    while (retry_count) {
        retry_count--;

        result = i2c_smbus_read_i2c_block_data(client, command, data_len, data);

        if (unlikely(result < 0)) {
            msleep(10);
            continue;
        }

        if (unlikely(result != data_len)) {
            result = -EIO;
            msleep(10);
            continue;
        }

        result = 0;
        break;
    }

    return result;
}

enum psu_type {
    PSU_TYPE_AC_110V,
    PSU_TYPE_DC_48V,
    PSU_TYPE_DC_12V,
    PSU_TYPE_AC_ACBEL_FSF019,
    PSU_TYPE_AC_ACBEL_FSF045
};

struct model_name_info {
    enum psu_type type;
    u8 offset;
    u8 length;
    char* model_name;
};

struct serial_number_info {
    enum psu_type type;
    u8 offset;
    u8 length;
    char* serial_number;
};

struct model_name_info models[] = {
    {PSU_TYPE_AC_110V, 0x20, 8, "YM-2651Y"},
    {PSU_TYPE_DC_48V,  0x20, 8, "YM-2651V"},
    {PSU_TYPE_DC_12V,  0x00, 11, "PSU-12V-750"},
    {PSU_TYPE_AC_ACBEL_FSF019, 0x15, 10, "FSF019-"},
    {PSU_TYPE_AC_ACBEL_FSF045, 0x15, 10, "FSF045-"}
};

struct serial_number_info serials[] = {
    {PSU_TYPE_AC_110V, 0x2e, 18, "YM-2651Y"},
    {PSU_TYPE_DC_48V,  0x2e, 18, "YM-2651V"},
    {PSU_TYPE_DC_12V,  0x2e, 18, "PSU-12V-750"},
    {PSU_TYPE_AC_ACBEL_FSF019, 0x2e, 16, "FSF019-"},
    {PSU_TYPE_AC_ACBEL_FSF045, 0x2e, 16, "FSF045-"}
};

static int as7326_56x_psu_model_name_get(struct device *dev)
{
    struct i2c_client *client = to_i2c_client(dev);
    struct as7326_56x_psu_data *data = i2c_get_clientdata(client);
    int i, status;

    for (i = 0; i < ARRAY_SIZE(models); i++) {
        memset(data->model_name, 0, sizeof(data->model_name));

        status = as7326_56x_psu_read_block(client, models[i].offset,
                                           data->model_name, models[i].length);
        if (status < 0) {
            data->model_name[0] = '\0';
            dev_dbg(&client->dev, "unable to read model name from (0x%x) offset(0x%x)\n",
                                  client->addr, models[i].offset);
            return status;
        }
        else {
            data->model_name[models[i].length] = '\0';
        }

        /* Determine if the model name is known, if not, read next index
         */
        if (strncmp(data->model_name, models[i].model_name, strlen(models[i].model_name)) == 0) {
            return 0;
        }
        else {
            data->model_name[0] = '\0';
        }
    }

    return -ENODATA;
}

static int as7326_56x_psu_serial_number_get(struct device *dev)
{
    struct i2c_client *client = to_i2c_client(dev);
    struct as7326_56x_psu_data *data = i2c_get_clientdata(client);
    int i, status;

    for (i = 0; i < ARRAY_SIZE(models); i++) {
        memset(data->serial_number, 0, sizeof(data->serial_number));

        status = as7326_56x_psu_read_block(client, serials[i].offset,
                                           data->serial_number, serials[i].length);
        if (status < 0) {
            data->serial_number[0] = '\0';
            dev_dbg(&client->dev, "unable to read serial_number from (0x%x) offset(0x%x)\n",
                                  client->addr, serials[i].offset);
            return status;
        }
        else {
            data->serial_number[serials[i].length] = '\0';
        }

        /* Determine if the model name is known, if not, read next index
         */
        if (strncmp(data->model_name, models[i].model_name, strlen(models[i].model_name)) == 0) {
            return 0;
        }
        else {
            data->serial_number[0] = '\0';
        }
    }

    return -ENODATA;
}

static struct as7326_56x_psu_data *as7326_56x_psu_update_device(struct device *dev)
{
    struct i2c_client *client = to_i2c_client(dev);
    struct as7326_56x_psu_data *data = i2c_get_clientdata(client);

    mutex_lock(&data->update_lock);

    if (time_after(jiffies, data->last_updated + HZ + HZ / 2)
            || !data->valid) {
        int status;
        int power_good = 0;

        data->valid = 0;
        dev_dbg(&client->dev, "Starting as7326_56x update\n");

        /* Read psu status */
        status = as7326_56x_cpld_read(0x60, 0x2);

        if (status < 0) {
            dev_dbg(&client->dev, "cpld reg 0x60 err %d\n", status);
            goto exit;
        }
        else {
            data->status = status;
        }

        /* Read model name */
        memset(data->model_name, 0, sizeof(data->model_name));
        memset(data->serial_number, 0, sizeof(data->serial_number));
        power_good = (data->status >> (3-data->index) & 0x1);

        if (power_good) {
            if (as7326_56x_psu_model_name_get(dev) < 0) {
                goto exit;
            }
            if (as7326_56x_psu_serial_number_get(dev) < 0) {
                goto exit;
            }
        }

        data->last_updated = jiffies;
        data->valid = 1;
    }

exit:
    mutex_unlock(&data->update_lock);

    return data;
}

module_i2c_driver(as7326_56x_psu_driver);

MODULE_AUTHOR("Brandon Chuang <brandon_chuang@accton.com.tw>");
MODULE_DESCRIPTION("as7326_56x_psu driver");
MODULE_LICENSE("GPL");

