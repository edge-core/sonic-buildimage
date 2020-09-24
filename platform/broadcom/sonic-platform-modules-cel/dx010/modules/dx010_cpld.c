/*
 * dx010_cpld.c - driver for SeaStone's CPLD
 *
 * Copyright (C) 2017 Celestica Corp.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include <linux/interrupt.h>
#include <linux/module.h>
#include <linux/pci.h>
#include <linux/kernel.h>
#include <linux/stddef.h>
#include <linux/delay.h>
#include <linux/ioport.h>
#include <linux/init.h>
#include <linux/i2c.h>
#include <linux/acpi.h>
#include <linux/io.h>
#include <linux/dmi.h>
#include <linux/slab.h>
#include <linux/wait.h>
#include <linux/err.h>
#include <linux/platform_device.h>
#include <linux/types.h>
#include <uapi/linux/stat.h>

#define DRIVER_NAME "dx010_cpld"

#define CPLD1_VERSION_ADDR 0x100
#define CPLD2_VERSION_ADDR 0x200
#define CPLD3_VERSION_ADDR 0x280
#define CPLD4_VERSION_ADDR 0x300
#define CPLD5_VERSION_ADDR 0x380


#define RESET0108   0x250
#define RESET0910   0x251
#define RESET1118   0x2d0
#define RESET1921   0x2d1
#define RESET2229   0x3d0
#define RESET3032   0x3d1

#define LPMOD0108   0x252
#define LPMOD0910   0x253
#define LPMOD1118   0x2d2
#define LPMOD1921   0x2d3
#define LPMOD2229   0x3d2
#define LPMOD3032   0x3d3

#define ABS0108     0x254
#define ABS0910     0x255
#define ABS1118     0x2d4
#define ABS1921     0x2d5
#define ABS2229     0x3d4
#define ABS3032     0x3d5

#define INT0108     0x256
#define INT0910     0x257
#define INT1118     0x2d6
#define INT1921     0x2d7
#define INT2229     0x3d6
#define INT3032     0x3d7


#define LENGTH_PORT_CPLD        34
#define PORT_BANK1_START        1
#define PORT_BANK1_END          10
#define PORT_BANK2_START        11
#define PORT_BANK2_END          21
#define PORT_BANK3_START        22
#define PORT_BANK3_END          32
#define PORT_SFPP1              33
#define PORT_SFPP2              34


#define CPLD_I2C_CLK_100Khz_BIT    BIT(6)
#define CPLD_I2C_DATA_SZ_MASK      GENMASK(7,4)
#define CPLD_I2C_CMD_SZ_MASK       GENMASK(1,0)
#define CPLD_I2C_ERR               BIT(7)
#define CPLD_I2C_BUSY              BIT(6)
#define CPLD_I2C_RST_BIT           BIT(0)
#define CPLD_I2C_RESET             0
#define CPLD_I2C_UNRESET           1
#define CPLD_I2C_DATA_SZ_MAX       8
#define CPLD_I2C_CMD_SZ_MAX        3


#define CPLD_I2C_BANK1_BASE     0x210
#define CPLD_I2C_BANK2_BASE     0x290
#define CPLD_I2C_BANK3_BASE     0x390

#define I2C_PORT_ID        0x0
#define I2C_OPCODE         0x1
#define I2C_DEV_ADDR       0x2
#define I2C_CMD_BYT0       0x3
#define I2C_SSR            0x6
#define I2C_WRITE_DATA     0x10
#define I2C_READ_DATA      0x20

/*
 * private data to send to I2C core
 */
struct current_xfer {
    u8 addr;
    u8 cmd[CPLD_I2C_CMD_SZ_MAX];
    u8 cmd_len;
    u8 data_len;
    union i2c_smbus_data *data;
};

/*
 * private data of I2C adapter
 * base_addr: Base address of this I2C adapter core.
 * port_id: The port ID, use to mux an i2c core to a font panel port.
 * current_xfer: The struct carry current data setup of current smbus transfer.
 */
struct dx010_i2c_data {
        int base_addr;
        int portid;
        struct current_xfer curr_xfer;
};

struct dx010_cpld_data {
        struct i2c_adapter *i2c_adapter[LENGTH_PORT_CPLD];
        struct mutex       cpld_lock;
        uint16_t           read_addr;
};

struct dx010_cpld_data *cpld_data;

static ssize_t getreg_store(struct device *dev, struct device_attribute *devattr,
                const char *buf, size_t count)
{

    uint16_t addr;
    char *last;

    addr = (uint16_t)strtoul(buf,&last,16);
    if(addr == 0 && buf == last){
        return -EINVAL;
    }
    cpld_data->read_addr = addr;
    return count;
}

static ssize_t getreg_show(struct device *dev, struct device_attribute *attr, char *buf)
{

    int len = 0;
    mutex_lock(&cpld_data->cpld_lock);
    len = sprintf(buf, "0x%2.2x\n",inb(cpld_data->read_addr));
    mutex_unlock(&cpld_data->cpld_lock);
    return len;
}

static ssize_t get_reset(struct device *dev, struct device_attribute *devattr,
                char *buf)
{
        unsigned long reset = 0;

        mutex_lock(&cpld_data->cpld_lock);

        reset =
                (inb(RESET3032) & 0x07) << (24+5) |
                inb(RESET2229) << (24-3)  |
                (inb(RESET1921) & 0x07) << (16 + 2) |
                inb(RESET1118) << (16-6) |
                (inb(RESET0910) & 0x03 ) << 8 |
                inb(RESET0108);

        mutex_unlock(&cpld_data->cpld_lock);

        return sprintf(buf,"0x%8.8lx\n", reset & 0xffffffff);
}

static ssize_t setreg_store(struct device *dev, struct device_attribute *devattr,
                const char *buf, size_t count)
{

    uint16_t addr;
    uint8_t value;
    char *tok;
    char clone[count];
    char *pclone = clone;
    char *last;

    strcpy(clone, buf);

    mutex_lock(&cpld_data->cpld_lock);
    tok = strsep((char**)&pclone, " ");
    if(tok == NULL){
        mutex_unlock(&cpld_data->cpld_lock);
        return -EINVAL;
    }
    addr = (uint16_t)strtoul(tok,&last,16);
    if(addr == 0 && tok == last){
        mutex_unlock(&cpld_data->cpld_lock);
        return -EINVAL;
    }

    tok = strsep((char**)&pclone, " ");
    if(tok == NULL){
        mutex_unlock(&cpld_data->cpld_lock);
        return -EINVAL;
    }
    value = (uint8_t)strtoul(tok,&last,16);
    if(value == 0 && tok == last){
        mutex_unlock(&cpld_data->cpld_lock);
        return -EINVAL;
    }

    outb(value,addr);
    mutex_unlock(&cpld_data->cpld_lock);
    return count;
}

static ssize_t set_reset(struct device *dev, struct device_attribute *devattr,
                const char *buf, size_t count)
{
        unsigned long reset;
        int err;

        mutex_lock(&cpld_data->cpld_lock);

        err = kstrtoul(buf, 16, &reset);
        if (err)
        {
                mutex_unlock(&cpld_data->cpld_lock);
                return err;
        }

        outb( (reset >> 0)  & 0xFF, RESET0108);
        outb( (reset >> 8)  & 0x03, RESET0910);
        outb( (reset >> 10) & 0xFF, RESET1118);
        outb( (reset >> 18) & 0x07, RESET1921);
        outb( (reset >> 21) & 0xFF, RESET2229);
        outb( (reset >> 29) & 0x07, RESET3032);

        mutex_unlock(&cpld_data->cpld_lock);

        return count;
}

static ssize_t get_lpmode(struct device *dev, struct device_attribute *devattr,
                char *buf)
{
        unsigned long lpmod = 0;

        mutex_lock(&cpld_data->cpld_lock);

        lpmod =
                (inb(LPMOD3032) & 0x07) << (24+5) |
                inb(LPMOD2229) << (24-3)  |
                (inb(LPMOD1921) & 0x07) << (16 + 2) |
                inb(LPMOD1118) << (16-6) |
                (inb(LPMOD0910) & 0x03 ) << 8 |
                inb(LPMOD0108);

        mutex_unlock(&cpld_data->cpld_lock);

        return sprintf(buf,"0x%8.8lx\n", lpmod & 0xffffffff);
}

static ssize_t set_lpmode(struct device *dev, struct device_attribute *devattr,
                const char *buf, size_t count)
{
        unsigned long lpmod;
        int err;

        mutex_lock(&cpld_data->cpld_lock);

        err = kstrtoul(buf, 16, &lpmod);
        if (err)
        {
                mutex_unlock(&cpld_data->cpld_lock);
                return err;
        }

        outb( (lpmod >> 0) & 0xFF, LPMOD0108);
        outb( (lpmod >> 8) & 0x03, LPMOD0910);
        outb( (lpmod >> 10) & 0xFF, LPMOD1118);
        outb( (lpmod >> 18) & 0x07, LPMOD1921);
        outb( (lpmod >> 21) & 0xFF, LPMOD2229);
        outb( (lpmod >> 29) & 0x07, LPMOD3032);

        mutex_unlock(&cpld_data->cpld_lock);

        return count;
}

static ssize_t get_modprs(struct device *dev, struct device_attribute *devattr,
                char *buf)
{
        unsigned long present;

        mutex_lock(&cpld_data->cpld_lock);

        present =
                (inb(ABS3032) & 0x07) << (24+5) |
                inb(ABS2229) << (24-3)  |
                (inb(ABS1921) & 0x07) << (16 + 2) |
                inb(ABS1118) << (16-6) |
                (inb(ABS0910) & 0x03) << 8 |
                inb(ABS0108);

        mutex_unlock(&cpld_data->cpld_lock);

        return sprintf(buf,"0x%8.8lx\n", present & 0xffffffff);
}

static ssize_t get_modirq(struct device *dev, struct device_attribute *devattr,
                char *buf)
{
        unsigned long irq;

        mutex_lock(&cpld_data->cpld_lock);

        irq =
                (inb(INT3032) & 0x07) << (24+5) |
                inb(INT2229) << (24-3)  |
                (inb(INT1921) & 0x07) << (16 + 2) |
                inb(INT1118) << (16-6) |
                (inb(INT0910) & 0x03) << 8 |
                inb(INT0108);

        mutex_unlock(&cpld_data->cpld_lock);

        return sprintf(buf,"0x%8.8lx\n", irq  & 0xffffffff);
}

static DEVICE_ATTR_RW(getreg);
static DEVICE_ATTR_WO(setreg);
static DEVICE_ATTR(qsfp_reset, S_IRUGO | S_IWUSR, get_reset, set_reset);
static DEVICE_ATTR(qsfp_lpmode, S_IRUGO | S_IWUSR, get_lpmode, set_lpmode);
static DEVICE_ATTR(qsfp_modprs, S_IRUGO, get_modprs, NULL);
static DEVICE_ATTR(qsfp_modirq, S_IRUGO, get_modirq, NULL);

static struct attribute *dx010_lpc_attrs[] = {
        &dev_attr_getreg.attr,
        &dev_attr_setreg.attr,
        &dev_attr_qsfp_reset.attr,
        &dev_attr_qsfp_lpmode.attr,
        &dev_attr_qsfp_modprs.attr,
        &dev_attr_qsfp_modirq.attr,
        NULL,
};

static struct attribute_group dx010_lpc_attr_grp = {
        .attrs = dx010_lpc_attrs,
};

static struct resource cel_dx010_lpc_resources[] = {
        {
                .flags  = IORESOURCE_IO,
        },
};

static void cel_dx010_lpc_dev_release( struct device * dev)
{
        return;
}

static struct platform_device cel_dx010_lpc_dev = {
        .name           = DRIVER_NAME,
        .id             = -1,
        .num_resources  = ARRAY_SIZE(cel_dx010_lpc_resources),
        .resource       = cel_dx010_lpc_resources,
        .dev = {
                        .release = cel_dx010_lpc_dev_release,
        }
};

// TODO: Refactoring this function with helper functions.
static s32 cpld_smbus_transfer(struct dx010_i2c_data *priv) {

        u8 val;
        s32 error;
        unsigned long ioBase;
        short portid, opcode, devaddr, cmdbyte0, ssr, writedata, readdata;
        union i2c_smbus_data *data;

        error = -EIO;

        mutex_lock(&cpld_data->cpld_lock);

        ioBase = priv->base_addr;
        data = priv->curr_xfer.data;

        portid = ioBase + I2C_PORT_ID;
        opcode = ioBase + I2C_OPCODE;
        devaddr = ioBase + I2C_DEV_ADDR;
        cmdbyte0 = ioBase + I2C_CMD_BYT0;
        ssr = ioBase + I2C_SSR;
        writedata = ioBase + I2C_WRITE_DATA;
        readdata = ioBase + I2C_READ_DATA;

        /* Wait for the core to be free */
        pr_debug("CPLD_I2C Wait busy bit(6) to be cleared\n");
        do {
                val = inb(ssr);
                if ((val & CPLD_I2C_BUSY) == 0)
                        break;
                udelay(100);
        } while (true);  // Risky - add timeout

        /*
         * If any error happen here, we do soft-reset
         * and check the BUSY/ERROR again.
         */
        pr_debug("CPLD_I2C Check error bit(7)\n");
        if (val & CPLD_I2C_ERR) {
                pr_debug("CPLD_I2C Error, try soft-reset\n");
                outb(CPLD_I2C_RESET, ssr);
                udelay(3000);
                outb(CPLD_I2C_UNRESET, ssr);

                val = inb(ssr);
                if (val & (CPLD_I2C_BUSY | CPLD_I2C_ERR)) {
                    pr_debug("CPLD_I2C Error, core busy after reset\n");
                    error = -EIO;
                    goto exit_unlock;
                }
        }

        /* Configure PortID */
        val = priv->portid | CPLD_I2C_CLK_100Khz_BIT;
        outb(val, portid);
        pr_debug("CPLD_I2C Write PortID 0x%x\n", val);

        /* Configure OP_Code */
        val = (priv->curr_xfer.data_len << 4) &  CPLD_I2C_DATA_SZ_MASK;
        val |= (priv->curr_xfer.cmd_len & CPLD_I2C_CMD_SZ_MASK);
        outb(val, opcode);
        pr_debug("CPLD_I2C Write OP_Code 0x%x\n", val);

        /* Configure CMD_Byte */
        outb(priv->curr_xfer.cmd[0], cmdbyte0);
        pr_debug("CPLD_I2C Write CMD_Byte 0x%x\n", priv->curr_xfer.cmd[0]);

        /* Configure write data buffer */
        if ((priv->curr_xfer.addr & BIT(0)) == I2C_SMBUS_WRITE){
                pr_debug("CPLD_I2C Write WR_DATA buffer\n");
                switch(priv->curr_xfer.data_len){
                case 1:
                        outb(data->byte, writedata);
                        break;
                case 2:
                        outb(data->block[0], writedata);
                        outb(data->block[1], ++writedata);
                        break;
                }
        }

        /* Start transfer, write the device address register */
        pr_debug("CPLD_I2C Write DEV_ADDR 0x%x\n", priv->curr_xfer.addr);
        outb(priv->curr_xfer.addr, devaddr);

        /* Wait for transfer finish */
        pr_debug("CPLD_I2C Wait busy bit(6) to be cleared\n");
        do {
                val = inb(ssr);
                if ((val & CPLD_I2C_BUSY) == 0)
                        break;
                udelay(100);
        } while (true); // Risky - add timeout

        pr_debug("CPLD_I2C Check error bit(7)\n");
        if (val & CPLD_I2C_ERR) {
                error = -EIO;
                goto exit_unlock;
        }

        /* Get the data from buffer */
        if ((priv->curr_xfer.addr & BIT(0)) == I2C_SMBUS_READ){
                pr_debug("CPLD_I2C Read RD_DATA buffer\n");
                switch (priv->curr_xfer.data_len) {
                case 1:
                        data->byte = inb(readdata);
                        break;
                case 2:
                        data->block[0] = inb(readdata);
                        data->block[1] = inb(++readdata);
                        break;
                }
        }

        error = 0;

exit_unlock:
        pr_debug("CPLD_I2C Exit with %d\n", error);
        mutex_unlock(&cpld_data->cpld_lock);
        return error;

}

/*
 * dx010_smbus_xfer - execute LPC-SMBus transfer
 * Returns a negative errno code else zero on success.
 */
static s32 dx010_smbus_xfer(struct i2c_adapter *adap, u16 addr,
               unsigned short flags, char read_write,
               u8 command, int size, union i2c_smbus_data *data) {

        int error = 0;
        struct dx010_i2c_data *priv;

        priv = i2c_get_adapdata(adap);

        pr_debug("smbus_xfer called RW:%x CMD:%x SIZE:0x%x",
                 read_write, command, size);

        priv->curr_xfer.addr = (addr << 1) | read_write;
        priv->curr_xfer.data = data;

        /* Map the size to what the chip understands */
        switch (size) {
        case I2C_SMBUS_BYTE:
                priv->curr_xfer.cmd_len = 0;
                priv->curr_xfer.data_len = 1;
                break;
        case I2C_SMBUS_BYTE_DATA:
                priv->curr_xfer.cmd_len = 1;
                priv->curr_xfer.data_len = 1;
                priv->curr_xfer.cmd[0] = command;
                break;
        case I2C_SMBUS_WORD_DATA:
                priv->curr_xfer.cmd_len = 1;
                priv->curr_xfer.data_len = 2;
                priv->curr_xfer.cmd[0] = command;
                break;
        default:
                dev_warn(&adap->dev, "Unsupported transaction %d\n", size);
                error = -EOPNOTSUPP;
                goto Done;
        }

        error = cpld_smbus_transfer(priv);

Done:
        return error;
}

// TODO: Add support for I2C_FUNC_SMBUS_PROC_CALL and I2C_FUNC_SMBUS_I2C_BLOCK
static u32 dx010_i2c_func(struct i2c_adapter *a) {
        return  I2C_FUNC_SMBUS_READ_BYTE  |
                I2C_FUNC_SMBUS_BYTE_DATA  |
                I2C_FUNC_SMBUS_WORD_DATA;
}

static const struct i2c_algorithm dx010_i2c_algorithm = {
        .smbus_xfer = dx010_smbus_xfer,
        .functionality  = dx010_i2c_func,
};

static struct i2c_adapter *cel_dx010_i2c_init(struct platform_device *pdev, int portid)
{
        int error;
        int base_addr;
        struct i2c_adapter *new_adapter;
        struct dx010_i2c_data *priv;

        switch (portid) {
        case PORT_SFPP1 ... PORT_SFPP2:
        case PORT_BANK1_START ... PORT_BANK1_END:
                base_addr = CPLD_I2C_BANK1_BASE;
                break;
        case PORT_BANK2_START ... PORT_BANK2_END:
                base_addr = CPLD_I2C_BANK2_BASE;
                break;
        case PORT_BANK3_START ... PORT_BANK3_END:
                base_addr = CPLD_I2C_BANK3_BASE;
                break;
        default:
                dev_err(&pdev->dev, "Invalid port adapter ID: %d\n", portid);
                goto error_exit;
        }

        new_adapter = kzalloc(sizeof(*new_adapter), GFP_KERNEL);
                if (!new_adapter)
                        return NULL;

        new_adapter->dev.parent = &pdev->dev;
        new_adapter->owner = THIS_MODULE;
        new_adapter->class = I2C_CLASS_DEPRECATED;
        new_adapter->algo  = &dx010_i2c_algorithm;

        snprintf(new_adapter->name, sizeof(new_adapter->name),
                        "SMBus dx010 i2c Adapter port %d", portid);

        priv = kzalloc(sizeof(*priv), GFP_KERNEL);
        if (!priv) {
                goto free_adap;
        }

        priv->portid = portid;
        priv->base_addr = base_addr;

        i2c_set_adapdata(new_adapter, priv);
        error = i2c_add_adapter(new_adapter);
        if(error)
                goto free_data;

        return new_adapter;

free_adap:
        kzfree(new_adapter);
free_data:
        kzfree(priv);
error_exit:
        return NULL;
};

static int cel_dx010_lpc_drv_probe(struct platform_device *pdev)
{
        struct resource *res;
        int ret = 0;
        int portid_count;

        cpld_data = devm_kzalloc(&pdev->dev, sizeof(struct dx010_cpld_data),
                        GFP_KERNEL);
        if (!cpld_data)
                return -ENOMEM;

        mutex_init(&cpld_data->cpld_lock);
        cpld_data->read_addr = CPLD1_VERSION_ADDR;

        res = platform_get_resource(pdev, IORESOURCE_IO, 0);
        if (unlikely(!res)) {
                printk(KERN_ERR " Specified Resource Not Available...\n");
                return -1;
        }

        ret = sysfs_create_group(&pdev->dev.kobj, &dx010_lpc_attr_grp);
        if (ret) {
                printk(KERN_ERR "Cannot create sysfs\n");
        }

        for(portid_count=1 ; portid_count<=LENGTH_PORT_CPLD ; portid_count++)
                cpld_data->i2c_adapter[portid_count-1] =
                                cel_dx010_i2c_init(pdev, portid_count);

        return 0;
}

static int cel_dx010_lpc_drv_remove(struct platform_device *pdev)
{
        int portid_count;

        sysfs_remove_group(&pdev->dev.kobj, &dx010_lpc_attr_grp);

        for (portid_count=1 ; portid_count<=LENGTH_PORT_CPLD ; portid_count++)
                i2c_del_adapter(cpld_data->i2c_adapter[portid_count-1]);

        return 0;
}

static struct platform_driver cel_dx010_lpc_drv = {
        .probe  = cel_dx010_lpc_drv_probe,
        .remove = __exit_p(cel_dx010_lpc_drv_remove),
        .driver = {
        .name   = DRIVER_NAME,
        },
};

int cel_dx010_lpc_init(void)
{
        platform_device_register(&cel_dx010_lpc_dev);
        platform_driver_register(&cel_dx010_lpc_drv);

        return 0;
}

void cel_dx010_lpc_exit(void)
{
        platform_driver_unregister(&cel_dx010_lpc_drv);
        platform_device_unregister(&cel_dx010_lpc_dev);
}

module_init(cel_dx010_lpc_init);
module_exit(cel_dx010_lpc_exit);

MODULE_AUTHOR("Abhisit Sangjan  <asang@celestica.com>");
MODULE_AUTHOR("Pariwat Leamsumran  <pleamsum@celestica.com>");
MODULE_DESCRIPTION("Celestica SeaStone DX010 LPC Driver");
MODULE_LICENSE("GPL");