/* An hwmon driver for Cameo ESC600-128Q i2c Module */
#pragma GCC diagnostic ignored "-Wformat-zero-length"
#include "x86-64-cameo-esc600-128q.h"

/* Addresses scanned */
static const unsigned short normal_i2c[] = { 0x30, 0x31, 0x33, I2C_CLIENT_END };

/*function */
/*0x31 CPLD-1 700HC*/
#ifdef LED_CTRL_WANTED
/********************************************************************************/
/*    Function Name      : led_ctrl_get                                         */
/*    Description        : This is the function to get Ctrl LED Reg 0x31 0xa0   */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t led_ctrl_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == LED_CTRL)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa0); //to get register 0x31 0xa0
        debug_print((KERN_DEBUG "DEBUG : LED_CTRL status = %x\n",status));
        sprintf(buf, "");
        if (status & res)
        {
            sprintf(buf, "%sFront port LED is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sFront port LED is disabled\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : led_ctrl_set                                         */
/*    Description        : This is the function to set Ctrl LED Reg 0x31 0xa0   */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t led_ctrl_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = 0;
    u8 value  = 0;
    u8 result = 0;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *CPLD_3_data = i2c_get_clientdata(Cameo_CPLD_3_client);
    
    mutex_lock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : led_ctrl_set lock\n"));
    if (attr->index == LED_CTRL)
    {
        i = simple_strtol(buf, NULL, 10);
        switch(i)
        { 
            case TURN_ON:
                status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa0); //to get register 0x31 0xa0
                debug_print((KERN_ALERT "DEBUG : LED_CTRL status = %x\n",status)); 
                value = status | LED_ON;
                debug_print((KERN_ALERT "DEBUG : LED_CTRL value = %x\n",value));
                result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xa0, value); //to set register 0x31 0xa0
                debug_print((KERN_ALERT "DEBUG : LED_CTRL result = %x\n",result));
                if (result < 0)
                {
                    printk(KERN_ALERT "ERROR: led_ctrl_set on FAILED!\n");
                }
                else
                {
                    debug_print((KERN_ALERT "DEBUG : Fiber LED is Enable\n"));
                }
                break;
                
            case TURN_OFF:
                status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa0); //to get register 0x31 0xa0
                debug_print((KERN_DEBUG "DEBUG : LED_CTRL status = %x\n",status));
                value = status & LED_OFF;
                debug_print((KERN_DEBUG "DEBUG : LED_CTRL value = %x\n",value));
                result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xa0, value); //to set register 0x31 0xa0
                debug_print((KERN_DEBUG "DEBUG : LED_CTRL result = %x\n",result));
                if (result < 0)
                {
                    printk(KERN_ALERT "ERROR: led_ctrl_set off FAILED!\n");
                }
                else
                {
                    debug_print((KERN_DEBUG "DEBUG : Fiber LED is Disable\n"));
                }
                break;
                
            default:
            printk(KERN_ALERT "LED set wrong Value\n");
        }
    }
    mutex_unlock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : led_ctrl_set unlock\n"));
    return count;
}
#endif

/********************************************************************************/
/*    Function Name      : sensor_status_get                                    */
/*    Description        : This is the function to get thermal sensor alert     */
/*                         status 0x31 0xc0                                     */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sensor_status_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc0); //to get register 0x31 0xc0
    debug_print((KERN_DEBUG "DEBUG : sensor_status_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SENSOR_STATUS)
    {
        for (i = 1; i <= 6; i++)
        {
            switch(i)
            {
                case ALERT_TH0:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by ALERT_TH0 (LM63)\n", buf);
                    }
                    break;
                    
                case ALERT_TH1:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by ALERT_TH1\n", buf);
                    }
                    break;
                    
                case ALERT_TH2:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by ALERT_TH2\n", buf);
                    }
                    break;
                    
                case ALERT_TH3:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by ALERT_TH3\n", buf);
                    }
                    break;
                    
                case ALERT_TH4:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by ALERT_TH4\n", buf);
                    }
                    break;
                    
                case ALERT_TH5:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by ALERT_TH5 (IO Board)\n", buf);
                    }
                    break;
            }
            res = res << 1;
        }
        if(status == 0xf)
        {
            sprintf(buf, "%sNo interrupt is triggered\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sersor_status_mask_all_get                           */
/*    Description        : This is the function to get all thermal sensor alert */
/*                         status mask 0x31 0xc1                                */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sersor_status_mask_all_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc1); //to get register 0x31 0xc1
    debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_all_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SENSOR_STATUS_MASK)
    {
        for (i = 1; i <= 6; i++)
        {
            switch(i)
            {
                case ALERT_TH0_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sALERT_TH1 Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sALERT_TH1 Mask is disabled\n", buf);
                    }
                    break;
                case ALERT_TH1_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sALERT_TH2 Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sALERT_TH2 Mask is disabled\n", buf);
                    }
                    break;
                case ALERT_TH2_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sALERT_TH3 Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sALERT_TH3 Mask is disabled\n", buf);
                    }
                    break;
                case ALERT_TH3_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sALERT_TH4 Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sALERT_TH4 Mask is disabled\n", buf);
                    }
                    break;
                case ALERT_TH4_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sALERT_TH5 Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sALERT_TH5 Mask is disabled\n", buf);
                    }
                    break;
                case ALERT_TH5_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sALERT_TH6 Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sALERT_TH6 Mask is disabled\n", buf);
                    }
                    break;
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sersor_status_mask_get                               */
/*    Description        : This is the function to get thermal sensor alert     */
/*                         status mask 0x31 0xc1                                */
/*    Input(s)           : attr->index.                                         */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sersor_status_mask_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc1); //to get register 0x31 0xc1
    debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_get status = %x\n",status));
    sprintf(buf, "");
    switch(attr->index)
    {
        case ALERT_TH0_MASK:
            if (status & 0x1)
            {
                sprintf(buf, "%sALERT_TH1 Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sALERT_TH1 Mask is disabled\n", buf);
            }
            break;
        case ALERT_TH1_MASK:
            if (status & 0x2)
            {
                sprintf(buf, "%sALERT_TH2 Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sALERT_TH2 Mask is disabled\n", buf);
            }
            break;
        case ALERT_TH2_MASK:
            if (status & 0x4)
            {
                sprintf(buf, "%sALERT_TH3 Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sALERT_TH3 Mask is disabled\n", buf);
            }
            break;
        case ALERT_TH3_MASK:
            if (status & 0x8)
            {
                sprintf(buf, "%sALERT_TH4 Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sALERT_TH4 Mask is disabled\n", buf);
            }
            break;
        case ALERT_TH4_MASK:
            if (status & 0x10)
            {
                sprintf(buf, "%sALERT_TH5 Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sALERT_TH5 Mask is disabled\n", buf);
            }
            break;
        case ALERT_TH5_MASK:
            if (status & 0x20)
            {
                sprintf(buf, "%sALERT_TH6 Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sALERT_TH6 Mask is disabled\n", buf);
            }
            break;
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sersor_status_mask_set                               */
/*    Description        : This is the function to set thermal sensor alert     */
/*                         status mask 0x31 0xc1                                */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t sersor_status_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 result = 0;
    int i = 0;
    int j = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct Cameo_i2c_data *CPLD_3_data = i2c_get_clientdata(Cameo_CPLD_3_client);

    i = attr->index;
    j = simple_strtol(buf, NULL, 10); //get input ON or OFF
    debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set i: %d\n", i));
    debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set j: %d\n", j));
    mutex_lock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set lock\n"));
    if (i >= 1 && i <= 6)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc1); //to get register 0x31 0xc1
        debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set status = %x\n",status));
        if( j == TURN_ON)
        {
            status |= (1 << (i-1));
            debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set value = %x\n",status));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xc1, status); //to set register 0x31 0xc1
            debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sersor_status_mask_%d set ON FAILED!\n", i);
            }
            else
            {
                debug_print((KERN_DEBUG "sersor_status_mask_set %02d ON\n", i));
            }
        }
        else if( j == TURN_OFF)
        {
            status &= ~(1 << (i-1));
            debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set value = %x\n",status));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xc1, status); //to set register 0x31 0xc1
            debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sersor_status_mask_%d set set OFF FAILED!\n", i);
            }
            else
            {
                debug_print((KERN_DEBUG "sersor_status_mask_set %02d OFF\n", i));
            }
        }
        else
        {
            printk(KERN_ALERT "sersor_status_mask_%d set wrong value\n", i);
        }
    }
    mutex_unlock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sersor_status_mask_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : switch_alarm_get                                     */
/*    Description        : This is the function to get thermal sensor alert     */
/*                         status switch board 0x31 0xc2                        */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_alarm_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    res = 0x1;
    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc2); //to get register 0x31 0xc2
    debug_print((KERN_DEBUG "DEBUG : switch_alarm_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SWITCH_ALARM)
    {
        for (i = 1; i <= 4; i++)
        {
            if ( i == SW_ALERT_TH0)
            {
                if (!(status & res))
                {
                    sprintf(buf, "%sInterrupt is triggered by SW_ALERT_TH0\n", buf);
                }
            }
            else if( i == SW_ALERT_TH1)
            {
                if (!(status & res))
                {
                    sprintf(buf, "%sInterrupt is triggered by SW_ALERT_TH1\n", buf);
                }
            }
            else if( i == SW_ALERT_TH2)
            {
                if (!(status & res))
                {
                    sprintf(buf, "%sInterrupt is triggered by SW_ALERT_TH2\n", buf);
                }
            }
            else if( i == SW_ALERT_TH3)
            {
                if (!(status & res))
                {
                    sprintf(buf, "%sInterrupt is triggered by SW_ALERT_TH3\n", buf);
                }
            }
            res = res << 1;
        }
        if(status == 0xf)
        {
            sprintf(buf, "%sNo interrupt is triggered\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_alarm_mask_all_get                            */
/*    Description        : This is the function to get all thermal sensor alert */
/*                         status switch board mask 0x31 0xc3                   */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_alarm_mask_all_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc3); //to get register 0x31 0xc3
    debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_all_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SWITCH_ALARM_MASK)
    {
        for (i = 1; i <= 4; i++)
        {
            if ( i == SW_ALERT_TH0)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSW_ALERT_TH1 Mask is enabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSW_ALERT_TH1 Mask is disabled\n", buf);
                }
            }
            else if( i == SW_ALERT_TH1)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSW_ALERT_TH2 Mask is enabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSW_ALERT_TH2 Mask is disabled\n", buf);
                }
            }
            else if( i == SW_ALERT_TH2)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSW_ALERT_TH3 Mask is enabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSW_ALERT_TH3 Mask is disabled\n", buf);
                }
            }
            else if( i == SW_ALERT_TH3)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSW_ALERT_TH4 Mask is enabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSW_ALERT_TH4 Mask is disabled\n", buf);
                }
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_alarm_mask_get                                */
/*    Description        : This is the function to get thermal sensor alert     */
/*                         status switch board mask 0x31 0xc3                   */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_alarm_mask_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc3); //to get register 0x31 0xc3
    debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SW_ALERT_TH0_MASK)
    {
        if (status & 0x1)
        {
            sprintf(buf, "%sALERT_TH1 Mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sALERT_TH1 Mask is disabled\n", buf);
        }
    }
    else if(attr->index == SW_ALERT_TH1_MASK)
    {
        if (status & 0x2)
        {
            sprintf(buf, "%sALERT_TH2 Mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sALERT_TH2 Mask is disabled\n", buf);
        }
    }
    else if(attr->index == SW_ALERT_TH2_MASK)
    {
        if (status & 0x4)
        {
            sprintf(buf, "%sALERT_TH3 Mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sALERT_TH3 Mask is disabled\n", buf);
        }
    }
    else if(attr->index == SW_ALERT_TH3_MASK)
    {
        if (status & 0x8)
        {
            sprintf(buf, "%sALERT_TH4 Mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sALERT_TH4 Mask is disabled\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_alarm_mask_set                                */
/*    Description        : This is the function to set thermal sensor alert     */
/*                         status switch board mask 0x31 0xc3                   */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t switch_alarm_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 result = 0;
    int i = 0;
    int j = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct Cameo_i2c_data *CPLD_3_data = i2c_get_clientdata(Cameo_CPLD_3_client);

    i = attr->index;
    j = simple_strtol(buf, NULL, 10);
    debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set i: %d\n", i));
    debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set j: %d\n", j));
    mutex_lock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set lock\n"));
    if (i >= 1 && i <= 4)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xc3); //to get register 0x31 0xc3
        debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set status = %x\n",status));
        if( j == TURN_ON)
        {
            status |= (1 << (i-1));
            debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set value = %x\n",status));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xc3, status); //to set register 0x31 0xc3
            debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: switch_alarm_mask_%d set ON FAILED!\n", i);
            }
            else
            {
                debug_print((KERN_DEBUG "switch_alarm_mask_set %02d ON\n", i));
            }
        }
        else if( j == TURN_OFF)
        {
            status &= ~(1 << (i-1));
            debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set value = %x\n",status));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xc3, status); //to set register 0x31 0xc3
            debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: switch_alarm_mask_%d set set OFF FAILED!\n", i);
            }
            else
            {
                debug_print((KERN_DEBUG "switch_alarm_mask_set %02d OFF\n", i));
            }
        }
        else
        {
            printk(KERN_ALERT "switch_alarm_mask_%d set wrong value\n", i);
        }
    }
    mutex_unlock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_alarm_mask_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : sensor_int_get                                       */
/*    Description        : This is the function to get thermal sensor interrupt */
/*                         0x31 0xd0                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sensor_int_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xd0);  //to get register 0x31 0xd0
    debug_print((KERN_DEBUG "DEBUG : sensor_int_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SENSOR_INT)
    {
        for (i = 1; i <= 2; i++)
        {
            if ( i == SENSOR_INT_0)
            {
                if (!(status & res))
                {
                    sprintf(buf, "%sInterrupt is triggered by Switch Board\n", buf);
                }
            }
            else if( i == SENSOR_INT_1)
            {
                if (!(status & res))
                {
                    sprintf(buf, "%sInterrupt is triggered by Carrier Board\n", buf);
                }
            }
            res = res << 1;
        }
        if(status == 0x3)
        {
            sprintf(buf, "%sNo interrupt is triggered\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sersor_int_mask_all_get                              */
/*    Description        : This is function to get all thermal sensor interrupt */
/*                         mask 0x31 0xd1                                       */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sersor_int_mask_all_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xd1); //to get register 0x31 0xd1
    debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_all_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SENSOR_STATUS_MASK)
    {
        for (i = 1; i <= 2; i++)
        {
            if ( i == SENSOR_INT_0)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSENSOR_INT_1 Mask is enabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSENSOR_INT_1 Mask is disabled\n", buf);
                }
            }
            else if( i == SENSOR_INT_1)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSENSOR_INT_2 Mask is enabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSENSOR_INT_2 Mask is disabled\n", buf);
                }
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sersor_int_mask_get                                  */
/*    Description        : This is the function to get thermal sensor interrupt */
/*                         mask 0x31 0xd1                                       */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sersor_int_mask_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xd1); //to get register 0x31 0xd1
    debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SENSOR_INT_0_MASK)
    {
        if (status & 0x1)
        {
            sprintf(buf, "%sSENSOR_INT_1 Mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sSENSOR_INT_1 Mask is disabled\n", buf);
        }
    }
    else if(attr->index == SENSOR_INT_1_MASK)
    {
        if (status & 0x2)
        {
            sprintf(buf, "%sSENSOR_INT_2 Mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sSENSOR_INT_2 Mask is disabled\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sersor_int_mask_set                                  */
/*    Description        : This is the function to set thermal sensor interrupt */
/*                         mask 0x31 0xd1                                       */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t sersor_int_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 result = 0;
    int i = 0;
    int j = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct Cameo_i2c_data *CPLD_3_data = i2c_get_clientdata(Cameo_CPLD_3_client);

    i = attr->index;
    j = simple_strtol(buf, NULL, 10);
    debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set i: %d\n", i));
    debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set j: %d\n", j));
    mutex_lock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set lock\n"));
    
    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xd1); //to get register 0x31 0xd1
    debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set status = %x\n",status));
    if( j == TURN_ON)
    {
        status |= (1 << (i-1));
        debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set value = %x\n",status));
        result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xd1, status); //to set register 0x31 0xd1
        debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: sersor_int_mask_%d set ON FAILED!\n", i);
        }
        else
        {
            debug_print((KERN_DEBUG "sersor_int_mask_set %02d ON\n", i));
        }
    }
    else if( j == TURN_OFF)
    {
        status &= ~(1 << (i-1));
        debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set value = %x\n",status));
        result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xd1, status); //to set register 0x31 0xd1
        debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: sersor_int_mask_%d set set OFF FAILED!\n", i);
        }
        else
        {
            debug_print((KERN_DEBUG "sersor_int_mask_set %02d OFF\n", i));
        }
    }
    else
    {
        printk(KERN_ALERT "sersor_int_mask_%d set wrong value\n", i);
    }

    mutex_unlock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sersor_int_mask_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : fan_status_get                                       */
/*    Description        : This is the function to get fan status 0x30 0x00     */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
/*0x30 CPLD-1 640UHC*/
static ssize_t fan_status_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 bmc_present = -EPERM;
    u8 mask = 0x1;
    u8 res = 0x1;
    u16 fan_speed;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct i2c_client *target_client = NULL;  

    debug_print((KERN_DEBUG "DEBUG : fan_status_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == FAN_STATUS)
    {
        bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
        if (bmc_present & mask)
        {
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0xe9); //to get register 0x14 0xe9
        }
        else
        {
            status = i2c_smbus_read_byte_data(Cameo_CPLD_4_client, 0xa1); //to get register 0x35 0xa1
        }
        for (i = 1; i <= 8; i++)
        {
            if ( i >= 5 && i <= 8 )
            {
                if (status & res)
                {
                    sprintf(buf, "%sFan module %d status is Good\n", buf, i-4);
                }
                else
                {
                    sprintf(buf, "%sFan module %d status is Fail\n", buf, i-4);
                }
            }
            res = res << 1;
        }
    }
    else if (attr->index == FAN_SPEED_RPM)
    {
        bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
        if (bmc_present & mask)
        {
            target_client = Cameo_BMC_client;
            res = i2c_smbus_read_byte_data(Cameo_BMC_client, 0xe9); //to get register 0x14 0xe9
        }
        else
        {
            target_client = Cameo_CPLD_4_client;
            res = i2c_smbus_read_byte_data(Cameo_CPLD_4_client, 0xa1); //to get register 0x35 0xa1
        }
        if(res < 0) {
            sprintf(buf, "%sCheck fan present error\n", buf);
            return sprintf(buf, "%s\n",buf);
        }
        for(i=0; i<4; i++)
        {
            // skip the fan which is not present
            if(!(res & (0x01<<i)))
            {
                sprintf(buf, "%sFanModule%i RPM : N/A\n", buf, i+1);
                continue;
            }
            if(target_client == Cameo_BMC_client)
            {
                // read high byte
                status = i2c_smbus_read_byte_data(target_client, 0xe0+(i*2)+1);
                if(status < 0){
                    sprintf(buf, "%sFanModule%i RPM : read error\n", buf, i+1);
                    continue;
                }
                fan_speed = status;
                
                // read low byte
                status = i2c_smbus_read_byte_data(target_client, 0xe0+(i*2));
                if(status < 0){
                    sprintf(buf, "%sFanModule%i RPM : read error\n", buf, i+1);
                    continue;
                }
                fan_speed = ((fan_speed<<8) + status)*30;

                sprintf(buf, "%sFanModule%i : %d RPM\n", buf, i+1, fan_speed);
            }
            else
            {
                // read high byte
                status = i2c_smbus_read_byte_data(target_client, 0xA3+(i*2)+1);
                if(status < 0){
                    sprintf(buf, "%sFanModule%i RPM : read error\n", buf, i+1);
                    continue;
                }
                fan_speed = status;
                
                // read low byte
                status = i2c_smbus_read_byte_data(target_client, 0xA3+(i*2));
                if(status < 0){
                    sprintf(buf, "%sFanModule%i RPM : read error\n", buf, i+1);
                    continue;
                }
                fan_speed = ((fan_speed<<8) + status)*30;

                sprintf(buf, "%sFanModule%i : %d RPM\n", buf, i+1, fan_speed);
            }
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : fan_insert_get                                       */
/*    Description        : This is the function to get fan insert 0x30 0x01     */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t fan_insert_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 bmc_present = -EPERM;
    u8 mask = 0x1;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
    if (bmc_present & mask)
    {
        status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0xe9); //to get register 0x14 0xe9
    }
    else
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_4_client, 0xa1); //to get register 0x35 0xa1
    }
    debug_print((KERN_DEBUG "DEBUG : fan_insert_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == FAN_INSERT)
    {
        for (i = 1; i <= 4; i++)
        {
            if (status & res)
            {
                sprintf(buf, "%sFan module %d is Insert\n", buf, i);
            }
            else
            {
                sprintf(buf, "%sFan module %d is Absent\n", buf, i);
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : fan_power_get                                        */
/*    Description        : This is the function to get fan power 0x30 0x02      */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t fan_power_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 bmc_present = -EPERM;
    u8 mask = 0x1;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
    if (bmc_present & mask)
    {
        status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0xea); //to get register 0x14 0xe9
    }
    else
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_4_client, 0xa2); //to get register 0x35 0xa1
    }
    debug_print((KERN_DEBUG "DEBUG : fan_power_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == FAN_POWER)
    {
        for (i = 1; i <= 8; i++)
        {
            if ( i >= 5 && i <= 8 )
            {
                if (status & res)
                {
                    sprintf(buf, "%sFan module %d status is Power ON\n", buf, i-4);
                }
                else
                {
                    sprintf(buf, "%sFan module %d status is Power OFF\n", buf, i-4);
                }
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : fan_direct_get                                       */
/*    Description        : This is the function to get fan direct 0x30 0x03     */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t fan_direct_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 bmc_present = -EPERM;
    u8 mask = 0x1;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
    if (bmc_present & mask)
    {
        status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0xea); //to get register 0x14 0xe9
    }
    else
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_4_client, 0xa2); //to get register 0x35 0xa1
    }
    debug_print((KERN_DEBUG "DEBUG : fan_direct_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == FAN_DIRECT)
    {
        for (i = 1; i <= 4; i++)
        {
            if (status & res)
            {
                sprintf(buf, "%sFan module %d direction is OUT\n", buf, i);
            }
            else
            {
                sprintf(buf, "%sFan module %d direction is IN\n", buf, i);
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : usb_power_get                                        */
/*    Description        : This is the function to get usb power 0x30 0xa0      */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t usb_power_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == USB_POWER)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa0); //to get register 0x30 0xa0
        debug_print((KERN_DEBUG "DEBUG : USB_POWER status = %x\n",status));
        sprintf(buf, "");
        if (status & res)
        {
            sprintf(buf, "%sUSB Power is ON\n", buf);
        }
        else
        {
            sprintf(buf, "%sUSB Power is OFF\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : usb_power_set                                        */
/*    Description        : This is the function to set usb power 0x30 0xa0      */
/*                                                                              */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t usb_power_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *CPLD_2_data = i2c_get_clientdata(Cameo_CPLD_2_client);
    
    mutex_lock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : usb_power_set lock\n"));
    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa0); //to get register 0x30 0xa0
    debug_print((KERN_DEBUG "DEBUG : usb_power_set status = %x\n",status));
    if (attr->index == USB_POWER)
    {
        i = simple_strtol(buf, NULL, 10); //get input ON or OFF
        if (i == TURN_ON)
        {
            value = status | USB_ON;
            debug_print((KERN_DEBUG "DEBUG : usb_power_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa0, value); //to set register 0x30 0xa0
            debug_print((KERN_DEBUG "DEBUG : usb_power_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: usb_ctrl_set ON FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "USB Power is ON\n"));
            }
        }
        else if (i == TURN_OFF)
        {
            value = status & USB_OFF;
            debug_print((KERN_DEBUG "DEBUG : usb_power_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa0, value); //to set register 0x30 0xa0
            debug_print((KERN_DEBUG "DEBUG : usb_power_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: usb_power_set OFF FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "USB Power is OFF\n"));
            }
        }
        else
        {
            printk(KERN_ALERT "USB_POWER set wrong Value\n");
        }
    }
    mutex_unlock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : usb_power_set unlock\n"));
    return count;
}

#ifdef WDT_CTRL_WANTED
/********************************************************************************/
/*    Function Name      : wdt_status_get                                       */
/*    Description        : This is the function to get WDT timer                */
/*                                                                              */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t wdt_status_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x10;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == WDT_CTRL)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa0); //to get register 0x30 0xa0
        debug_print((KERN_DEBUG "DEBUG : WDT status = %x\n",status));
        sprintf(buf, "");
        if (status & res)
        {
            sprintf(buf, "%sWDT is Enable\n", buf);
        }
        else
        {
            sprintf(buf, "%sWDT is Disable\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}
/********************************************************************************/
/*    Function Name      : wdt_status_set                                       */
/*    Description        : This is the function to set WDT timer                */
/*                                                                              */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t wdt_status_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *CPLD_2_data = i2c_get_clientdata(Cameo_CPLD_2_client);
    
    mutex_lock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : wdt_status_set lock\n"));
    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa0); //to get register 0x30 0xa0
    debug_print((KERN_DEBUG "DEBUG : wdt_status_set status = %x\n",status));
    if (attr->index == WDT_CTRL)
    {
        i = simple_strtol(buf, NULL, 10); //get input ON or OFF
        if (i == TURN_ON)
        {
            value = status | 0x10;
            debug_print((KERN_DEBUG "DEBUG : wdt_status_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa0, value); //to set register 0x30 0xa0
            debug_print((KERN_DEBUG "DEBUG : wdt_status_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: usb_ctrl_set ON FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "WDT is Enable\n"));
            }
        }
        else if (i == TURN_OFF)
        {
            value = status & 0xef;
            debug_print((KERN_DEBUG "DEBUG : wdt_status_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa0, value); //to set register 0x30 0xa0
            debug_print((KERN_DEBUG "DEBUG : wdt_status_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: wdt_status_set OFF FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "WDT is Disable\n"));
            }
        }
        else
        {
            printk(KERN_ALERT "WDT set wrong Value\n");
        }
    }
    mutex_unlock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : wdt_status_set unlock\n"));
    return count;
}
#endif /*WDT_CTRL_WANTED*/
/********************************************************************************/
/*    Function Name      : shutdown_sys_get                                     */
/*    Description        : This is the function to get shutdown status          */
/*                                                                              */
/*    Input(s)           : 0.                                                   */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
static ssize_t shutdown_sys_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x10;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == SYS_SHUTDOWN)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa1); //to get register 0x30 0xa1
        debug_print((KERN_DEBUG "DEBUG : Shutdown status = %x\n",status));
        sprintf(buf, "");
        if (status & res)
        {
            sprintf(buf, "%sShutdown is triggered\n", buf);
        }
        else
        {
            sprintf(buf, "%sShutdown is not triggered\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}
/********************************************************************************/
/*    Function Name      : shutdown_sys_set                                     */
/*    Description        : This is the function to set shutdown status          */
/*                                                                              */
/*    Input(s)           : 0.                                                   */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
static ssize_t shutdown_sys_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *CPLD_2_data = i2c_get_clientdata(Cameo_CPLD_2_client);
    
    mutex_lock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : shutdown_sys_set lock\n"));
    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa1); //to get register 0x30 0xa0
    debug_print((KERN_DEBUG "DEBUG : shutdown_sys_set status = %x\n",status));
    if (attr->index == WDT_CTRL)
    {
        i = simple_strtol(buf, NULL, 10); //get input ON or OFF
        if (i == TURN_ON)
        {
            value = status | 0x10;
            debug_print((KERN_DEBUG "DEBUG : shutdown_sys_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa1, value); //to set register 0x30 0xa0
            debug_print((KERN_DEBUG "DEBUG : shutdown_sys_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: usb_ctrl_set ON FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "Shutdown is Enable\n"));
            }
        }
        else if (i == TURN_OFF)
        {
            value = status & 0xef;
            debug_print((KERN_DEBUG "DEBUG : shutdown_sys_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa1, value); //to set register 0x30 0xa0
            debug_print((KERN_DEBUG "DEBUG : shutdown_sys_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: shutdown_sys_set OFF FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "Shutdown is Disable\n"));
            }
        }
        else
        {
            printk(KERN_ALERT "Shutdown set wrong Value\n");
        }
    }
    mutex_unlock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : shutdown_sys_set unlock\n"));
    return count;
}
/********************************************************************************/
/*    Function Name      : reset_sys_set                                        */
/*    Description        : This is the function to reset system 0x30 0xa1       */
/*                                                                              */
/*    Input(s)           : 0.                                                   */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t reset_sys_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = 0;
    u8 value  = 0;
    u8 result = 0;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *CPLD_2_data = i2c_get_clientdata(Cameo_CPLD_2_client);
    
    mutex_lock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : reset_sys_set lock\n"));
    status  = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa1); //to get register 0x30 0xa1
    debug_print((KERN_DEBUG "DEBUG : SYS_RESET status = %x\n",status));
    if (attr->index == SYS_RESET)
    {
        i = simple_strtol(buf, NULL, 10); //get input 0 to reset system
        if (i == 0)
        {
            value = 0x0; //value 0 to reset system
            debug_print((KERN_DEBUG "DEBUG : reset_sys_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa1, value); //to set register 0x30 0xa1
            debug_print((KERN_DEBUG "DEBUG : reset_sys_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: reset_sys_set set FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "Switch is reset\n"));
            }
        }
        else
        {
            printk(KERN_ALERT "reset_sys_set set wrong Value\n");
        }
    }
    mutex_unlock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : reset_sys_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : module_reset_set                                     */
/*    Description        : This is the function to reset PHY module 0x30 0xa2   */
/*                                                                              */
/*    Input(s)           : PHY module number.                                   */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t module_reset_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 result = 0;
    int card_num = 0;
    int input = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct Cameo_i2c_data *CPLD_2_data = i2c_get_clientdata(Cameo_CPLD_2_client);

    if (attr->index == MODULE_RESET)
    {
        input = simple_strtol(buf, NULL, 10); //get input module number
        if(input <= 0 || input > 8)
        {
            printk(KERN_ALERT "ERROR: module_reset_%d RESET FAILED!\n", input);
        }
        else
        {
            mutex_lock(&CPLD_2_data->update_lock);
            debug_print((KERN_DEBUG "DEBUG : module_reset_set lock\n"));
            status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa2); //to get register 0x30 0xa2
            debug_print((KERN_DEBUG "DEBUG : module_reset_set status = %x\n",status));
            status &= ~(1 << (input-1));
            debug_print((KERN_DEBUG "DEBUG : module_reset_set value = %x\n",status));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa2, status); //to set register 0x30 0xa2
            debug_print((KERN_DEBUG "DEBUG : module_reset_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: module_reset_%d RESET FAILED!\n", card_num);
            }
            else
            {
                debug_print((KERN_DEBUG "module_reset_%02d SUCCESS\n", card_num));
            }
        }
    }
    mutex_unlock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : module_reset_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : module_insert_get                                    */
/*    Description        : This is the function to get module insert 0x30 0xa3  */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t module_insert_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa3); //get slot present status 0x30 0xa3
    debug_print((KERN_DEBUG "DEBUG : module_insert_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == MODULE_INSERT)
    {
        for (i = 1; i <= 8; i++)
        {
            if (status & res)
            {
                sprintf(buf, "%sModule %d is present\n", buf , i);
            }
            else
            {
                sprintf(buf, "%sModule %d is not present\n", buf, i);
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}
/********************************************************************************/
/*    Function Name      : module_power_get                                    */
/*    Description        : This is the function to get module insert 0x30 0xa3  */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t module_power_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa4); //get slot present status 0x30 0xa3
    debug_print((KERN_DEBUG "DEBUG : module_power_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == MODULE_POWER)
    {
        for (i = 1; i <= 8; i++)
        {
            if (status & res)
            {
                sprintf(buf, "%sModule %d is power good\n", buf , i);
            }
            else
            {
                sprintf(buf, "%sModule %d is not power good\n", buf, i);
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : module_12v_status_get                                    */
/*    Description        : This is the function to get module insert 0x30 0xa3  */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t module_12v_status_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa5); //get slot present status 0x30 0xa3
    debug_print((KERN_DEBUG "DEBUG : module_12v_status_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == MODULE_12V_STAT)
    {
        for (i = 1; i <= 8; i++)
        {
            if (status & res)
            {
                sprintf(buf, "%sModule %d 12V is enable\n", buf , i);
            }
            else
            {
                sprintf(buf, "%sModule %d 12V is disable\n", buf, i);
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : module_enable_get                                    */
/*    Description        : This is the function to get module insert 0x30 0xa3  */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t module_enable_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xa5); //get slot present status 0x30 0xa3
    debug_print((KERN_DEBUG "DEBUG : module_enable_get status = %x\n",status));
    if (attr->index == MODULE_ENABLE)
    {
        sprintf(buf, "%s0x%x\n", buf, status);
    }
    return sprintf(buf, "%s", buf);
}
/********************************************************************************/
/*    Function Name      : module_enable_set                                     */
/*    Description        : This is the function to reset PHY module 0x30 0xa2   */
/*                                                                              */
/*    Input(s)           : PHY module number.                                   */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t module_enable_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 result = 0;
    int input = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct Cameo_i2c_data *CPLD_2_data = i2c_get_clientdata(Cameo_CPLD_2_client);

    if (attr->index == MODULE_ENABLE)
    {
        input = simple_strtol(buf, NULL, 16); //get input module number
        debug_print((KERN_DEBUG "DEBUG : module_enable_set input = %x \n",input));

        mutex_lock(&CPLD_2_data->update_lock);
        result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xa5, input); //to set register 0x30 0xa2
        debug_print((KERN_DEBUG "DEBUG : module_enable_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: module RESET FAILED!\n");
        }
        else
        {
            debug_print((KERN_DEBUG "module enable SUCCESS\n"));
        }
        mdelay(1000);
    }
    mutex_unlock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : module_enable_set unlock\n"));
    return count;
}
/********************************************************************************/
/*    Function Name      : switch_int_get                                       */
/*    Description        : This is the function to get switch interrupt status  */
/*                         0x30 0xd0                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_int_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xd0); //to get register 0x30 0xd0
    debug_print((KERN_DEBUG "DEBUG : switch_int_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SWITCH_INT)
    {
        for (i = 1; i <= 6; i++)
        {
            switch(i)
            {
                case MODULE_INS_INT:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by Module insert\n", buf);
                    }
                    break;
                case MODULE_INT:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by Module\n", buf);
                    }
                    break;
                case MODULE_POWER_INT:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by Module Power\n", buf);
                    }
                    break;
                case THER_SENSOR_INT:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by Thermal Sensor\n", buf);
                    }
                    break;
                case IO_BOARD_INT:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by IO Board\n", buf);
                    }
                    break;
                case FAN_ERROR_INT:
                    if (!(status & res))
                    {
                        sprintf(buf, "%sInterrupt is triggered by FAN ERROR\n", buf);
                    }
                    break;
            }
            res = res << 1;
        }
        if(status == 0xf)
        {
            sprintf(buf, "%sNo interrupt is triggered\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_int_mask_all_get                              */
/*    Description        : This is the function to get all switch interrupt     */
/*                         mask status 0x30 0xd1                                */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_int_mask_all_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xd1); //to get register 0x30 0xd1
    debug_print((KERN_DEBUG "DEBUG : switch_int_mask_all_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SWITCH_INT_MASK)
    {
        for (i = 1; i <= 6; i++)
        {
            switch(i)
            {
                case MODULE_INS_INT_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sModule insert interrupt Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sModule insert interrupt Mask is disabled\n", buf);
                    }
                    break;
                case MODULE_INT_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sModule interrupt Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sModule interrupt Mask is disabled\n", buf);
                    }
                    break;
                case MODULE_POW_INT_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sModule power interrupt Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sModule power interrupt Mask is disabled\n", buf);
                    }
                    break;
                case THER_SEN_INT_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sThermal Sensor interrupt Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sThermal Sensor interrupt Mask is disabled\n", buf);
                    }
                    break;
                case IO_BOARD_INT_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sIO Board interrupt Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sIO Board interrupt Mask is disabled\n", buf);
                    }
                    break;
                case FAN_ERROR_INT_MASK:
                    if (status & res)
                    {
                        sprintf(buf, "%sFan error interrupt Mask is enabled\n", buf);
                    }
                    else
                    {
                        sprintf(buf, "%sFan error interrupt Mask is disabled\n", buf);
                    }
                    break;
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_int_mask_get                                  */
/*    Description        : This is the function to get  switch interrupt        */
/*                         mask status 0x30 0xd1                                */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_int_mask_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xd1); //to get register 0x30 0xd1
    debug_print((KERN_DEBUG "DEBUG : switch_int_mask_get status = %x\n",status));
    sprintf(buf, "");
    switch(attr->index)
    {
        case MODULE_INS_INT_MASK:
            if (status & 0x1)
            {
                sprintf(buf, "%sModule insert interrupt Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sModule insert interrupt Mask is disabled\n", buf);
            }
            break;
        case MODULE_INT_MASK:
            if (status & 0x2)
            {
                sprintf(buf, "%sModule interrupt Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sModule interrupt Mask is disabled\n", buf);
            }
            break;
        case MODULE_POW_INT_MASK:
            if (status & 0x4)
            {
                sprintf(buf, "%sModule power interrupt Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sModule power interrupt Mask is disabled\n", buf);
            }
            break;
        case THER_SEN_INT_MASK:
            if (status & 0x8)
            {
                sprintf(buf, "%sThermal Sensor interrupt Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sThermal Sensor interrupt Mask is disabled\n", buf);
            }
            break;
        case IO_BOARD_INT_MASK:
            if (status & 0x10)
            {
                sprintf(buf, "%sIO Board interrupt Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sIO Board interrupt Mask is disabled\n", buf);
            }
            break;
        case FAN_ERROR_INT_MASK:
            if (status & 0x20)
            {
                sprintf(buf, "%sFan error interrupt Mask is enabled\n", buf);
            }
            else
            {
                sprintf(buf, "%sFan error interrupt Mask is disabled\n", buf);
            }
            break;
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_int_mask_set                                  */
/*    Description        : This is the function to set  switch interrupt        */
/*                         mask status 0x30 0xd1                                */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None  .                                              */
/********************************************************************************/
static ssize_t switch_int_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 result = 0;
    int i = 0;
    int j = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct Cameo_i2c_data *CPLD_2_data = i2c_get_clientdata(Cameo_CPLD_2_client);

    i = attr->index;
    j = simple_strtol(buf, NULL, 10);
    debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set i: %d\n", i));
    debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set j: %d\n", j));
    mutex_lock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set lock\n"));
    if (i >= 1 && i <= 6)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0xd1); //to get register 0x30 0xd1
        debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set status = %x\n",status));
        if( j == TURN_ON)
        {
            status |= (1 << (i-1));
            debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set value = %x\n",status));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xd1, status); //to set register 0x30 0xd1
            debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: switch_int_mask_%d set ON FAILED!\n", i);
            }
            else
            {
                debug_print((KERN_DEBUG "switch_int_mask_set %02d ON\n", i));
            }
        }
        else if( j == TURN_OFF)
        {
            status &= ~(1 << (i-1));
            debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set value = %x\n",status));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_2_client, 0xd1, status); //to set register 0x30 0xd1
            debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: switch_int_mask_%d set set OFF FAILED!\n", i);
            }
            else
            {
                debug_print((KERN_DEBUG "switch_int_mask_set %02d OFF\n", i));
            }
        }
        else
        {
            printk(KERN_ALERT "switch_int_mask_%d set wrong value\n", i);
        }
    }
    mutex_unlock(&CPLD_2_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_int_mask_set unlock\n"));
    return count;
}

/*0x33 I/O Board CPLD*/
/********************************************************************************/
/*    Function Name      : sfp_select_get                                       */
/*    Description        : This is the function to get sfp i2c interface        */
/*                         status 0x33 0x20                                     */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sfp_select_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == SFP_SELECT)
    {
        status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0x60); //to get register 0x33 0x60
        debug_print((KERN_DEBUG "DEBUG : SFP_SELECT status = %x\n",status));
        sprintf(buf, "");
        if (status & 0x1)
        {
            sprintf(buf, "%sI2C interface is set Port 1\n", buf);
        }
        else if (status & 0x2)
        {
            sprintf(buf, "%sI2C interface is set Port 2\n", buf);
        }
        else if (status & 0x3)
        {
            sprintf(buf, "%sI2C interface is set Port MGM\n", buf);
        }
        else
        {
            sprintf(buf, "%sI2C interface is NOT SET\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sfp_select_set                                       */
/*    Description        : This is the function to set sfp i2c interface        */
/*                         status 0x33 0x20                                     */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t sfp_select_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);
    
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sfp_select_set lock\n"));
    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0x60); //to get register 0x33 0x60
    debug_print((KERN_DEBUG "DEBUG : sfp_select_set status = %x\n",status));
    if (attr->index == SFP_SELECT)
    {
        i = simple_strtol(buf, NULL, 10);
        if (i == 0)
        {
            value = 0x0;
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x60, value); //to set register 0x33 0x60
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: I2C interface is set Port 1 FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "I2C interface is NOT set\n"));
            }
        }
        else if (i == 1)
        {
            value = 0x1;
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x60, value); //to set register 0x33 0x60
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: I2C interface is set Port 1 FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "I2C interface is set Port 1\n"));
            }
        }
        else if (i == 2)
        {
            value = 0x2;
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x60, value); //to set register 0x33 0x60
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: I2C interface is set Port 2 FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "I2C interface is set Port 2\n"));
            }
        }
        else if (i == 3)
        {
            value = 0x3;
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x60, value); //to set register 0x33 0x60
            debug_print((KERN_DEBUG "DEBUG : sfp_select_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: I2C interface is set Port MGM FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "I2C interface is set Port MGM\n"));
            }
        }
        else
        {
            printk(KERN_ALERT "SFP_SELECT set wrong Value\n");
        }
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sfp_select_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : sfp_tx_get                                           */
/*    Description        : This is the function to get sfp tx status            */
/*                         0x33 0x70                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sfp_tx_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0x70); //to get register 0x33 0x70
    debug_print((KERN_DEBUG "DEBUG : sfp_tx_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SFP_TX_DISABLE)
    {
        for (i = 1; i <= 3; i++)
        {
            if ( i == SFP_PORT_1)
            {
                if (status & res)
                {
                    sprintf(buf, "%sTX of SFP port 1 is disabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sTX of SFP port 1 is enabled\n", buf);
                }
            }
            else if( i == SFP_PORT_2)
            {
                if (status & res)
                {
                    sprintf(buf, "%sTX of SFP port 2 is disabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sTX of SFP port 2 is enabled\n", buf);
                }
            }
            else if( i == SFP_PORT_MGM)
            {
                if (status & res)
                {
                    sprintf(buf, "%sTX of SFP port MGM is disabled\n", buf);
                }
                else
                {
                    sprintf(buf, "%sTX of SFP port MGM is enabled\n", buf);
                }
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sfp_tx_set                                           */
/*    Description        : This is the function to set sfp tx status            */
/*                         0x33 0x70                                            */
/*    Input(s)           : 1 ~ 4.                                               */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t sfp_tx_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);
    
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sfp_tx_set lock\n"));
    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0x70); //to get register 0x33 0xa0
    debug_print((KERN_DEBUG "DEBUG : sfp_tx_set status = %x\n",status));
    if (attr->index == SFP_TX_DISABLE)
    {
        i = simple_strtol(buf, NULL, 10);
        if (i == SFP_PORT_1_OFF) //i = 1
        {
            value = status | 0x1;
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x70, value); //to set register 0x33 0xa0
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sfp_tx_set PORT_1 OFF FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "SFP_PORT_1 is OFF\n"));
            }
        }
        else if (i == SFP_PORT_1_ON) //i = 2
        {
            value = status & 0xfe;
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x70, value); //to set register 0x33 0xa0
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sfp_tx_set PORT_1 ON FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "SFP_PORT_1 is ON\n"));
            }
        }
        else if (i == SFP_PORT_2_OFF) //i = 3
        {
            value = status | 0x2;
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x70, value); //to set register 0x33 0xa0
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sfp_tx_set PORT_2 OFF FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "SFP_PORT_2 is OFF\n"));
            }
        }
        else if (i == SFP_PORT_2_ON) //i = 4
        {
            value = status & 0xfd;
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x70, value); //to set register 0x33 0xa0
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sfp_tx_set PORT_2 ON FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "SFP_PORT_2 is ON\n"));
            }
        }
        else if (i == SFP_PORT_MGM_OFF) //i = 5
        {
            value = status | 0x4;
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x70, value); //to set register 0x33 0xa0
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sfp_tx_set MGM OFF FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "SFP_PORT_MGM is OFF\n"));
            }
        }
        else if (i == SFP_PORT_MGM_ON) //i = 6
        {
            value = status & 0xfb;
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0x70, value); //to set register 0x33 0xa0
            debug_print((KERN_DEBUG "DEBUG : sfp_tx_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: sfp_tx_set MGM ON FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "SFP_PORT_MGM is ON\n"));
            }
        }
        else
        {
            printk(KERN_ALERT "SFP_TX set wrong Value\n");
        }
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : usb_power_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : sfp_insert_get                                       */
/*    Description        : This is the function to get sfp insert status        */
/*                         0x33 0x80                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sfp_insert_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0x80); //to get register 0x33 0x80 
    debug_print((KERN_DEBUG "DEBUG : sfp_insert_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SFP_INSERT)
    {
        for (i = 1; i <= 3; i++)
        {
            if ( i == SFP_PORT_1)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSFP port 1 is not present\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSFP port 1 is present\n", buf);
                }
            }
            else if( i == SFP_PORT_2)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSFP port 2 is not present\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSFP port 2 is present\n", buf);
                }
            }
            else if( i == SFP_PORT_MGM)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSFP port MGM is not present\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSFP port MGM is present\n", buf);
                }
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sfp_rx_get                                           */
/*    Description        : This is the function to get sfp rx loss status       */
/*                         0x33 0x90                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sfp_rx_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0x90); //to get register 0x33 0x90
    debug_print((KERN_DEBUG "DEBUG : sfp_rx_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SFP_RX_LOSS)
    {
        for (i = 1; i <= 3; i++)
        {
            if ( i == SFP_PORT_1)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSFP port 1 receiver loss of signal\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSFP port 1 receiver signal is detceted\n", buf);
                }
            }
            else if( i == SFP_PORT_2)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSFP port 2 receiver loss of signal\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSFP port 2 receiver signal is detceted\n", buf);
                }
            }
            else if( i == SFP_PORT_MGM)
            {
                if (status & res)
                {
                    sprintf(buf, "%sSFP port MGM receiver loss of signal\n", buf);
                }
                else
                {
                    sprintf(buf, "%sSFP port MGM receiver signal is detceted\n", buf);
                }
            }
            res = res << 1;
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : psu_status_get                                       */
/*    Description        : This is the function to get psu status               */
/*                         0x33 0xa0                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t psu_status_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 bmc_present = -EPERM;
    u8 res = 0x1;
    u8 mask = 0x1;
    int i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
    if (bmc_present & mask)
    {
        status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0xe8); //to get register 0x14 0xe8
    }
    else
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_4_client, 0xa0); //to get register 0x35 0xa0
    }
    debug_print((KERN_DEBUG "DEBUG : psu_status_get status = %x\n",status));
    sprintf(buf, "");
    switch (attr->index)
    {
        case PSU_PRESENT:
            res = 0x1;
            for (i = 1; i <= 4; i++)
            {
                if (status & res)
                {
                    sprintf(buf, "%sPSU %d is present\n", buf, i);
                }
                else
                {
                    sprintf(buf, "%sPSU %d is not present\n", buf, i);
                }
                res = res << 1;
            }
            break;
        case PSU_STATUS:
            res = 0x1;
            for (i = 1; i <= 8; i++)
            {
                if (i >= 5 && i <=8)
                {
                    if (status & res)
                    {
                        sprintf(buf, "%sPSU %d is not power good\n", buf, i - 4);
                    }
                    else
                    {
                        sprintf(buf, "%sPSU %d is power good\n", buf, i - 4);
                    }
                }
                res = res << 1;
            }
            break;
    }
    return sprintf(buf, "%s", buf);
}

#ifdef LINEAR_CONVERT_FUNCTION
static long read_reg_linear(s32 data)
{
	s16 exponent;
	s32 mantissa;
	long val;

    exponent = ((s16)data) >> 11;
    mantissa = ((s16)((data & 0x7ff) << 5)) >> 5;

	val = mantissa;
    val = val * 1000L;

	if (exponent >= 0)
		val <<= exponent;
	else
		val >>= -exponent;

	return val/1000;
}
#endif /*LINEAR_CONVERT_FUNCTION*/
/********************************************************************************/
/*    Function Name      : switch_button_get                                    */
/*    Description        : This is the function to get switch button status     */
/*                         0x33 0xa1                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_button_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa1); //to get register 0x33 0xa1
    debug_print((KERN_DEBUG "DEBUG : switch_button_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SWITCH_BUTTON)
    {
        if (status & res)
        {
            sprintf(buf, "%sSwitch button is normal\n", buf);
        }
        else
        {
            sprintf(buf, "%sSwitch button is press and hold\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sys_led_get                                          */
/*    Description        : This is the function to get switch sys LED status    */
/*                         0x33 0xa2                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sys_led_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    int led_a_status = 0;
    int led_g_status = 0;
    int led_b_status = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa2); //to get register 0x33 0xa2
    debug_print((KERN_DEBUG "DEBUG : sys_led_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == SYS_LED)
    {
        for (i = 1; i <= 3; i++)
        {
            if ( i == SYS_LED_A)
            {
                if (status & res)
                {
                    led_a_status = TURN_ON;
                }
                else
                {
                    led_a_status = TURN_OFF;
                }
            }
            else if( i == SYS_LED_G)
            {
                if (status & res)
                {
                    led_g_status = TURN_ON;
                }
                else
                {
                    led_g_status = TURN_OFF;
                }
            }
            else if( i == SYS_LED_BLINK)
            {
                if (status & res)
                {
                    led_b_status = TURN_ON;
                }
                else
                {
                    led_b_status = TURN_OFF;
                }
            }
            res = res << 1;
        }
        
        if(led_a_status == TURN_ON && led_b_status == TURN_ON)
        {
            sprintf(buf, "%sSYS LED is set to amber and blink\n", buf);
        }
        else if(led_a_status == TURN_ON && led_b_status == TURN_OFF)
        {
            sprintf(buf, "%sSYS LED is set to amber\n", buf);
        }
        else if(led_g_status == TURN_ON && led_b_status == TURN_ON)
        {
            sprintf(buf, "%sSYS LED is set to green and blink\n", buf);
        }
        else if(led_g_status == TURN_ON && led_b_status == TURN_OFF)
        {
            sprintf(buf, "%sSYS LED is set to green\n", buf);
        }
        else
        {
            sprintf(buf, "%sSYS LED is set OFF\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : sys_led_Set                                          */
/*    Description        : This is the function to set switch sys LED status    */
/*                         0x33 0xa2                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sys_led_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);
    
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sys_led_set lock\n"));
    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa2); //to get register 0x33 0xa2
    debug_print((KERN_DEBUG "DEBUG : sys_led_set status = %x\n",status));
    if (attr->index == SYS_LED)
    {
        i = simple_strtol(buf, NULL, 10);
        switch(i)
        {
            case SYS_LED_OFF:
                value = 0x0;
                debug_print((KERN_DEBUG "DEBUG : sys_led_set value = %x\n",value));
                result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa2, value); //to set register 0x33 0xa2
                debug_print((KERN_DEBUG "DEBUG : sys_led_set result = %x\n",result));
                if (result < 0)
                {
                    printk(KERN_ALERT "ERROR: sys_led_set SYS_LED_OFF FAILED!\n");
                }
                else
                {
                    debug_print((KERN_DEBUG "SYS LED is set OFF\n"));
                }
                break;
            case SYS_LED_A_N:
                value = 0x1;
                debug_print((KERN_DEBUG "DEBUG : sys_led_set value = %x\n",value));
                result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa2, value); //to set register 0x33 0xa2
                debug_print((KERN_DEBUG "DEBUG : sys_led_set result = %x\n",result));
                if (result < 0)
                {
                    printk(KERN_ALERT "ERROR: sys_led_set SYS_LED_A_N FAILED!\n");
                }
                else
                {
                    debug_print((KERN_DEBUG "SYS LED is set Amber\n"));
                }
                break;
            case SYS_LED_A_B:
                value = 0x5;
                debug_print((KERN_DEBUG "DEBUG : sys_led_set value = %x\n",value));
                result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa2, value); //to set register 0x33 0xa2
                debug_print((KERN_DEBUG "DEBUG : sys_led_set result = %x\n",result));
                if (result < 0)
                {
                    printk(KERN_ALERT "ERROR: sys_led_set SYS_LED_A_B FAILED!\n");
                }
                else
                {
                    debug_print((KERN_DEBUG "SYS LED is set Amber and Blink\n"));
                }
                break;
            case SYS_LED_G_N:
                value = 0x2;
                debug_print((KERN_DEBUG "DEBUG : sys_led_set value = %x\n",value));
                result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa2, value); //to set register 0x33 0xa2
                debug_print((KERN_DEBUG "DEBUG : sys_led_set result = %x\n",result));
                if (result < 0)
                {
                    printk(KERN_ALERT "ERROR: sys_led_set SYS_LED_G_N FAILED!\n");
                }
                else
                {
                    debug_print((KERN_DEBUG "SYS LED is set Green\n"));
                }
                break;
            case SYS_LED_G_B:
                value = 0x6;
                debug_print((KERN_DEBUG "DEBUG : sys_led_set value = %x\n",value));
                result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa2, value); //to set register 0x33 0xa2
                debug_print((KERN_DEBUG "DEBUG : sys_led_set result = %x\n",result));
                if (result < 0)
                {
                    printk(KERN_ALERT "ERROR: sys_led_set SYS_LED_G_B FAILED!\n");
                }
                else
                {
                    debug_print((KERN_DEBUG "SYS LED is set Green and Blink\n"));
                }
                break;
            default:
                printk(KERN_ALERT "SYS LED set wrong Value\n");
        }
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : sys_led_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : switch_led_all_get                                   */
/*    Description        : This is the function to get all switch LED status    */
/*                         0x33 0xa3 ~ 0xa8                                     */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_led_all_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 a_shift = 0x1;
    u8 g_shift = 0x2;
    u8 b_shift = 0x1;
#ifdef LED_L3_CTRL_WANTED
    u8 led_3_status = 0;
    u8 led_3_blink  = 0;
#endif /*LED_L3_CTRL_WANTED*/
    u8 led_4_status = 0;
    u8 led_4_blink  = 0;
    u8 led_5_status = 0;
    u8 led_5_blink  = 0;
    u8 led_status_reg = 0xa3;
    u8 led_blink_reg  = 0xa4;
    int i;
    int j;
    int led_status[5][4] = {{0},{0}};
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
#ifdef LED_L3_CTRL_WANTED
    led_3_status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3); //to get register 0x33 0xa3
    led_3_blink  = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
#endif /*LED_L3_CTRL_WANTED*/
    led_4_status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3);
    led_4_blink  = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
    led_5_status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa5);
    led_5_blink  = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa6);
#ifdef LED_L3_CTRL_WANTED
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_get led_3_status   = %x\n", led_3_status));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_get led_3_blink    = %x\n", led_3_blink));
#endif /*LED_L3_CTRL_WANTED*/
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_get led_4_status   = %x\n", led_4_status));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_get led_4_blink    = %x\n", led_4_blink));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_get led_5_status   = %x\n", led_5_status));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_get led_5_blink    = %x\n", led_5_blink));
    sprintf(buf, "");
    if (attr->index == SWITCH_LED)
    {
#ifdef LED_L3_CTRL_WANTED
        for(i = 3; i<= 5; i++)
#else
        for(i = 4; i<= 5; i++)
#endif /*LED_L3_CTRL_WANTED*/
        {
            a_shift = 0x1;
            g_shift = 0x2;
            b_shift = 0x1;
            for(j = 1; j<= 4; j++)
            {
                if (i2c_smbus_read_byte_data(ESC_600_128q_client, led_status_reg) & a_shift)
                {
                    if(i2c_smbus_read_byte_data(ESC_600_128q_client, led_blink_reg) & b_shift)
                    {
                        led_status[i][j] = SWITCH_LED_A_B;
                        sprintf(buf, "%sSwitch LED %d-%d is set to amber and blink\n", buf, i, j);
                    }
                    else
                    {
                        led_status[i][j] = SWITCH_LED_A_N;
                        sprintf(buf, "%sSwitch LED %d-%d is set to amber\n", buf, i, j);
                    }
                }
                else if (i2c_smbus_read_byte_data(ESC_600_128q_client, led_status_reg) & g_shift)
                {
                    if(i2c_smbus_read_byte_data(ESC_600_128q_client, led_blink_reg) & b_shift)
                    {
                        led_status[i][j] = SWITCH_LED_G_B;
                        sprintf(buf, "%sSwitch LED %d-%d is set to green and blink\n", buf, i, j);
                    }
                    else
                    {
                        led_status[i][j] = SWITCH_LED_G_N;
                        sprintf(buf, "%sSwitch LED %d-%d is set to green\n", buf, i, j);
                    }
                }
                else
                {
                    led_status[i][j] = SWITCH_LED_OFF;
                    sprintf(buf, "%sSwitch LED %d-%d is set OFF\n", buf, i, j);
                }
                a_shift = a_shift<< 2;
                g_shift = g_shift<< 2;
                b_shift = b_shift<< 1;
            }
            led_status_reg = led_status_reg + 0x2;
            led_blink_reg  = led_blink_reg  + 0x2;
        }
        
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_led_all_set                                   */
/*    Description        : This is the function to set all switch LED status    */
/*                         0x33 0xa3 ~ 0xa8                                     */
/*    Input(s)           : 0 ~ 4.                                               */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t switch_led_all_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 led_value  = -EPERM;
    u8 blink_value  = -EPERM;
#ifdef LED_L3_CTRL_WANTED
    u8 led_3_status = 0;
    u8 led_3_blink  = 0;
#endif /*LED_L3_CTRL_WANTED*/
    u8 led_4_status = 0;
    u8 led_4_blink  = 0;
    u8 led_5_status = 0;
    u8 led_5_blink  = 0;
    u8 result  = 0;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);
    
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set lock\n"));
#ifdef LED_L3_CTRL_WANTED
    led_3_status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3); //to get register 0x33 0xa3
    led_3_blink  = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
#endif /*LED_L3_CTRL_WANTED*/
    led_4_status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3);
    led_4_blink  = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
    led_5_status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa5);
    led_5_blink  = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa6);
#ifdef LED_L3_CTRL_WANTED
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set led_3_status   = %x\n", led_3_status));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set led_3_blink    = %x\n", led_3_blink));
#endif /*LED_L3_CTRL_WANTED*/
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set led_4_status   = %x\n", led_4_status));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set led_4_blink    = %x\n", led_4_blink));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set led_5_status   = %x\n", led_5_status));
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set led_5_blink    = %x\n", led_5_blink));
    if (attr->index == SWITCH_LED)
    {
        i = simple_strtol(buf, NULL, 10);
        switch(i)
        {
            case SWITCH_LED_OFF:
                led_value = 0x0;
                blink_value = 0x0;
                break;
            case SWITCH_LED_A_N:
                led_value = 0x55;
                blink_value = 0x0;
                break;
            case SWITCH_LED_A_B:
                led_value = 0x55;
                blink_value = 0xf;
                break;
            case SWITCH_LED_G_N:
                led_value = 0xaa;
                blink_value = 0x0;
                break;
            case SWITCH_LED_G_B:
                led_value = 0xaa;
                blink_value = 0xf;
                break;
            default:
                printk(KERN_ALERT "switch_led_all_set set wrong Value\n");
        }
        debug_print((KERN_DEBUG "DEBUG : switch_led_all_set led_value = %x\n",led_value));
        debug_print((KERN_DEBUG "DEBUG : switch_led_all_set blink_value = %x\n",blink_value));
#ifdef LED_L3_CTRL_WANTED
        result  = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa3, led_value);
#endif /*LED_L3_CTRL_WANTED*/
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa3, led_value);
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa5, led_value);
#ifdef LED_L3_CTRL_WANTED
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa4, blink_value);
#endif /*LED_L3_CTRL_WANTED*/
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa4, blink_value);
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa6, blink_value);
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: switch_led_all_set OFF FAILED!\n");
        }
        else
        {
            debug_print((KERN_DEBUG "Switch LED ALL set %d \n", i));
        }
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_all_set unlock\n"));
    return count;
}
#ifdef LED_L3_CTRL_WANTED
/********************************************************************************/
/*    Function Name      : switch_led_3_get                                     */
/*    Description        : This is the function to get switch LED 3 status      */
/*                         0x33 0xa3 0xa4                                       */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_led_3_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    int led_a_status = 0;
    int led_g_status = 0;
    int led_b_status = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3); //to get register 0x33 0xa3
    debug_print((KERN_DEBUG "DEBUG : switch_led_3_get status = %x\n",status));
    sprintf(buf, "");
    for (i = 1; i <= 8; i++)
    {
        if ( i == attr->index)
        {
            if (status & res)
            {
                led_a_status = TURN_ON;
            }
            else
            {
                led_a_status = TURN_OFF;
            }
        }
        res = res << 1;
        if( i == (attr->index + 1) )
        {
            if (status & res)
            {
                led_g_status = TURN_ON;
            }
            else
            {
                led_g_status = TURN_OFF;
            }
        }
        res = res << 1;
    }
    res = 0x1;
    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
    debug_print((KERN_DEBUG "DEBUG : switch_led_3_get status = %x\n",status));
    for (i = 1; i <= 4; i++)
    {
        if ( i == attr->index)
        {
            if (status & res)
            {
                led_b_status = TURN_ON;
            }
            else
            {
                led_b_status = TURN_OFF;
            }
        }
        res = res << 1;
    }
    
    if(led_a_status == TURN_ON && led_b_status == TURN_ON)
    {
        sprintf(buf, "%sSwitch LED 3-%d is set to amber and blink\n", buf, attr->index);
    }
    else if(led_a_status == TURN_ON && led_b_status == TURN_OFF)
    {
        sprintf(buf, "%sSwitch LED 3-%d is set to amber\n", buf, attr->index);
    }
    else if(led_g_status == TURN_ON && led_b_status == TURN_ON)
    {
        sprintf(buf, "%sSwitch LED 3-%d is set to green and blink\n", buf, attr->index);
    }
    else if(led_g_status == TURN_ON && led_b_status == TURN_OFF)
    {
        sprintf(buf, "%sSwitch LED 3-%d is set to green\n", buf, attr->index);
    }
    else
    {
        sprintf(buf, "%sSwitch LED 3-%d is set OFF\n", buf, attr->index);
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_led_3_set                                     */
/*    Description        : This is the function to set switch LED 3 status      */
/*                         0x33 0xa3 0xa4                                       */
/*    Input(s)           : 0 ~ 4.                                               */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t switch_led_3_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 led_value  = -EPERM;
    u8 blk_value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);
    
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_3_set lock\n"));
    led_value = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3); //to get register 0x33 0xa3
    debug_print((KERN_DEBUG "DEBUG : switch_led_3_set led_value = %x\n",led_value));
    blk_value = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
    debug_print((KERN_DEBUG "DEBUG : switch_led_3_set blk_value = %x\n",blk_value));
    if (attr->index != 0)
    {
        i = simple_strtol(buf, NULL, 10);
        debug_print((KERN_DEBUG "DEBUG : switch_led_3_set value = %d\n",i));
        switch(i)
        {
            case SWITCH_LED_OFF:
                led_value   &= ~(1 << ((attr->index)-1));
                led_value   &= ~(1 << (attr->index));
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_A_N:
                led_value   |= (1 << ((attr->index)-1));
                led_value   &= ~(1 << (attr->index));
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_A_B:
                led_value   |= (1 << ((attr->index)-1));
                led_value   &= ~(1 << (attr->index));
                blk_value   |= (1 << ((attr->index)-1));
                break;
            case SWITCH_LED_G_N:
                led_value   |= (1 << (attr->index));
                led_value   &= ~(1 << ((attr->index)-1));
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_G_B:
                led_value   |= (1 << (attr->index));
                led_value   &= ~(1 << ((attr->index)-1));
                blk_value   |= (1 << ((attr->index)-1));
                break;
            default:
                printk(KERN_ALERT "Switch LED set wrong Value\n");
        }
        debug_print((KERN_DEBUG "DEBUG : switch_led_3_set led_value = %x\n",led_value));
        debug_print((KERN_DEBUG "DEBUG : switch_led_3_set blk_value = %x\n",blk_value));
        result  = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa3, led_value);
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa4, blk_value);
        debug_print((KERN_DEBUG "DEBUG : switch_led_3_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: switch_led_3_set SYS_LED_OFF FAILED!\n");
        }
        else
        {
            debug_print((KERN_DEBUG "Switch LED is set Success\n"));
        }
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_3_set unlock\n"));
    return count;
}
#endif /*LED_L3_CTRL_WANTED*/

/********************************************************************************/
/*    Function Name      : switch_led_4_get                                     */
/*    Description        : This is the function to get switch LED 4 status      */
/*                         0x33 0xa5 0xa6                                       */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_led_4_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    int led_a_status = 0;
    int led_g_status = 0;
    int led_b_status = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3); //to get register 0x33 0xa5
    debug_print((KERN_DEBUG "DEBUG : switch_led_4_get status = %x\n",status));
    sprintf(buf, "");
    for (i = 1; i <= 4; i++)
    {
        if ( i == attr->index)
        {
            if (status & res)
            {
                led_a_status = TURN_ON;
            }
            else
            {
                led_a_status = TURN_OFF;
            }
        }
        res = res << 1;
        if( i == (attr->index + 1) )
        {
            if (status & res)
            {
                led_g_status = TURN_ON;
            }
            else
            {
                led_g_status = TURN_OFF;
            }
        }
        res = res << 1;
    }
    res = 0x1;

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
    debug_print((KERN_DEBUG "DEBUG : switch_led_4_get status = %x\n",status));
    for (i = 1; i <= 4; i++)
    {
        if ( i == attr->index)
        {
            if (status & res)
            {
                led_b_status = TURN_ON;
            }
            else
            {
                led_b_status = TURN_OFF;
            }
        }
        res = res << 1;
    }
    
    if(led_a_status == TURN_ON && led_b_status == TURN_ON)
    {
        sprintf(buf, "%sSwitch LED 4-%d is set to amber and blink\n", buf, attr->index);
    }
    else if(led_a_status == TURN_ON && led_b_status == TURN_OFF)
    {
        sprintf(buf, "%sSwitch LED 4-%d is set to amber\n", buf, attr->index);
    }
    else if(led_g_status == TURN_ON && led_b_status == TURN_ON)
    {
        sprintf(buf, "%sSwitch LED 4-%d is set to green and blink\n", buf, attr->index);
    }
    else if(led_g_status == TURN_ON && led_b_status == TURN_OFF)
    {
        sprintf(buf, "%sSwitch LED 4-%d is set to green\n", buf, attr->index);
    }
    else
    {
        sprintf(buf, "%sSwitch LED 4-%d is set OFF\n", buf, attr->index);
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_led_4_set                                     */
/*    Description        : This is the function to set switch LED 4 status      */
/*                         0x33 0xa5 0xa6                                       */
/*    Input(s)           : 0 ~ 4.                                               */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t switch_led_4_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 led_value  = -EPERM;
    u8 blk_value  = -EPERM;
    u8 result = -EPERM;
    u8 offset = 0;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);
    
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_4_set lock\n"));
    led_value = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa3); //to get register 0x33 0xa5
    debug_print((KERN_DEBUG "DEBUG : switch_led_4_set led_value = %x\n",led_value));
    blk_value = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa4);
    debug_print((KERN_DEBUG "DEBUG : switch_led_4_set blk_value = %x\n",blk_value));
    if (attr->index != 0)
    {
        i = simple_strtol(buf, NULL, 10);
        debug_print((KERN_DEBUG "DEBUG : switch_led_4_set value = %d\n",i));
        debug_print((KERN_DEBUG "DEBUG : switch_led_4_set led 4-%d\n",attr->index));
        if(attr->index == 1)
        {
            offset = 0;
        }
        else
        {
            offset = 2*((attr->index)-1);
        }
        switch(i)
        {
            case SWITCH_LED_OFF: //i=0
                led_value   &= ~(0x03 << offset);
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_A_N: //i=1
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x01 << offset);
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_A_B: //i=2
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x01 << offset);
                blk_value   |= (1 << ((attr->index)-1));
                break;
            case SWITCH_LED_G_N: //i=3
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x02 << offset);
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_G_B: //i=4
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x02 << offset);
                blk_value   |= (1 << ((attr->index)-1));
                break;
            default:
                printk(KERN_ALERT "Switch LED set wrong Value\n");
        }
        debug_print((KERN_DEBUG "DEBUG : switch_led_4_set led_value = %x\n",led_value));
        debug_print((KERN_DEBUG "DEBUG : switch_led_4_set blk_value = %x\n",blk_value));
        result  = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa3, led_value);
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa4, blk_value);
        debug_print((KERN_DEBUG "DEBUG : switch_led_4_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: switch_led_4_set SYS_LED_OFF FAILED!\n");
        }
        else
        {
            debug_print((KERN_DEBUG "Switch LED is set Success\n"));
        }
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_4_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : switch_led_5_get                                     */
/*    Description        : This is the function to get switch LED 5 status      */
/*                         0x33 0xa7 0xa8                                       */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t switch_led_5_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x1;
    int i;
    int led_a_status = 0;
    int led_g_status = 0;
    int led_b_status = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa5); //to get register 0x33 0xa5
    debug_print((KERN_DEBUG "DEBUG : switch_led_5_get status = %x\n",status));
    sprintf(buf, "");
    for (i = 1; i <= 8; i++)
    {
        if ( i == attr->index)
        {
            if (status & res)
            {
                led_a_status = TURN_ON;
            }
            else
            {
                led_a_status = TURN_OFF;
            }
        }
        res = res << 1;
        if( i == (attr->index + 1) )
        {
            if (status & res)
            {
                led_g_status = TURN_ON;
            }
            else
            {
                led_g_status = TURN_OFF;
            }
        }
        res = res << 1;
    }
    res = 0x1;
    
    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa6);
    debug_print((KERN_DEBUG "DEBUG : switch_led_5_get status = %x\n",status));
    for (i = 1; i <= 4; i++)
    {
        if ( i == attr->index)
        {
            if (status & res)
            {
                led_b_status = TURN_ON;
            }
            else
            {
                led_b_status = TURN_OFF;
            }
        }
        res = res << 1;
    }
    
    if(led_a_status == TURN_ON && led_b_status == TURN_ON)
    {
        sprintf(buf, "%sSwitch LED 5-%d is set to amber and blink\n", buf, attr->index);
    }
    else if(led_a_status == TURN_ON && led_b_status == TURN_OFF)
    {
        sprintf(buf, "%sSwitch LED 5-%d is set to amber\n", buf, attr->index);
    }
    else if(led_g_status == TURN_ON && led_b_status == TURN_ON)
    {
        sprintf(buf, "%sSwitch LED 5-%d is set to green and blink\n", buf, attr->index);
    }
    else if(led_g_status == TURN_ON && led_b_status == TURN_OFF)
    {
        sprintf(buf, "%sSwitch LED 5-%d is set to green\n", buf, attr->index);
    }
    else
    {
        sprintf(buf, "%sSwitch LED 5-%d is set OFF\n", buf, attr->index);
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : switch_led_5_set                                     */
/*    Description        : This is the function to set switch LED 5 status      */
/*                         0x33 0xa7 0xa8                                       */
/*    Input(s)           : 0 ~ 4.                                               */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t switch_led_5_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 led_value  = -EPERM;
    u8 blk_value  = -EPERM;
    u8 result = -EPERM;
    u8 offset = 0;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);
    
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_5_set lock\n"));
    led_value = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa5); //to get register 0x33 0xa5
    debug_print((KERN_DEBUG "DEBUG : switch_led_5_set led_value = %x\n",led_value));
    blk_value = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xa6);
    debug_print((KERN_DEBUG "DEBUG : switch_led_5_set blk_value = %x\n",blk_value));
    if (attr->index != 0)
    {
        i = simple_strtol(buf, NULL, 10);
        debug_print((KERN_DEBUG "DEBUG : switch_led_5_set value = %d\n",i));
        debug_print((KERN_DEBUG "DEBUG : switch_led_5_set led 5-%d\n",attr->index));
        if(attr->index == 1)
        {
            offset = 0;
        }
        else
        {
            offset = 2*((attr->index)-1);
        }
        switch(i)
        {
            case SWITCH_LED_OFF: //i=0
                led_value   &= ~(0x03 << offset);
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_A_N: //i=1
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x01 << offset);
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_A_B: //i=2
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x01 << offset);
                blk_value   |= (1 << ((attr->index)-1));
                break;
            case SWITCH_LED_G_N: //i=3
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x02 << offset);
                blk_value   &= ~(1 << ((attr->index)-1));
                break;
            case SWITCH_LED_G_B: //i=4
                led_value   &= ~(0x03 << offset);
                led_value   |= (0x02 << offset);
                blk_value   |= (1 << ((attr->index)-1));
                break;
            default:
                printk(KERN_ALERT "Switch LED set wrong Value\n");
        }
        debug_print((KERN_DEBUG "DEBUG : switch_led_5_set led_value = %x\n",led_value));
        debug_print((KERN_DEBUG "DEBUG : switch_led_5_set blk_value = %x\n",blk_value));
        result  = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa5, led_value);
        result |= i2c_smbus_write_byte_data(ESC_600_128q_client, 0xa6, blk_value);
        debug_print((KERN_DEBUG "DEBUG : switch_led_5_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: switch_led_5_set SYS_LED_OFF FAILED!\n");
        }
        else
        {
            debug_print((KERN_DEBUG "Switch LED is set Success\n"));
        }
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : switch_led_5_set unlock\n"));
    return count;
}

/********************************************************************************/
/*    Function Name      : sfp_int_get                                          */
/*    Description        : This is the function to get sfp interrupt status     */
/*                         0x33 0xd0                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t sfp_int_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == SFP_INT)
    {
        status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xd0); //to set register 0x33 0xd0
        debug_print((KERN_DEBUG "DEBUG : sfp_int_get status = %x\n",status));
        sprintf(buf, "");
        if (status & 0x2)
        {
            sprintf(buf, "%sInterrupt is triggered by SFP Loss\n", buf);
        }
        else if (status & 0x4)
        {
            sprintf(buf, "%sInterrupt is triggered by SFP ABS\n", buf);
        }
        else
        {
            sprintf(buf, "%sNo interrupt is triggered\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : psu_int_get                                          */
/*    Description        : This is the function to get psu interrupt status     */
/*                         0x33 0xd0                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t psu_int_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == PSU_INT)
    {
        status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xd0); //to set register 0x33 0xd0
        debug_print((KERN_DEBUG "DEBUG : psu_int_get status = %x\n",status));
        sprintf(buf, "");
        if (status & 0x1)
        {
            sprintf(buf, "%sInterrupt is triggered by PSU\n", buf);
        }
        else
        {
            sprintf(buf, "%sNo interrupt is triggered\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}
/********************************************************************************/
/*    Function Name      : int_mask_get                                         */
/*    Description        : This is the function to get interrupt status         */
/*                         0x33 0xd1                                            */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t int_mask_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xd1); //to get register 0x33 0xd1
    debug_print((KERN_DEBUG "DEBUG : int_mask_get status = %x\n",status));
    sprintf(buf, "");
    if (attr->index == 1)
    {

        if (status & 0x1)
        {
            sprintf(buf, "%sPSU interrupt mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sPSU interrupt mask is disabled\n", buf);
        }
    }
    if (attr->index == 2)
    {

        if (status & 0x2)
        {
            sprintf(buf, "%sSFP Loss interrupt mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sSFP Loss interrupt mask is disabled\n", buf);
        }
    }
    if (attr->index == 3)
    {

        if (status & 0x4)
        {
            sprintf(buf, "%sSFP ABS interrupt mask is enabled\n", buf);
        }
        else
        {
            sprintf(buf, "%sSFP ABS interrupt mask is disabled\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : int_mask_set                                         */
/*    Description        : This is the function to set interrupt status         */
/*                         0x33 0xa3 0xa4                                       */
/*    Input(s)           : 1 or 0.                                              */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t int_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 result = 0;
    int i = 0;
    int j = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct Cameo_i2c_data *data = i2c_get_clientdata(ESC_600_128q_client);

    i = attr->index;
    j = simple_strtol(buf, NULL, 10);
    debug_print((KERN_DEBUG "DEBUG : int_mask_set i: %d\n", i));
    debug_print((KERN_DEBUG "DEBUG : int_mask_set j: %d\n", j));
    mutex_lock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : int_mask_set lock\n"));
    
    status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0xd1); //to get register 0x33 0xd1
    debug_print((KERN_DEBUG "DEBUG : int_mask_set status = %x\n",status));
    if( j == TURN_ON)
    {
        status |= (1 << (i-1));
        debug_print((KERN_DEBUG "DEBUG : int_mask_set value = %x\n",status));
        result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xd1, status); //to set register 0x33 0xd1
        debug_print((KERN_DEBUG "DEBUG : int_mask_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: int_mask_set set ON FAILED!\n");
        }
        else
        {
        debug_print((KERN_DEBUG "int_mask_set ON\n"));
        }
    }
    else if( j == TURN_OFF)
    {
        status &= ~(1 << (i-1));
        debug_print((KERN_DEBUG "DEBUG : int_mask_set value = %x\n",status));
        result = i2c_smbus_write_byte_data(ESC_600_128q_client, 0xd1, status); //to set register 0x33 0xd1
        debug_print((KERN_DEBUG "DEBUG : int_mask_set result = %x\n",result));
        if (result < 0)
        {
            printk(KERN_ALERT "ERROR: int_mask_set set OFF FAILED!\n");
        }
        else
        {
            debug_print((KERN_DEBUG "int_mask_set OFF\n"));
        }
    }
    else
    {
        printk(KERN_ALERT " int_mask_set set wrong value\n");
    }
    mutex_unlock(&data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : int_mask_set unlock\n"));
    return count;
}
#ifdef ESC_600_BMC_WANTED
static ssize_t bmc_module_detect(struct device *dev, struct device_attribute *da, char *buf)
{
    u32 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    sprintf(buf, "");
    if(attr->index == BMC_DETECT)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3);
        debug_print((KERN_DEBUG "DEBUG : BMC byte status = 0x%x\n", status));
    }
    if(status == 0x1)
    {
        sprintf(buf, "%sBMC module is present\n", buf);
    }
    else
    {
        sprintf(buf, "%sBMC module is not present\n", buf);
    }
    return sprintf(buf, "%s", buf);
}
static ssize_t themal_temp_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 bmc_present = -EPERM;
    u8 status = -EPERM;
    u8 mask = 0x1;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    sprintf(buf, "");
    if (attr->index == SENSOR_TEMP)
    {
        bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
        if (bmc_present & mask)
        {
            //to get 0x14 0x08 NCT7511 Temp
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x08); 
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (NCT7511)         READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (NCT7511)         is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x09 Left-Bottom:SB
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x09); 
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (Left-Bottom:SB)  READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (Left-Bottom:SB)  is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x10 Center-Top:SB
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x10);
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (Center-Top:SB)   READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (Center-Top:SB)   is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x11 Center:SB
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x11);
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (Center:SB)       READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (Center:SB)       is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x13 Left-Top:CB
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x13);
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (Left-Top:CB)     READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (Left-Top:CB)     is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x14 Center:CB
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x14);
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (Center:CB)       READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (Center:CB)       is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x15 Right-Bottom:CB
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x15);
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (Right-Bottom:CB) READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (Right-Bottom:CB) is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x16 Left-Bottom:CB
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x16);
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (Left-Bottom:CB)  READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (Left-Bottom:CB)  is %d degrees (C)\n", buf, status);
            }
            //to get 0x14 0x17 I/O Board
            status = i2c_smbus_read_byte_data(Cameo_BMC_client, 0x17);
            if(status == 0xff)
            {
                sprintf(buf, "%sSensor (I/O Board)       READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (I/O Board)       is %d degrees (C)\n", buf, status);
            }
        }
        else
        {
            sprintf(buf, "%sBMC Module is not present\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}
static ssize_t module_temp_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 bmc_present = -EPERM;
    u8 up_reg   [9] = {0x00, 0x20, 0x22, 0x24, 0x26, 0x28, 0x2a, 0x2c, 0x2e};
    u8 down_reg [9] = {0x00, 0x21, 0x23, 0x25, 0x27, 0x29, 0x2b, 0x2d, 0x2f};
    u8 status = -EPERM;
    u8 mask = 0x1;
    u8 i = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    sprintf(buf, "");
    
    if(attr->index == MODULE_TEMP)
    {
        bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
        if (bmc_present & mask)
        {
            for(i = 1; i <= 8; i ++)
            {
                //to get Line Card up Temp
                status = i2c_smbus_read_byte_data(Cameo_BMC_client, up_reg[i]); 
                if(status == 0xff)
                {
                    sprintf(buf, "%sLine Card %d up     READ FAILED\n", buf, i);
                }
                else
                {
                    sprintf(buf, "%sLine Card %d up     is %d degrees (C)\n", buf, i, status);
                }
                //to get Line Card down Temp
                status = i2c_smbus_read_byte_data(Cameo_BMC_client, down_reg[i]); 
                if(status == 0xff)
                {
                    sprintf(buf, "%sLine Card %d down   READ FAILED\n", buf, i);
                }
                else
                {
                    sprintf(buf, "%sLine Card %d down   is %d degrees (C)\n", buf, i, status);
                }
            }
        }
        else
        {
            sprintf(buf, "%sBMC Module is not present\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}
static ssize_t mac_temp_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 bmc_present = -EPERM;
    u16 status = -EPERM;
    u8 mask = 0x1;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    sprintf(buf, "");
    if (attr->index == MAC_TEMP)
    {
        bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
        if (bmc_present & mask)
        {
            //to get MAC Temp 0x14 0x12
            status = i2c_smbus_read_word_data(Cameo_BMC_client, 0x12); 
            if(status == 0xffff)
            {
                sprintf(buf, "%sSensor (MAC MCP3425)     READ FAILED\n", buf);
            }
            else
            {
                sprintf(buf, "%sSensor (MAC MCP3425)     is 0x%x\n", buf, status);
            }
        }
        else
        {
            sprintf(buf, "%sBMC Module is not present\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}

static int two_complement_to_int(u16 data, u8 valid_bit, int mask)
{
    u16  valid_data  = data & mask;
    bool is_negative = valid_data >> (valid_bit - 1);

    return is_negative ? (-(((~valid_data) & mask) + 1)) : valid_data;
}

static ssize_t psu_module_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 bmc_present = -EPERM;
    u8 module_num = 0;
    u8 psu_table [5][11] = 
    {
        {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
        {0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xd8},
        {0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf, 0xc0, 0xc1, 0xc2, 0xc3, 0xd9},
        {0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xcb, 0xcc, 0xcd, 0xda},
        {0xce, 0xcf, 0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xdb},
    };
    u32 psu_status [11] = {0}; 
    u8 mask = 0x1;
    u8 i = 0;
    u16 u16_val = 0;
    int exponent = 0, mantissa = 0;
    int multiplier = 1000;  // lm-sensor uint: mV, mA, mC
    
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    sprintf(buf, "");
    
    bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
    if (bmc_present & mask)
    {
        switch(attr->index)
        {
            case PSU_MODULE_1:
                module_num = 1;
                break;
            case PSU_MODULE_2:
                module_num = 2;
                break;
            case PSU_MODULE_3:
                module_num = 3;
                break;
            case PSU_MODULE_4:
                module_num = 4;
                break;
        }
       
        for(i = 0; i < 10; i ++)
        {
            u16_val = i2c_smbus_read_word_data(Cameo_BMC_client, psu_table[module_num][i]);
            /* word data with linear format */
            if (i != 2 && i != 8) {
                multiplier = 1000;
                if (i == 6 || i == 7) /* pin, pout */
                    multiplier = 1000000;   // lm-sensor unit: uW
                if ( i == 5 ) /* fan_speed */
                    multiplier = 1;
                
                exponent = two_complement_to_int(u16_val >> 11, 5, 0x1f);
                mantissa = two_complement_to_int(u16_val & 0x7ff, 11, 0x7ff);
                psu_status[i] = (exponent >= 0) ? ((mantissa << exponent)*multiplier) : \
                                                  (mantissa*multiplier / (1 << -exponent));
            }
        }
        /* vout mode */
        multiplier = 1000;
        u16_val = i2c_smbus_read_byte_data(Cameo_BMC_client, psu_table[module_num][10]);
        psu_status[10] = u16_val;   
        exponent = two_complement_to_int(u16_val & 0x1f, 5, 0x1f);
        /* vout */
        u16_val = i2c_smbus_read_word_data(Cameo_BMC_client, psu_table[module_num][2]);
        psu_status[2] = (exponent >= 0) ? ((u16_val << exponent)*multiplier) : \
                                          (u16_val*multiplier / (1 << -exponent));

        sprintf(buf, "%sPSU %d VIN          is %d\n", buf, module_num, psu_status[0]);
        sprintf(buf, "%sPSU %d IIN          is %d\n", buf, module_num, psu_status[1]);
        sprintf(buf, "%sPSU %d VOUT         is %d\n", buf, module_num, psu_status[2]);
        sprintf(buf, "%sPSU %d IOUT         is %d\n", buf, module_num, psu_status[3]);
        sprintf(buf, "%sPSU %d TEMP_1       is %d\n", buf, module_num, psu_status[4]);
        sprintf(buf, "%sPSU %d FAN_SPEED    is %d\n", buf, module_num, psu_status[5]);
        sprintf(buf, "%sPSU %d POUT         is %d\n", buf, module_num, psu_status[6]);
        sprintf(buf, "%sPSU %d PIN          is %d\n", buf, module_num, psu_status[7]);
        sprintf(buf, "%sPSU %d MFR_MODEL    is %d\n", buf, module_num, psu_status[8]);
        sprintf(buf, "%sPSU %d MFR_IOUT_MAX is %d\n", buf, module_num, psu_status[9]);
        sprintf(buf, "%sPSU %d VMODE        is %d\n", buf, module_num, psu_status[10]);
    }
    else
    {
        sprintf(buf, "%sBMC Module is not present\n", buf);
    }
    return sprintf(buf, "%s", buf);
}
static ssize_t dc_chip_switch_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 bmc_present = -EPERM;
    u8 dc_table [8] = {0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f};
    u16 dc_status [8] = {0}; 
    u8 mask = 0x1;
    u8 i = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    sprintf(buf, "");
    if (attr->index == DC_CHIP_SWITCH)
    {
        bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
        if (bmc_present & mask)
        {
            for(i = 0; i < 8; i ++)
            {
                dc_status[i] = i2c_smbus_read_word_data(Cameo_BMC_client, dc_table[i]);
            }
            sprintf(buf, "%sTPS40425 0x6e 0x88  is 0x%x\n", buf, dc_status[0]);
            sprintf(buf, "%sTPS40425 0x6e 0x8c  is 0x%x\n", buf, dc_status[1]);
            sprintf(buf, "%sTPS40425 0x6e 0x96  is 0x%x\n", buf, dc_status[2]);
            sprintf(buf, "%sTPS40425 0x70 0x88  is 0x%x\n", buf, dc_status[3]);
            sprintf(buf, "%sTPS40425 0x70 0x8c  is 0x%x\n", buf, dc_status[4]);
            sprintf(buf, "%sTPS40425 0x70 0x96  is 0x%x\n", buf, dc_status[5]);
            /*0x04 TBD*/
            sprintf(buf, "%sISP1014A 0x04 0x00  is 0x%x\n", buf, dc_status[6]);
            sprintf(buf, "%sISP1014A 0x04 0x00  is 0x%x\n", buf, dc_status[7]);
        }
        else
        {
            sprintf(buf, "%sBMC Module is not present\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}
static ssize_t dc_chip_slot_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 bmc_present = -EPERM;
    u8 module_num = 0;
    u8 dc_table [9][10] = 
    {
        {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
        {0x30, 0x31, 0x33, 0x34, 0x36, 0x37, 0x38, 0x39, 0x3b, 0x3c},
        {0x40, 0x41, 0x43, 0x44, 0x46, 0x47, 0x48, 0x49, 0x4b, 0x4c},
        {0x50, 0x51, 0x53, 0x54, 0x56, 0x57, 0x58, 0x59, 0x5b, 0x5c},
        {0x60, 0x61, 0x63, 0x64, 0x66, 0x67, 0x68, 0x69, 0x6b, 0x6c},
        {0x70, 0x71, 0x73, 0x74, 0x76, 0x77, 0x78, 0x79, 0x7b, 0x7c},
        {0x80, 0x81, 0x83, 0x84, 0x86, 0x87, 0x88, 0x89, 0x8b, 0x8c},
        {0x90, 0x91, 0x93, 0x94, 0x96, 0x97, 0x98, 0x99, 0x9b, 0x9c},
        {0xa0, 0xa1, 0xa3, 0xa4, 0xa6, 0xa7, 0xa8, 0xa9, 0xab, 0xac},
    };
    u16 dc_status [10] = {0}; 
    u8 mask = 0x1;
    u8 i = 0;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    sprintf(buf, "");
    bmc_present = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa3); //to get 0x31 0xa3
    if (bmc_present & mask)
    {
        switch(attr->index)
        {
            case DC_CHIP_SLOT_1:
                module_num = 1;
                break;
            case DC_CHIP_SLOT_2:
                module_num = 2;
                break;
            case DC_CHIP_SLOT_3:
                module_num = 3;
                break;
            case DC_CHIP_SLOT_4:
                module_num = 4;
                break;
            case DC_CHIP_SLOT_5:
                module_num = 5;
                break;
            case DC_CHIP_SLOT_6:
                module_num = 6;
                break;
            case DC_CHIP_SLOT_7:
                module_num = 7;
                break;
            case DC_CHIP_SLOT_8:
                module_num = 8;
                break;
        }
        for(i = 0; i < 10; i ++)
        {
            dc_status[i] = i2c_smbus_read_word_data(Cameo_BMC_client, dc_table[module_num][i]);
        }
        sprintf(buf, "%sLine Card %d Chip 1 P0_VOUT is 0x%x\n", buf, module_num, dc_status[0]);
        sprintf(buf, "%sLine Card %d Chip 1 P0_IOUT is 0x%x\n", buf, module_num, dc_status[1]);
        sprintf(buf, "%sLine Card %d Chip 1 P1_VOUT is 0x%x\n", buf, module_num, dc_status[2]);
        sprintf(buf, "%sLine Card %d Chip 1 P1_IOUT is 0x%x\n", buf, module_num, dc_status[3]);
        sprintf(buf, "%sLine Card %d Chip 2 P0_VOUT is 0x%x\n", buf, module_num, dc_status[4]);
        sprintf(buf, "%sLine Card %d Chip 2 P0_IOUT is 0x%x\n", buf, module_num, dc_status[5]);
        sprintf(buf, "%sLine Card %d Chip 3 P0_VOUT is 0x%x\n", buf, module_num, dc_status[6]);
        sprintf(buf, "%sLine Card %d Chip 3 P0_IOUT is 0x%x\n", buf, module_num, dc_status[7]);
        sprintf(buf, "%sLine Card %d Chip 3 P1_VOUT is 0x%x\n", buf, module_num, dc_status[8]);
        sprintf(buf, "%sLine Card %d Chip 3 P1_IOUT is 0x%x\n", buf, module_num, dc_status[9]);
    }
    else
    {
        sprintf(buf, "%sBMC Module is not present\n", buf);
    }
    return sprintf(buf, "%s", buf);
}
#endif /*ESC_600_BMC_WANTED*/
/********************************************************************************/
/*    Function Name      : jtag_select_get                                      */
/*    Description        : This is the function to get JTAG Reg 0x31 0xa1 0xa2  */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : String.                                              */
/********************************************************************************/
static ssize_t jtag_select_get(struct device *dev, struct device_attribute *da, char *buf)
{
    sprintf(buf, "");
    /*TBD*/
    return sprintf(buf, "%s", buf);
}

/********************************************************************************/
/*    Function Name      : jtag_select_set                                      */
/*    Description        : This is the function to set JTAG Reg 0x31 0xa1 0xa2  */
/*    Input(s)           : Jtag number.                                         */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static ssize_t jtag_select_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    /*TBD*/
    return count;
}

static ssize_t cpld_version_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);

    sprintf(buf, "");
    if(attr->index == CPLD_VER)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_2_client, 0x20);
        sprintf(buf, "%s0x30 CPLD version is 0x%x\n", buf, status);
        status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0x20);
        sprintf(buf, "%s0x31 CPLD version is 0x%x\n", buf, status);
        status = i2c_smbus_read_byte_data(ESC_600_128q_client, 0x20);
        sprintf(buf, "%s0x33 CPLD version is 0x%x\n", buf, status);
    }
    return sprintf(buf, "%s", buf);
}

#ifdef EEPROM_WP_WANTED
static ssize_t eeprom_wp_status_get(struct device *dev, struct device_attribute *da, char *buf)
{
    u8 status = -EPERM;
    u8 res = 0x10;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    
    if (attr->index == EEPROM_WP_CTRL)
    {
        status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa0); //to get register 0x30 0xa0
        debug_print((KERN_DEBUG "DEBUG : eeprom_wp status = %x\n",status));
        sprintf(buf, "");
        if (status & res)
        {
            sprintf(buf, "%sEEPROM is Protected\n", buf);
        }
        else
        {
            sprintf(buf, "%sEEPROM is Not Protected\n", buf);
        }
    }
    return sprintf(buf, "%s", buf);
}
static ssize_t eeprom_wp_status_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    u8 status = -EPERM;
    u8 value  = -EPERM;
    u8 result = -EPERM;
    u16 i;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
	struct Cameo_i2c_data *CPLD_3_data = i2c_get_clientdata(Cameo_CPLD_3_client);
    
    mutex_lock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : eeprom_wp_status_set lock\n"));
    status = i2c_smbus_read_byte_data(Cameo_CPLD_3_client, 0xa0); //to get register 0x31 0xa0
    debug_print((KERN_DEBUG "DEBUG : eeprom_wp_status_set status = %x\n",status));
    if (attr->index == EEPROM_WP_CTRL)
    {
        i = simple_strtol(buf, NULL, 10); //get input ON or OFF
        if (i == TURN_ON)
        {
            value = status | 0x10;
            debug_print((KERN_DEBUG "DEBUG : eeprom_wp_status_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xa0, value); //to set register 0x31 0xa0
            debug_print((KERN_DEBUG "DEBUG : eeprom_wp_status_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: usb_ctrl_set ON FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "EEPROM is Protected\n"));
            }
        }
        else if (i == TURN_OFF)
        {
            value = status & 0xef;
            debug_print((KERN_DEBUG "DEBUG : eeprom_wp_status_set value = %x\n",value));
            result = i2c_smbus_write_byte_data(Cameo_CPLD_3_client, 0xa0, value); //to set register 0x31 0xa0
            debug_print((KERN_DEBUG "DEBUG : eeprom_wp_status_set result = %x\n",result));
            if (result < 0)
            {
                printk(KERN_ALERT "ERROR: eeprom_wp_status_set OFF FAILED!\n");
            }
            else
            {
                debug_print((KERN_DEBUG "EEPROM is Not Protected\n"));
            }
        }
        else
        {
            printk(KERN_ALERT "EEPROM set wrong Value\n");
        }
    }
    mutex_unlock(&CPLD_3_data->update_lock);
    debug_print((KERN_DEBUG "DEBUG : usb_power_set unlock\n"));
    return count;
}
#endif /*EEPROM_WP_WANTED*/
/* end of function */
/********************************************************************************/
/*    Function Name      : Cameo_i2c_probe                                      */
/*    Description        : To probe i2c device                                  */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static int Cameo_i2c_probe(struct i2c_client *client, const struct i2c_device_id *dev_id)
{
    struct Cameo_i2c_data *data;
	struct Cameo_i2c_data *CPLD_2_data;
    struct Cameo_i2c_data *CPLD_3_data;
    struct Cameo_i2c_data *CPLD_4_data;
    struct Cameo_i2c_data *Cameo_Extpand_1_data;
    struct Cameo_i2c_data *Cameo_Extpand_2_data;
    struct Cameo_i2c_data *Cameo_BMC_data;

    int status;
    if (!i2c_check_functionality(client->adapter, I2C_FUNC_SMBUS_BYTE_DATA | I2C_FUNC_SMBUS_WORD_DATA))
    {
        status = -EIO;
        goto exit;
    }
    data = kzalloc(sizeof(struct Cameo_i2c_data), GFP_KERNEL);
    if (!data)
    {
        printk(KERN_ALERT "data kzalloc fail\n");
        status = -ENOMEM;
        goto exit;
    }
    CPLD_2_data = kzalloc(sizeof(struct Cameo_i2c_data), GFP_KERNEL);
    if (!CPLD_2_data)
    {
        printk(KERN_ALERT "CPLD_2_data kzalloc fail\n");
        status = -ENOMEM;
        goto exit;
    }
    CPLD_3_data = kzalloc(sizeof(struct Cameo_i2c_data), GFP_KERNEL);
    if (!CPLD_3_data)
    {
        printk(KERN_ALERT "CPLD_3_data kzalloc fail\n");
        status = -ENOMEM;
        goto exit;
    }
    CPLD_4_data = kzalloc(sizeof(struct Cameo_i2c_data), GFP_KERNEL);
    if (!CPLD_4_data)
    {
        printk(KERN_ALERT "CPLD_4_data kzalloc fail\n");
        status = -ENOMEM;
        goto exit;
    }
    Cameo_Extpand_1_data = kzalloc(sizeof(struct Cameo_i2c_data), GFP_KERNEL);
    if (!Cameo_Extpand_1_data)
    {
        printk(KERN_ALERT "Cameo_Extpand_1_data kzalloc fail\n");
        status = -ENOMEM;
        goto exit;
    }
    Cameo_Extpand_2_data = kzalloc(sizeof(struct Cameo_i2c_data), GFP_KERNEL);
    if (!Cameo_Extpand_2_data)
    {
        printk(KERN_ALERT "Cameo_Extpand_2_data kzalloc fail\n");
        status = -ENOMEM;
        goto exit;
    }
    Cameo_BMC_data = kzalloc(sizeof(struct Cameo_i2c_data), GFP_KERNEL);
    if (!Cameo_BMC_data)
    {
        printk(KERN_ALERT "Cameo_BMC_data kzalloc fail\n");
        status = -ENOMEM;
        goto exit;
    }
    i2c_set_clientdata(client                   , data);
    i2c_set_clientdata(Cameo_CPLD_2_client      , CPLD_2_data);
    i2c_set_clientdata(Cameo_CPLD_3_client      , CPLD_3_data);
    i2c_set_clientdata(Cameo_CPLD_4_client      , CPLD_4_data);
    i2c_set_clientdata(Cameo_Extpand_1_client   , Cameo_Extpand_1_data);
    i2c_set_clientdata(Cameo_Extpand_2_client   , Cameo_Extpand_2_data);
    i2c_set_clientdata(Cameo_BMC_client         , Cameo_BMC_data);
    mutex_init(&CPLD_2_data             ->update_lock);
    mutex_init(&CPLD_3_data             ->update_lock);
    mutex_init(&CPLD_4_data             ->update_lock);
    mutex_init(&Cameo_Extpand_1_data    ->update_lock);
    mutex_init(&Cameo_Extpand_2_data    ->update_lock);
    mutex_init(&Cameo_BMC_data          ->update_lock);
    data->valid = 0;
    mutex_init(&data->update_lock);
    dev_info(&client->dev, "chip found\n");
    /* Register sysfs hooks */
    status = sysfs_create_group(&client->dev.kobj, &ESC600_SYS_group);
    if (status)
    {
        goto exit_free;
    }
    status = sysfs_create_group(&client->dev.kobj, &ESC600_PSU_group);
    if (status)
    {
        goto exit_free;
    }
#ifdef ESC_600_JTAG_WANTED
    status = sysfs_create_group(&client->dev.kobj, &ESC600_JTAG_group);
    if (status)
    {
        goto exit_free;
    }
#endif
    status = sysfs_create_group(&client->dev.kobj, &ESC600_SFP_group);
    if (status)
    {
        goto exit_free;
    }
#ifdef ESC_600_MASK_WANTED
    status = sysfs_create_group(&client->dev.kobj, &ESC600_MASK_group);
    if (status)
    {
        goto exit_free;
    }
#endif
    status = sysfs_create_group(&client->dev.kobj, &ESC600_FAN_group);
    if (status)
    {
        goto exit_free;
    }
    status = sysfs_create_group(&client->dev.kobj, &ESC600_USB_group);
    if (status)
    {
        goto exit_free;
    }
    status = sysfs_create_group(&client->dev.kobj, &ESC600_LED_group);
    if (status)
    {
        goto exit_free;
    }
    status = sysfs_create_group(&client->dev.kobj, &ESC600_Reset_group);
    if (status)
    {
        goto exit_free;
    }
    status = sysfs_create_group(&client->dev.kobj, &ESC600_Sensor_group);
    if (status)
    {
        goto exit_free;
    }
#ifdef ESC_600_INT_WANTED
    status = sysfs_create_group(&client->dev.kobj, &ESC600_INT_group);
    if (status)
    {
        goto exit_free;
    }
#endif
    status = sysfs_create_group(&client->dev.kobj, &ESC600_Module_group);
    if (status)
    {
        goto exit_free;
    }
    data->hwmon_dev = hwmon_device_register(&client->dev);
    if (IS_ERR(data->hwmon_dev))
    {
        status = PTR_ERR(data->hwmon_dev);
        goto exit_remove;
    }
    dev_info(&client->dev, "%s: '%s'\n", dev_name(data->hwmon_dev), client->name);
    return 0;
exit_remove:
    sysfs_remove_group(&client->dev.kobj, &ESC600_SYS_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_PSU_group);
#ifdef ESC_600_JTAG_WANTED
    sysfs_remove_group(&client->dev.kobj, &ESC600_JTAG_group);
#endif
    sysfs_remove_group(&client->dev.kobj, &ESC600_SFP_group);
#ifdef ESC_600_MASK_WANTED
    sysfs_remove_group(&client->dev.kobj, &ESC600_MASK_group);
#endif
    sysfs_remove_group(&client->dev.kobj, &ESC600_FAN_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_USB_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_LED_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_Reset_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_Sensor_group);
#ifdef ESC_600_INT_WANTED
    sysfs_remove_group(&client->dev.kobj, &ESC600_INT_group);
#endif
    sysfs_remove_group(&client->dev.kobj, &ESC600_Module_group);
exit_free:
    kfree(data);
exit:
    return status;
}

static int Cameo_i2c_remove(struct i2c_client *client)
{
    struct Cameo_i2c_data *data = i2c_get_clientdata(client);
    hwmon_device_unregister(data->hwmon_dev);
    sysfs_remove_group(&client->dev.kobj, &ESC600_SYS_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_PSU_group);
#ifdef ESC_600_JTAG_WANTED
    sysfs_remove_group(&client->dev.kobj, &ESC600_JTAG_group);
#endif
    sysfs_remove_group(&client->dev.kobj, &ESC600_SFP_group);
#ifdef ESC_600_MASK_WANTED
    sysfs_remove_group(&client->dev.kobj, &ESC600_MASK_group);
#endif
    sysfs_remove_group(&client->dev.kobj, &ESC600_FAN_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_USB_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_LED_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_Reset_group);
    sysfs_remove_group(&client->dev.kobj, &ESC600_Sensor_group);
#ifdef ESC_600_INT_WANTED
    sysfs_remove_group(&client->dev.kobj, &ESC600_INT_group);
#endif
    sysfs_remove_group(&client->dev.kobj, &ESC600_Module_group);
    kfree(data);
    return 0;
}

static const struct i2c_device_id Cameo_i2c_id[] =
{
    { "ESC_600_128q", 0 },
    {},
};
MODULE_DEVICE_TABLE(i2c, Cameo_i2c_id);

static struct i2c_driver Cameo_i2c_driver =
{
    .class        = I2C_CLASS_HWMON,
    .driver =
    {
        .name     = "ESC_600_128q",
    },
    .probe        = Cameo_i2c_probe,
    .remove       = Cameo_i2c_remove,
    .id_table     = Cameo_i2c_id,
    .address_list = normal_i2c,
};

static struct i2c_board_info ESC_600_128q_info[] __initdata =
{
    {
        I2C_BOARD_INFO("ESC_600_128q", 0x33),
        .platform_data = NULL,
    },
};

static struct i2c_board_info Cameo_CPLD_2_info[] __initdata =
{
    {
        I2C_BOARD_INFO("Cameo_CPLD_2", 0x30),
        .platform_data = NULL,
    },
};

static struct i2c_board_info Cameo_CPLD_3_info[] __initdata =
{
    {
        I2C_BOARD_INFO("Cameo_CPLD_3", 0x31),
        .platform_data = NULL,
    },
};

static struct i2c_board_info Cameo_CPLD_4_info[] __initdata =
{
    {
        I2C_BOARD_INFO("Cameo_CPLD_3", 0x35),
        .platform_data = NULL,
    },
};

static struct i2c_board_info Cameo_Extpand_1_info[] __initdata =
{
    {
        I2C_BOARD_INFO("Cameo_Extpand_1", 0x20),
        .platform_data = NULL,
    },
};

static struct i2c_board_info Cameo_Extpand_2_info[] __initdata =
{
    {
        I2C_BOARD_INFO("Cameo_Extpand_2", 0x21),
        .platform_data = NULL,
    },
};

static struct i2c_board_info Cameo_BMC_info[] __initdata =
{
    {
        I2C_BOARD_INFO("Cameo_BMC", 0x14),
        .platform_data = NULL,
    },
};

/********************************************************************************/
/*    Function Name      : Cameo_i2c_init                                       */
/*    Description        : To init i2c driver                                   */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static int __init Cameo_i2c_init(void)
{
    int ret;
    struct i2c_adapter *i2c_adap = i2c_get_adapter(0);
    if (i2c_adap == NULL)
    {
        printk("ERROR: i2c_get_adapter FAILED!\n");
        return -1;
    }
    ESC_600_128q_client         = i2c_new_device(i2c_adap, &ESC_600_128q_info[0]);
    Cameo_CPLD_2_client         = i2c_new_device(i2c_adap, &Cameo_CPLD_2_info[0]);
    Cameo_CPLD_3_client         = i2c_new_device(i2c_adap, &Cameo_CPLD_3_info[0]);
    Cameo_CPLD_4_client         = i2c_new_device(i2c_adap, &Cameo_CPLD_4_info[0]);
    Cameo_Extpand_1_client      = i2c_new_device(i2c_adap, &Cameo_Extpand_1_info[0]);
    Cameo_Extpand_2_client      = i2c_new_device(i2c_adap, &Cameo_Extpand_2_info[0]);
    Cameo_BMC_client            = i2c_new_device(i2c_adap, &Cameo_BMC_info[0]);
    if (ESC_600_128q_info       == NULL ||  Cameo_CPLD_2_info       == NULL ||
        Cameo_CPLD_3_info       == NULL ||  Cameo_Extpand_1_info    == NULL ||
        Cameo_Extpand_2_info    == NULL ||  Cameo_BMC_info          == NULL ||
        Cameo_CPLD_4_info       == NULL)
    {
        printk("ERROR: i2c_new_device FAILED!\n");
        return -1;
    }
    i2c_put_adapter(i2c_adap);
    ret = i2c_add_driver(&Cameo_i2c_driver);
    printk(KERN_ALERT "ESC600-128Q i2c Driver ret: %d\n", ret);
    printk(KERN_ALERT "ESC600-128Q i2c Driver Version: %s\n", DRIVER_VERSION);
    printk(KERN_ALERT "ESC600-128Q i2c Driver INSTALL SUCCESS\n");
    return ret;
}

/********************************************************************************/
/*    Function Name      : Cameo_i2c_exit                                       */
/*    Description        : To remove i2c driver                                 */
/*                                                                              */
/*    Input(s)           : None.                                                */
/*    Output(s)          : None.                                                */
/*    Returns            : None.                                                */
/********************************************************************************/
static void __exit Cameo_i2c_exit(void)
{
    i2c_unregister_device(ESC_600_128q_client);
    i2c_unregister_device(Cameo_CPLD_2_client);
    i2c_unregister_device(Cameo_CPLD_3_client);
    i2c_unregister_device(Cameo_CPLD_4_client);
    i2c_unregister_device(Cameo_Extpand_1_client);
    i2c_unregister_device(Cameo_Extpand_2_client);
    i2c_unregister_device(Cameo_BMC_client);
    i2c_del_driver(&Cameo_i2c_driver);
    printk(KERN_ALERT "ESC600-128Q i2c driver uninstall success\n");
}

MODULE_AUTHOR("Cameo Inc.");
MODULE_DESCRIPTION("Cameo ESC600-128Q i2c driver");
MODULE_LICENSE("GPL");

module_init(Cameo_i2c_init);
module_exit(Cameo_i2c_exit);