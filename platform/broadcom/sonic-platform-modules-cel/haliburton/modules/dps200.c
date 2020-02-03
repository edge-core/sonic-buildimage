/*
 * Hardware monitoring driver for Delta DPS200
 *
 * (C) Copyright 2019, Celestica Inc.
 * Author: Pradchaya Phucharoen <pphuchar@celestica.com>
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

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/err.h>
#include <linux/slab.h>
#include <linux/mutex.h>
#include <linux/i2c.h>
#include <linux/pmbus.h>
#include "pmbus.h"


static int dps200_read_word_data(struct i2c_client *client, int page, int reg)
{

    if (reg >= PMBUS_VIRT_BASE ||
        reg == PMBUS_VOUT_OV_FAULT_LIMIT ||
        reg == PMBUS_VOUT_OV_WARN_LIMIT ||
        reg == PMBUS_VOUT_UV_WARN_LIMIT ||
        reg == PMBUS_VOUT_UV_FAULT_LIMIT ||
        reg == PMBUS_IOUT_OC_LV_FAULT_LIMIT ||
        reg == PMBUS_IOUT_UC_FAULT_LIMIT ||
        reg == PMBUS_UT_WARN_LIMIT ||
        reg == PMBUS_UT_FAULT_LIMIT ||
        reg == PMBUS_VIN_OV_FAULT_LIMIT ||
        reg == PMBUS_VIN_OV_WARN_LIMIT ||
        reg == PMBUS_IIN_OC_FAULT_LIMIT ||
        reg == PMBUS_POUT_MAX)
        return -ENXIO;

    /* 
     * WARNING: The following feild have coinstant driver value.
     * If the register are 
     * PMBUS_IOUT_OC_WARN_LIMIT or PMBUS_IOUT_OC_FAULT_LIMIT convert 
     * the constant value from linear to direct fomat.
     */
    if (reg == PMBUS_IOUT_OC_WARN_LIMIT)
        return 0xb4;
    else if (reg == PMBUS_IOUT_OC_FAULT_LIMIT)
        return 0xc8;
    else
        return pmbus_read_word_data(client, page, reg);
}

/*
 * Form DPS-200 datasheet the supported sensors format defined as:
 * VOUT: direct mode with one decimal place.
 * 
 * Other sensors:
 * IOUT: direct mode with one decimal place.
 * IOUT Limits: linear mode, which difference from IOUT.
 * VIN, IIN, POWER, TEMP, & FAN: linear mode.
 */
static struct pmbus_driver_info dps200_info = {
    .pages = 1,
    .func[0] = PMBUS_HAVE_VIN | PMBUS_HAVE_VOUT | PMBUS_HAVE_STATUS_VOUT
                 | PMBUS_HAVE_IIN | PMBUS_HAVE_IOUT | PMBUS_HAVE_STATUS_IOUT
                 | PMBUS_HAVE_PIN | PMBUS_HAVE_POUT
                 | PMBUS_HAVE_FAN12 | PMBUS_HAVE_STATUS_FAN12
                 | PMBUS_HAVE_TEMP | PMBUS_HAVE_TEMP2 | PMBUS_HAVE_TEMP3 | PMBUS_HAVE_STATUS_TEMP
                 | PMBUS_HAVE_STATUS_INPUT,
    .format = {
        [PSC_VOLTAGE_OUT] = direct,
        [PSC_CURRENT_OUT] = direct,
    },
    .m = {
        [PSC_VOLTAGE_OUT] = 10,
        [PSC_CURRENT_OUT] = 10,
    },
    .b = {
        [PSC_VOLTAGE_OUT] = 0,
        [PSC_CURRENT_OUT] = 0,
    },
    .R = {
        [PSC_VOLTAGE_OUT] = 0,
        [PSC_CURRENT_OUT] = 0,
    },
    .read_word_data = &dps200_read_word_data,
};

static int pmbus_probe(struct i2c_client *client,
               const struct i2c_device_id *id)
{
    return pmbus_do_probe(client, id, &dps200_info);
}
/* user driver datat to pass the grpup */
static const struct i2c_device_id dps200_id[] = {
    {"dps200", 0},
    {}
};

MODULE_DEVICE_TABLE(i2c, dps200_id);

/* This is the driver that will be inserted */
static struct i2c_driver dps200_driver = {
    .driver = {
           .name = "dps200",
           },
    .probe = pmbus_probe,
    .remove = pmbus_do_remove,
    .id_table = dps200_id,
};

module_i2c_driver(dps200_driver);

MODULE_AUTHOR("Pradchaya Phucharoen");
MODULE_DESCRIPTION("PMBus driver for Delta DPS200");
MODULE_LICENSE("GPL");
