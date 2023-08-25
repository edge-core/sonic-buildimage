/*
 * Copyright 2019 Broadcom.
 * The term “Broadcom” refers to Broadcom Inc. and/or its subsidiaries.
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
 *
 * Description of various APIs related to FAN component
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
#include <linux/dmi.h>
#include "pddf_fan_defs.h"
#include "pddf_fan_driver.h"

/*#define FAN_DEBUG*/
#ifdef FAN_DEBUG
#define fan_dbg(...) printk(__VA_ARGS__)
#else
#define fan_dbg(...)
#endif

extern void *get_device_table(char *name);

void get_fan_duplicate_sysfs(int idx, char *str)
{
	switch (idx)
	{
		default:
			break;
	}

	return;
}


int fan_update_hw(struct device *dev, struct fan_attr_info *info, FAN_DATA_ATTR *udata)
{
	int status = 0;
    struct i2c_client *client = to_i2c_client(dev);
	FAN_SYSFS_ATTR_DATA *sysfs_attr_data = NULL;


    mutex_lock(&info->update_lock);

	sysfs_attr_data = udata->access_data;
	if (sysfs_attr_data->pre_set != NULL)
	{
		status = (sysfs_attr_data->pre_set)(client, udata, info);
		if (status!=0)
			dev_warn(&client->dev, "%s: pre_set function fails for %s attribute. ret %d\n", __FUNCTION__, udata->aname, status);
	}
	if (sysfs_attr_data->do_set != NULL)
	{
		status = (sysfs_attr_data->do_set)(client, udata, info);
		if (status!=0)
			dev_warn(&client->dev, "%s: do_set function fails for %s attribute. ret %d\n", __FUNCTION__, udata->aname, status);

	}
	if (sysfs_attr_data->post_set != NULL)
	{
		status = (sysfs_attr_data->post_set)(client, udata, info);
		if (status!=0)
			dev_warn(&client->dev, "%s: post_set function fails for %s attribute. ret %d\n", __FUNCTION__, udata->aname, status);
	}

    mutex_unlock(&info->update_lock);

    return 0;
}

int fan_update_attr(struct device *dev, struct fan_attr_info *info, FAN_DATA_ATTR *udata)
{
	int status = 0;
    struct i2c_client *client = to_i2c_client(dev);
	FAN_SYSFS_ATTR_DATA *sysfs_attr_data = NULL;


    mutex_lock(&info->update_lock);

    if (time_after(jiffies, info->last_updated + HZ + HZ / 2) || !info->valid) 
	{
        dev_dbg(&client->dev, "Starting pddf_fan update\n");
        info->valid = 0;

		sysfs_attr_data = udata->access_data;
		if (sysfs_attr_data->pre_get != NULL)
		{
			status = (sysfs_attr_data->pre_get)(client, udata, info);
			if (status!=0)
				dev_warn(&client->dev, "%s: pre_get function fails for %s attribute. ret %d\n", __FUNCTION__, udata->aname, status);
		}
		if (sysfs_attr_data->do_get != NULL)
		{
			status = (sysfs_attr_data->do_get)(client, udata, info);
			if (status!=0)
				dev_warn(&client->dev, "%s: do_get function fails for %s attribute. ret %d\n", __FUNCTION__, udata->aname, status);

		}
		if (sysfs_attr_data->post_get != NULL)
		{
			status = (sysfs_attr_data->post_get)(client, udata, info);
			if (status!=0)
				dev_warn(&client->dev, "%s: post_get function fails for %s attribute.ret %d\n", __FUNCTION__, udata->aname, status);
		}

		
        info->last_updated = jiffies;
        info->valid = 1;
    }

    mutex_unlock(&info->update_lock);

    return 0;
}

ssize_t fan_show_default(struct device *dev, struct device_attribute *da, char *buf)
{
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct i2c_client *client = to_i2c_client(dev);
    struct fan_data *data = i2c_get_clientdata(client);
    FAN_PDATA *pdata = (FAN_PDATA *)(client->dev.platform_data);
    FAN_DATA_ATTR *usr_data = NULL;
    struct fan_attr_info *attr_info = NULL;
    int i, status=0;
	char new_str[ATTR_NAME_LEN] = "";
	FAN_SYSFS_ATTR_DATA *ptr = NULL;

    for (i=0;i<data->num_attr;i++)
    {
		ptr = (FAN_SYSFS_ATTR_DATA *)pdata->fan_attrs[i].access_data;
		get_fan_duplicate_sysfs(ptr->index , new_str);
        if (strcmp(attr->dev_attr.attr.name, pdata->fan_attrs[i].aname) == 0 || strcmp(attr->dev_attr.attr.name, new_str) == 0)
        {
			attr_info = &data->attr_info[i];
            usr_data = &pdata->fan_attrs[i];
			strcpy(new_str, "");
        }
    }

    if (attr_info==NULL || usr_data==NULL)
    {
        printk(KERN_ERR "%s is not supported attribute for this client\n", usr_data->aname);
		goto exit;
	}

    fan_update_attr(dev, attr_info, usr_data);

	/*Decide the o/p based on attribute type */
	switch(attr->index)
	{
		case FAN1_PRESENT:
		case FAN2_PRESENT:
		case FAN3_PRESENT:
		case FAN4_PRESENT:
		case FAN5_PRESENT:
		case FAN6_PRESENT:
		case FAN7_PRESENT:
		case FAN8_PRESENT:
		case FAN9_PRESENT:
		case FAN10_PRESENT:
		case FAN11_PRESENT:
		case FAN12_PRESENT:
		case FAN1_DIRECTION:
		case FAN2_DIRECTION:
		case FAN3_DIRECTION:
		case FAN4_DIRECTION:
		case FAN5_DIRECTION:
		case FAN6_DIRECTION:
		case FAN7_DIRECTION:
		case FAN8_DIRECTION:
		case FAN9_DIRECTION:
		case FAN10_DIRECTION:
		case FAN11_DIRECTION:
		case FAN12_DIRECTION:
		case FAN1_INPUT:
		case FAN2_INPUT:
		case FAN3_INPUT:
		case FAN4_INPUT:
		case FAN5_INPUT:
		case FAN6_INPUT:
		case FAN7_INPUT:
		case FAN8_INPUT:
		case FAN9_INPUT:
		case FAN10_INPUT:
		case FAN11_INPUT:
		case FAN12_INPUT:
		case FAN1_PWM:
		case FAN2_PWM:
		case FAN3_PWM:
		case FAN4_PWM:
		case FAN5_PWM:
		case FAN6_PWM:
		case FAN7_PWM:
		case FAN8_PWM:
		case FAN9_PWM:
		case FAN10_PWM:
		case FAN11_PWM:
		case FAN12_PWM:
		case FAN1_FAULT:
		case FAN2_FAULT:
		case FAN3_FAULT:
		case FAN4_FAULT:
		case FAN5_FAULT:
		case FAN6_FAULT:
		case FAN7_FAULT:
		case FAN8_FAULT:
		case FAN9_FAULT:
		case FAN10_FAULT:
		case FAN11_FAULT:
		case FAN12_FAULT:
            status = attr_info->val.intval;
			break;
		default:
			fan_dbg(KERN_ERR "%s: Unable to find the attribute index for %s\n", __FUNCTION__, usr_data->aname);
			status = 0;
	}

exit:
    return sprintf(buf, "%d\n", status);
}


ssize_t fan_store_default(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct i2c_client *client = to_i2c_client(dev);
    struct fan_data *data = i2c_get_clientdata(client);
    FAN_PDATA *pdata = (FAN_PDATA *)(client->dev.platform_data);
    FAN_DATA_ATTR *usr_data = NULL;
    struct fan_attr_info *attr_info = NULL;
    int i, ret ;
	uint32_t val;

    for (i=0;i<data->num_attr;i++)
    {
		if (strcmp(data->attr_info[i].name, attr->dev_attr.attr.name) == 0 && strcmp(pdata->fan_attrs[i].aname, attr->dev_attr.attr.name) == 0)
        {
            attr_info = &data->attr_info[i];
            usr_data = &pdata->fan_attrs[i];
        }
    }

    if (attr_info==NULL || usr_data==NULL) {
		printk(KERN_ERR "%s is not supported attribute for this client\n", attr->dev_attr.attr.name);
		goto exit;
	}

	switch(attr->index)
	{
		case FAN1_PWM:
		case FAN2_PWM:
		case FAN3_PWM:
		case FAN4_PWM:
		case FAN5_PWM:
		case FAN6_PWM:
		case FAN7_PWM:
		case FAN8_PWM:
		case FAN9_PWM:
		case FAN10_PWM:
		case FAN11_PWM:
		case FAN12_PWM:
			ret = kstrtoint(buf, 10, &val);
			if (ret)
			{
				printk(KERN_ERR "%s: Unable to convert string into value for %s\n", __FUNCTION__, usr_data->aname);
				return ret;
			}
			/*Update the value of attr_info here, and use it to update the HW values*/
			attr_info->val.intval = val;
			break;
		default:
			printk(KERN_ERR "%s: Unable to find the attr index for %s\n", __FUNCTION__, usr_data->aname);
			goto exit;
	}

	fan_dbg(KERN_ERR "%s: pwm to be set is %d\n", __FUNCTION__, val);
	fan_update_hw(dev, attr_info, usr_data);

exit:
	return count;
}

int fan_cpld_client_read(FAN_DATA_ATTR *udata)
{
    int status = -1;

    if (udata!=NULL)
    {
        if (udata->len==1)
        {
            status = board_i2c_cpld_read(udata->devaddr , udata->offset);
        }
        else
        {
            /* Get the I2C client for the CPLD */
            struct i2c_client *client_ptr=NULL;
            client_ptr = (struct i2c_client *)get_device_table(udata->devname);
            if (client_ptr)
            {
                if (udata->len==2)
                {
                    status = i2c_smbus_read_word_swapped(client_ptr, udata->offset);
                }
                else
                    printk(KERN_ERR "PDDF_FAN: Doesn't support block CPLD read yet");
            }
            else
                printk(KERN_ERR "Unable to get the client handle for %s\n", udata->devname);
        }

    }

    return status;
}

int fan_cpld_client_write(FAN_DATA_ATTR *udata, uint32_t val)
{
    int status = 0;

    if (udata->len==1)
    {
        status = board_i2c_cpld_write(udata->devaddr, udata->offset, val);
    }
    else
    {
        /* Get the I2C client for the CPLD */
        struct i2c_client *client_ptr=NULL;
        client_ptr = (struct i2c_client *)get_device_table(udata->devname);
        if (client_ptr)
        {
            if (udata->len==2)
            {
                uint8_t val_lsb = val & 0xFF;
                uint8_t val_hsb = (val >> 8) & 0xFF;
                /* TODO: Check this logic for LE and BE */
                status = i2c_smbus_write_byte_data(client_ptr, udata->offset, val_lsb);
                if (status==0) status = i2c_smbus_write_byte_data(client_ptr, udata->offset+1, val_hsb);
            }
            else
                printk(KERN_ERR "PDDF_FAN: Doesn't support block CPLD write yet");
        }
        else
            printk(KERN_ERR "Unable to get the client handle for %s\n", udata->devname);
    }

    return status;
}

int fan_fpgai2c_client_read(FAN_DATA_ATTR *udata)
{
    int status = -1;

    if (udata!=NULL)
    {
        if (udata->len==1)
        {
            status = board_i2c_fpga_read(udata->devaddr , udata->offset);
            /*printk(KERN_ERR "### Reading offset 0x%x from 0x%x device ...  val 0x%x\n", udata->offset, udata->devaddr, status);*/
        }
        else
        {
            /* Get the I2C client for the FPGAI2C */
            struct i2c_client *client_ptr=NULL;
            client_ptr = (struct i2c_client *)get_device_table(udata->devname);
            if (client_ptr)
            {
                if (udata->len==2)
                {
                    status = i2c_smbus_read_word_swapped(client_ptr, udata->offset);
                }
                else
                    printk(KERN_ERR "PDDF_FAN: Doesn't support block FPGAI2C read yet");
            }
            else
                printk(KERN_ERR "Unable to get the client handle for %s\n", udata->devname);
        }

    }

    return status;
}

int fan_fpgai2c_client_write(FAN_DATA_ATTR *udata, uint32_t val)
{
    int status = 0;

    if (udata->len==1)
    {
        status = board_i2c_fpga_write(udata->devaddr, udata->offset, val);
    }
    else
    {
        /* Get the I2C client for the FPGAI2C */
        struct i2c_client *client_ptr=NULL;
        client_ptr = (struct i2c_client *)get_device_table(udata->devname);
        if (client_ptr)
        {
            if (udata->len==2)
            {
                uint8_t val_lsb = val & 0xFF;
                uint8_t val_hsb = (val >> 8) & 0xFF;
                /* TODO: Check this logic for LE and BE */
                status = i2c_smbus_write_byte_data(client_ptr, udata->offset, val_lsb);
                if (status==0) status = i2c_smbus_write_byte_data(client_ptr, udata->offset+1, val_hsb);
            }
            else
                printk(KERN_ERR "PDDF_FAN: Doesn't support block FPGAI2C write yet");
        }
        else
            printk(KERN_ERR "Unable to get the client handle for %s\n", udata->devname);
    }

    return status;
}


int sonic_i2c_get_fan_present_default(void *client, FAN_DATA_ATTR *udata, void *info)
{
    int status = 0;
    int val = 0;
    struct fan_attr_info *painfo = (struct fan_attr_info *)info;

    if (strcmp(udata->devtype, "cpld") == 0)
    {
        val = fan_cpld_client_read(udata);
    }
    else if (strcmp(udata->devtype, "fpgai2c") == 0)
    {
        val = fan_fpgai2c_client_read(udata);
    }
    else
    {
	    val = i2c_smbus_read_byte_data((struct i2c_client *)client, udata->offset);
    }
	
	if (val < 0)
		status = val;
	else
		painfo->val.intval = ((val & udata->mask) == udata->cmpval);
    

    return status;
}

int sonic_i2c_get_fan_rpm_default(void *client, FAN_DATA_ATTR *udata, void *info)
{
    int status = 0;
	int val = 0;
    struct fan_attr_info *painfo = (struct fan_attr_info *)info;

    if (strcmp(udata->devtype, "cpld") == 0)
    {
        val = fan_cpld_client_read(udata);
    }
    else if (strcmp(udata->devtype, "fpgai2c") == 0)
    {
        val = fan_fpgai2c_client_read(udata);
    }
    else
    {
        if (udata->len == 1)
        {
            val = i2c_smbus_read_byte_data((struct i2c_client *)client, udata->offset);
        }
        else if (udata->len ==2)
        {
            val = i2c_smbus_read_word_swapped((struct i2c_client *)client, udata->offset);
            
        }
    }

	if (val < 0)
		status = val;
	else
	{
		if (udata->is_divisor)
			painfo->val.intval = udata->mult / (val >> 3);
		else
			painfo->val.intval = udata->mult * val;
	}

	return status;
}


int sonic_i2c_get_fan_direction_default(void *client, FAN_DATA_ATTR *udata, void *info)
{
    int status = 0;
	int val = 0;
    struct fan_attr_info *painfo = (struct fan_attr_info *)info;

    if (strcmp(udata->devtype, "cpld") == 0)
    {
        val = fan_cpld_client_read(udata);
    }
    else if (strcmp(udata->devtype, "fpgai2c") == 0)
    {
        val = fan_fpgai2c_client_read(udata);
    }
    else
    {
	    val = i2c_smbus_read_byte_data((struct i2c_client *)client, udata->offset);
    }

    if (val < 0)
        status = val;
    else
        painfo->val.intval = ((val & udata->mask) == udata->cmpval);

    return status;
}


int sonic_i2c_set_fan_pwm_default(struct i2c_client *client, FAN_DATA_ATTR *udata, void *info)
{
    int status = 0;
	int val = 0;
    struct fan_attr_info *painfo = (struct fan_attr_info *)info;

	val = painfo->val.intval & udata->mask;

	if (val > 255)
	{
	  return -EINVAL;
	}

    if (strcmp(udata->devtype, "cpld") == 0)
    {
        status = fan_cpld_client_write(udata, val);
    }
    else if (strcmp(udata->devtype, "fpgai2c") == 0)
    {
        status = fan_fpgai2c_client_write(udata, val);
    }
    else
    {
        if (udata->len == 1)
            status = i2c_smbus_write_byte_data(client, udata->offset, val);
        else if (udata->len == 2)
        {
            uint8_t val_lsb = val & 0xFF;
            uint8_t val_hsb = (val >> 8) & 0xFF;
            /* TODO: Check this logic for LE and BE */
            status = i2c_smbus_write_byte_data(client, udata->offset, val_lsb);
            if (status == 0) status = i2c_smbus_write_byte_data(client, udata->offset+1, val_hsb);
        }
        else
        {
            printk(KERN_DEBUG "%s: pwm should be of len 1/2 bytes. Not setting the pwm as the length is %d\n", __FUNCTION__, udata->len);
        }
    }

    return status;
}


int sonic_i2c_get_fan_pwm_default(void *client, FAN_DATA_ATTR *udata, void *info)
{
    int status = 0;
	int val = 0;
    struct fan_attr_info *painfo = (struct fan_attr_info *)info;

    if (strcmp(udata->devtype, "cpld") == 0)
    {
        val = fan_cpld_client_read(udata);
    }
    else if (strcmp(udata->devtype, "fpgai2c") == 0)
    {
        val = fan_fpgai2c_client_read(udata);
    }
    else
    {
        if (udata->len == 1)
        {
            val = i2c_smbus_read_byte_data((struct i2c_client *)client, udata->offset);
        }
        else if (udata->len ==2)
        {
            val = i2c_smbus_read_word_swapped((struct i2c_client *)client, udata->offset);
            
        }
    }

	if (val < 0)
		status = val;
	else
	{
		val = val & udata->mask;
		painfo->val.intval = val;
	}
    return status;
}

int sonic_i2c_get_fan_fault_default(void *client, FAN_DATA_ATTR *udata, void *info)
{
    int status = 0;
	int val = 0;
    struct fan_attr_info *painfo = (struct fan_attr_info *)info;

	/*Assuming fan fault to be denoted by 1 byte only*/
    if (strcmp(udata->devtype, "cpld") == 0)
    {
        val = fan_cpld_client_read(udata);
    }
    else if (strcmp(udata->devtype, "fpgai2c") == 0)
    {
        val = fan_fpgai2c_client_read(udata);
    }
    else
    {
	    val = i2c_smbus_read_byte_data((struct i2c_client *)client, udata->offset);
    }

	if (val < 0)
		status = val;
	else
		painfo->val.intval = ((val & udata->mask) == udata->cmpval);
    return status;
}


int pddf_fan_post_probe_default(struct i2c_client *client, const struct i2c_device_id *dev_id)
{

	/*Dummy func for now - check the respective platform modules*/
    return 0;
}
