/*
 * optoe.c - A driver to read and write the EEPROM on optical transceivers
 * (SFP, QSFP and similar I2C based devices)
 *
 * Copyright (C) 2014 Cumulus networks Inc.
 * Copyright (C) 2017 Finisar Corp.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Freeoftware Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

/*
 *	Description:
 *	a) Optical transceiver EEPROM read/write transactions are just like
 *		the at24 eeproms managed by the at24.c i2c driver
 *	b) The register/memory layout is up to 256 128 byte pages defined by
 *		a "pages valid" register and switched via a "page select"
 *		register as explained in below diagram.
 *	c) 256 bytes are mapped at a time. 'Lower page 00h' is the first 128
 *	        bytes of address space, and always references the same
 *	        location, independent of the page select register.
 *	        All mapped pages are mapped into the upper 128 bytes
 *	        (offset 128-255) of the i2c address.
 *	d) Devices with one I2C address (eg QSFP) use I2C address 0x50
 *		(A0h in the spec), and map all pages in the upper 128 bytes
 *		of that address.
 *	e) Devices with two I2C addresses (eg SFP) have 256 bytes of data
 *		at I2C address 0x50, and 256 bytes of data at I2C address
 *		0x51 (A2h in the spec).  Page selection and paged access
 *		only apply to this second I2C address (0x51).
 *	e) The address space is presented, by the driver, as a linear
 *	        address space.  For devices with one I2C client at address
 *	        0x50 (eg QSFP), offset 0-127 are in the lower
 *	        half of address 50/A0h/client[0].  Offset 128-255 are in
 *	        page 0, 256-383 are page 1, etc.  More generally, offset
 *	        'n' resides in page (n/128)-1.  ('page -1' is the lower
 *	        half, offset 0-127).
 *	f) For devices with two I2C clients at address 0x50 and 0x51 (eg SFP),
 *		the address space places offset 0-127 in the lower
 *	        half of 50/A0/client[0], offset 128-255 in the upper
 *	        half.  Offset 256-383 is in the lower half of 51/A2/client[1].
 *	        Offset 384-511 is in page 0, in the upper half of 51/A2/...
 *	        Offset 512-639 is in page 1, in the upper half of 51/A2/...
 *	        Offset 'n' is in page (n/128)-3 (for n > 383)
 *
 *	                    One I2c addressed (eg QSFP) Memory Map
 *
 *	                    2-Wire Serial Address: 1010000x
 *
 *	                    Lower Page 00h (128 bytes)
 *	                    =====================
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |Page Select Byte(127)|
 *	                    =====================
 *	                              |
 *	                              |
 *	                              |
 *	                              |
 *	                              V
 *	     ------------------------------------------------------------
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    |                 |                  |                       |
 *	    V                 V                  V                       V
 *	 ------------   --------------      ---------------     --------------
 *	|            | |              |    |               |   |              |
 *	|   Upper    | |     Upper    |    |     Upper     |   |    Upper     |
 *	|  Page 00h  | |    Page 01h  |    |    Page 02h   |   |   Page 03h   |
 *	|            | |   (Optional) |    |   (Optional)  |   |  (Optional   |
 *	|            | |              |    |               |   |   for Cable  |
 *	|            | |              |    |               |   |  Assemblies) |
 *	|    ID      | |     AST      |    |      User     |   |              |
 *	|  Fields    | |    Table     |    |   EEPROM Data |   |              |
 *	|            | |              |    |               |   |              |
 *	|            | |              |    |               |   |              |
 *	|            | |              |    |               |   |              |
 *	 ------------   --------------      ---------------     --------------
 *
 * The SFF 8436 (QSFP) spec only defines the 4 pages described above.
 * In anticipation of future applications and devices, this driver
 * supports access to the full architected range, 256 pages.
 *
 **/
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/delay.h>
#include <linux/mutex.h>
#include <linux/sysfs.h>
#include <linux/jiffies.h>
#include <linux/i2c.h>
#include <linux/types.h>

#define BUS_MIN 11       // according to the cls-i2c-ocores mux 
#define BUS_MAX 44		 // according to the cls-i2c-ocores mux
#define BUS_NUM (BUS_MAX - BUS_MIN + 1)

 /* Optical Module device info */
 static struct i2c_board_info i2c_info[] = {
	 {
		 I2C_BOARD_INFO("optoe1", 0x50),
	 }
 };

struct i2c_adapter *adapter[BUS_NUM];
struct i2c_client *client[BUS_NUM];

static int __init optoe_init(void)
{
	int errno = 0;
	int i = 0, j = 0;
	int busnum = 0;
	
	for( j = 0, i = BUS_MIN; i <= BUS_MAX; i++, j++ ){
		adapter[j] = i2c_get_adapter(i); 
		if (IS_ERR(adapter[j])) {
			errno = PTR_ERR(adapter[j]);
			goto err_put_adapter_and_client;
		}
		
		client[j] = i2c_new_device(adapter[j], i2c_info); 
		if (IS_ERR(client[j])) {
			errno = PTR_ERR(client[j]);
			goto err_put_adapter_and_client;
		}
	}
	return 0;
err_put_adapter_and_client:
	for( j = 0, i = BUS_MIN; i <= BUS_MAX; i++, j++ ){
		if (client[j])
			i2c_unregister_device(client[j]);
		if (adapter[j])
			i2c_put_adapter(adapter[j]); 
	}
	return errno;
}
module_init(optoe_init);

static void __exit optoe_exit(void)
{
	int i = 0, j = 0;

	for( j = 0, i = BUS_MIN; i <= BUS_MAX; i++, j++ ){
		if (client[j])
			i2c_unregister_device(client[j]);
		if (adapter[j])
			i2c_put_adapter(adapter[j]); 
	}
	printk("optoe_exit\n");
}
module_exit(optoe_exit);

MODULE_DESCRIPTION("Device for optical transceiver (SFP, QSFP, ...) EEPROMs");
MODULE_VERSION("2.0.0");
MODULE_AUTHOR("Nicholas <nic@celestica.com>");
MODULE_LICENSE("GPL");
