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
 * Description
 *  Platform LED related defines and structures
 */


/*****************************************
 *  kobj list 
 *****************************************/

struct kobject *platform_kobj=NULL;
struct kobject *led_kobj=NULL;

struct kobject *state_attr_kobj=NULL;
struct kobject *cur_state_kobj=NULL;

/*****************************************
 * Static Data provided from user 
 * space JSON data file
 *****************************************/
#define NAME_SIZE 32
#define VALUE_SIZE 5
typedef enum {
    STATUS_LED_COLOR_GREEN,
    STATUS_LED_COLOR_GREEN_BLINK,
    STATUS_LED_COLOR_RED,
    STATUS_LED_COLOR_RED_BLINK,
    STATUS_LED_COLOR_AMBER,
    STATUS_LED_COLOR_AMBER_BLINK,
    STATUS_LED_COLOR_BLUE,
    STATUS_LED_COLOR_BLUE_BLINK,
    STATUS_LED_COLOR_YELLOW,
    STATUS_LED_COLOR_YELLOW_BLINK,
    STATUS_LED_COLOR_OFF,
    MAX_LED_STATUS
}LED_STATUS;

char*  LED_STATUS_STR[] = {
    "green",
    "green_blink",
    "red",
    "red_blink",
    "amber",
    "amber_blink",
    "blue",
    "blue_blink",
    "yellow",
    "yellow_blink",
    "off"
};


typedef struct 
{
    char bits[NAME_SIZE]; 
    int pos; 
    int mask_bits;
}MASK_BITS;

typedef struct
{
    int	swpld_addr;
    int swpld_addr_offset;
    MASK_BITS bits;
    u8	 reg_values[VALUE_SIZE];
    char value[NAME_SIZE];
    char attr_devtype[NAME_SIZE];
    char attr_devname[NAME_SIZE];
} LED_DATA;

typedef struct
{
    int state;
    char color[NAME_SIZE]; 
} CUR_STATE_DATA;

typedef struct
{
    CUR_STATE_DATA cur_state;
    char device_name[NAME_SIZE];
    int index;
    LED_DATA data[MAX_LED_STATUS];
    int	swpld_addr;
    int swpld_addr_offset;
    char attr_devtype[NAME_SIZE];
    char attr_devname[NAME_SIZE];
} LED_OPS_DATA; 

typedef enum{
	LED_SYS,
	LED_PSU,
	LED_FAN,
	LED_FANTRAY,
	LED_DIAG,
	LED_LOC,
	LED_TYPE_MAX
} LED_TYPE;
char* LED_TYPE_STR[LED_TYPE_MAX] = 
{
	"LED_SYS",
	"LED_PSU",
	"LED_FAN",
	"LED_FANTRAY",
	"LED_DIAG",
	"LED_LOC",
};

/*****************************************
 * Data exported from kernel for  
 * user space plugin to get/set
 *****************************************/
#define PDDF_LED_DATA_ATTR( _prefix, _name, _mode, _show, _store, _type, _len, _addr)    \
        struct pddf_data_attribute pddf_dev_##_prefix##_attr_##_name = { .dev_attr = __ATTR(_name, _mode, _show, _store),  \
          .type = _type , \
          .len = _len ,   \
          .addr = _addr }
