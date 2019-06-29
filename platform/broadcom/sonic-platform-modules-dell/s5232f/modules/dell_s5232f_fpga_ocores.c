/*
 * Copyright (C) 2018 Dell Inc
 *
 * Licensed under the GNU General Public License Version 2
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
 */

/**********************************************************************
 * @file fpga_ocores.c
 * @brief This is a driver to interface with Linux Open Cores driver for FPGA i2c access
 *
 ************************************************************************/
#include <linux/kobject.h>
#include <linux/kdev_t.h>
#include <linux/list.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/delay.h>
#include <linux/dma-mapping.h>
#include <linux/delay.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/jiffies.h>
#include <linux/module.h>
#include <linux/pci.h>
#include <linux/uaccess.h>
#include <linux/sched.h>

#include <asm/siginfo.h>    //siginfo
#include <linux/rcupdate.h> //rcu_read_lock
#include <linux/version.h>  //kernel_version
#include <linux/slab.h>
#include <linux/irqdomain.h>
#include <linux/workqueue.h>
#include <linux/i2c.h>
#include <linux/moduleparam.h>


void __iomem * fpga_base_addr = NULL;
void __iomem * fpga_ctl_addr = NULL;

#define DRIVER_NAME       "fpgapci"
#define PCI_NUM_BARS 4

#ifdef DEBUG
# define PRINT(fmt, ...) printk(fmt, ##__VA_ARGS__)
#else
# define PRINT(fmt, ...)
#endif

/* Maximum size of driver buffer (allocated with kalloc()).
 * Needed to copy data from user to kernel space, among other
 * things. */
static const size_t BUF_SIZE = PAGE_SIZE;

/* Device data used by this driver. */
struct fpgapci_dev {
    /* the kernel pci device data structure */
    struct pci_dev *pci_dev;

    /* upstream root node */
    struct pci_dev *upstream;

    /* kernels virtual addr. for the mapped BARs */
    void * __iomem bar[PCI_NUM_BARS];

    /* length of each memory region. Used for error checking. */
    size_t bar_length[PCI_NUM_BARS];

    /* Debug data */
    /* number of hw interrupts handled. */
    int num_handled_interrupts;
    int num_undelivered_signals;
    int pci_gen;
    int pci_num_lanes;

    unsigned int irq_first;
    unsigned int irq_length;
    unsigned int irq_assigned;
    unsigned int xcvr_intr_count;

};

static int use_irq = 1;
module_param(use_irq, int, 0644);
MODULE_PARM_DESC(use_irq, "Get an use_irq value from user...\n");

static uint32_t num_bus = 0;
module_param(num_bus, int, 0);
MODULE_PARM_DESC(num_bus,
        "Number of i2c busses supported by the FPGA on this platform.");


/* Xilinx FPGA PCIE info:                                                    */
/* Non-VGA unclassified device: Xilinx Corporation Device 7021*/
/* Subsystem: Xilinx Corporation Device 0007                       */
//#define VENDOR 0x10EE
#define DEVICE 0x7021
static phys_addr_t fpga_phys_addr;

typedef signed char s8;
typedef unsigned char u8;

typedef signed short s16;
typedef unsigned short u16;

typedef signed int s32;
typedef unsigned int u32;

typedef signed long long s64;
typedef unsigned long long u64;


/* struct to hold data related to the pcie device */
struct pci_data_struct{
    struct pci_dev* dev;
    unsigned long long phy_addr_bar0;
    unsigned long long phy_len_bar0;
    unsigned long long phy_flags_bar0;
    unsigned int irq_first;
    unsigned int irq_length;
    unsigned int irq_assigned;
    void * kvirt_addr_bar0;
};

/* global variable declarations */

/* Static function declarations */
static int fpgapci_probe(struct pci_dev *dev, const struct pci_device_id *id);
static void fpgapci_remove(struct pci_dev *dev);

static int scan_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev);
static int map_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev);
static void free_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev);


struct fpgalogic_i2c {
    void __iomem *base;
    u32 reg_shift;
    u32 reg_io_width;
    wait_queue_head_t wait;
    struct i2c_msg *msg;
    int pos;
    int nmsgs;
    int state; /* see STATE_ */
    int ip_clock_khz;
    int bus_clock_khz;
    void (*reg_set)(struct fpgalogic_i2c *i2c, int reg, u8 value);
    u8 (*reg_get)(struct fpgalogic_i2c *i2c, int reg);
    u32 timeout;
    struct mutex lock;
};
/* registers */
#define FPGAI2C_REG_PRELOW        0
#define FPGAI2C_REG_PREHIGH        1
#define FPGAI2C_REG_CONTROL        2
#define FPGAI2C_REG_DATA            3
#define FPGAI2C_REG_CMD            4 /* write only */
#define FPGAI2C_REG_STATUS        4 /* read only, same address as FPGAI2C_REG_CMD */
#define FPGAI2C_REG_VER            5



#define FPGAI2C_REG_CTRL_IEN        0x40
#define FPGAI2C_REG_CTRL_EN        0x80

#define FPGAI2C_REG_CMD_START        0x91
#define FPGAI2C_REG_CMD_STOP        0x41
#define FPGAI2C_REG_CMD_READ        0x21
#define FPGAI2C_REG_CMD_WRITE        0x11
#define FPGAI2C_REG_CMD_READ_ACK    0x21
#define FPGAI2C_REG_CMD_READ_NACK    0x29
#define FPGAI2C_REG_CMD_IACK        0x01

#define FPGAI2C_REG_STAT_IF        0x01
#define FPGAI2C_REG_STAT_TIP        0x02
#define FPGAI2C_REG_STAT_ARBLOST    0x20
#define FPGAI2C_REG_STAT_BUSY        0x40
#define FPGAI2C_REG_STAT_NACK        0x80

/* SR[7:0] - Status register */
#define FPGAI2C_REG_SR_RXACK    (1 << 7) /* Receive acknowledge from slave ‘1’ = No acknowledge received*/
#define FPGAI2C_REG_SR_BUSY    (1 << 6) /* Busy, I2C bus busy (as defined by start / stop bits) */
#define FPGAI2C_REG_SR_AL        (1 << 5) /* Arbitration lost - fpga i2c logic lost arbitration */
#define FPGAI2C_REG_SR_TIP    (1 << 1) /* Transfer in progress */
#define FPGAI2C_REG_SR_IF        (1 << 0) /* Interrupt flag */

enum {
    STATE_DONE = 0,
    STATE_INIT,
    STATE_ADDR,
    STATE_ADDR10,
    STATE_START,
    STATE_WRITE,
    STATE_READ,
    STATE_ERROR,
};

#define TYPE_FPGALOGIC        0
#define TYPE_GRLIB        1

/*I2C_CH1 Offset address from PCIE BAR 0*/
#define FPGALOGIC_I2C_BASE        0x00006000
#define FPGALOGIC_CH_OFFSET    0x10

#define i2c_bus_controller_numb 1
#define I2C_PCI_MAX_BUS         (16)
#define I2C_PCI_MAX_BUS_REV00   (7)
#define DELL_I2C_CLOCK_LEGACY   0
#define DELL_I2C_CLOCK_PRESERVE (~0U)
#define I2C_PCI_BUS_NUM_5           5
#define I2C_PCI_BUS_NUM_7           7
#define I2C_PCI_BUS_NUM_8           8
#define I2C_PCI_BUS_NUM_10          10
#define I2C_PCI_BUS_NUM_12          12
#define I2C_PCI_BUS_NUM_16          16

#define IRQ_LTCH_STS        		0x20
#define PRSNT_LTCH_STS	        	0x10

#define PORT_CTRL_OFFSET            0x4000
#define PORT_STS_OFFSET             0x4004
#define PORT_IRQ_STS_OFFSET         0x4008
#define PORT_IRQ_EN_OFFSET          0x400C
#define MB_BRD_REV_TYPE             0x0008
#define MB_BRD_REV_MASK             0x00f0
#define MB_BRD_REV_00               0x0000
#define MB_BRD_REV_01               0x0010
#define MB_BRD_REV_02               0x0020
#define MB_BRD_REV_03               0x0030
#define MB_BRD_TYPE_MASK            0x000f
#define BRD_TYPE_Z9232_NON_NEBS     0x0
#define BRD_TYPE_Z9232_NEBS         0x1
#define BRD_TYPE_Z9264_NON_NEBS     0x2
#define BRD_TYPE_Z9264_NEBS         0x3
#define BRD_TYPE_S5212_NON_NEBS     0x4
#define BRD_TYPE_S5212_NEBS         0x5
#define BRD_TYPE_S5224_NON_NEBS     0x6
#define BRD_TYPE_S5224_NEBS         0x7
#define BRD_TYPE_S5248_NON_NEBS     0x8
#define BRD_TYPE_S5248_NEBS         0x9
#define BRD_TYPE_S5296_NON_NEBS     0xa
#define BRD_TYPE_S5296_NEBS         0xb
#define BRD_TYPE_S5232_NON_NEBS     0xc
#define BRD_TYPE_S5232_NEBS         0xd

#define FPGA_CTL_REG_SIZE           0x6000
#define MSI_VECTOR_MAP_MASK         0x1f
#define MSI_VECTOR_MAP1             0x58
#define I2C_CH1_MSI_MAP_VECT_8      0x00000008
#define I2C_CH2_MSI_MAP_VECT_9      0x00000120
#define I2C_CH3_MSI_MAP_VECT_10     0x00002800
#define I2C_CH4_MSI_MAP_VECT_11     0x00058000
#define I2C_CH5_MSI_MAP_VECT_12     0x00c00000
#define I2C_CH6_MSI_MAP_VECT_13     0x15000000
#define MSI_VECTOR_MAP2             0x5c
#define I2C_CH7_MSI_MAP_VECT_14     0x0000000e
#define MSI_VECTOR_MAP3             0x9c
#define I2C_CH8_MSI_MAP_VECT_8      0x00800000
#define I2C_CH8_MSI_MAP_VECT_16     0x01100000
#define I2C_CH9_MSI_MAP_VECT_9      0x12000000
#define I2C_CH9_MSI_MAP_VECT_17     0x24000000
#define MSI_VECTOR_MAP4             0xa0
#define I2C_CH10_MSI_MAP_VECT_10    0x0000000a
#define I2C_CH10_MSI_MAP_VECT_18    0x00000012
#define I2C_CH11_MSI_MAP_VECT_11    0x00000120
#define I2C_CH11_MSI_MAP_VECT_19    0x00000260
#define I2C_CH12_MSI_MAP_VECT_12    0x00002800
#define I2C_CH12_MSI_MAP_VECT_20    0x00005000
#define I2C_CH13_MSI_MAP_VECT_13    0x00058000
#define I2C_CH13_MSI_MAP_VECT_21    0x000a8000
#define I2C_CH14_MSI_MAP_VECT_14    0x00c00000
#define I2C_CH14_MSI_MAP_VECT_22    0x01600000
#define I2C_CH15_MSI_MAP_VECT_8     0x10000000
#define I2C_CH15_MSI_MAP_VECT_23    0x2e000000
#define MSI_VECTOR_MAP5             0xa4
#define I2C_CH16_MSI_MAP_VECT_9     0x00000009
#define I2C_CH16_MSI_MAP_VECT_24    0x00000018

#define MSI_VECTOR_REV_00           16
#define MSI_VECTOR_REV_01           32

#define FPGA_MSI_VECTOR_ID_4       4
#define FPGA_MSI_VECTOR_ID_5       5
#define FPGA_MSI_VECTOR_ID_8       8
#define FPGA_MSI_VECTOR_ID_9       9
#define FPGA_MSI_VECTOR_ID_10      10
#define FPGA_MSI_VECTOR_ID_11      11
#define FPGA_MSI_VECTOR_ID_12      12
#define FPGA_MSI_VECTOR_ID_13      13
#define FPGA_MSI_VECTOR_ID_14      14
#define FPGA_MSI_VECTOR_ID_15      15   /*Note: this is external MSI vector id */
#define FPGA_MSI_VECTOR_ID_16      16
#define FPGA_MSI_VECTOR_ID_17      17
#define FPGA_MSI_VECTOR_ID_18      18
#define FPGA_MSI_VECTOR_ID_19      19
#define FPGA_MSI_VECTOR_ID_20      20
#define FPGA_MSI_VECTOR_ID_21      21
#define FPGA_MSI_VECTOR_ID_22      22
#define FPGA_MSI_VECTOR_ID_23      23
#define FPGA_MSI_VECTOR_ID_24      24



static int total_i2c_pci_bus = 0;
static uint32_t board_rev_type = 0;
static struct fpgalogic_i2c    fpgalogic_i2c[I2C_PCI_MAX_BUS];
static struct i2c_adapter     i2c_pci_adap[I2C_PCI_MAX_BUS];
static struct mutex         i2c_xfer_lock[I2C_PCI_MAX_BUS];

static void fpgai2c_reg_set_8(struct fpgalogic_i2c *i2c, int reg, u8 value)
{
    iowrite8(value, i2c->base + (reg << i2c->reg_shift));
}

static void fpgai2c_reg_set_16(struct fpgalogic_i2c *i2c, int reg, u8 value)
{
    iowrite16(value, i2c->base + (reg << i2c->reg_shift));
}

static void fpgai2c_reg_set_32(struct fpgalogic_i2c *i2c, int reg, u8 value)
{
    iowrite32(value, i2c->base + (reg << i2c->reg_shift));
}

static void fpgai2c_reg_set_16be(struct fpgalogic_i2c *i2c, int reg, u8 value)
{
    iowrite16be(value, i2c->base + (reg << i2c->reg_shift));
}

static void fpgai2c_reg_set_32be(struct fpgalogic_i2c *i2c, int reg, u8 value)
{
    iowrite32be(value, i2c->base + (reg << i2c->reg_shift));
}

static inline u8 fpgai2c_reg_get_8(struct fpgalogic_i2c *i2c, int reg)
{
    return ioread8(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 fpgai2c_reg_get_16(struct fpgalogic_i2c *i2c, int reg)
{
    return ioread16(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 fpgai2c_reg_get_32(struct fpgalogic_i2c *i2c, int reg)
{
    return ioread32(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 fpgai2c_reg_get_16be(struct fpgalogic_i2c *i2c, int reg)
{
    return ioread16be(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 fpgai2c_reg_get_32be(struct fpgalogic_i2c *i2c, int reg)
{
    return ioread32be(i2c->base + (reg << i2c->reg_shift));
}

static inline void fpgai2c_reg_set(struct fpgalogic_i2c *i2c, int reg, u8 value)
{
    i2c->reg_set(i2c, reg, value);
    udelay(100);
}

static inline u8 fpgai2c_reg_get(struct fpgalogic_i2c *i2c, int reg)
{
    udelay(100);
    return i2c->reg_get(i2c, reg);
}

static void fpgai2c_dump(struct fpgalogic_i2c *i2c)
{
    u8 tmp;

    PRINT("Logic register dump:\n");

    tmp = fpgai2c_reg_get(i2c, FPGAI2C_REG_PRELOW);
    PRINT("FPGAI2C_REG_PRELOW (%d) = 0x%x\n",FPGAI2C_REG_PRELOW,tmp);

    tmp = fpgai2c_reg_get(i2c, FPGAI2C_REG_PREHIGH);
    PRINT("FPGAI2C_REG_PREHIGH(%d) = 0x%x\n",FPGAI2C_REG_PREHIGH,tmp);

    tmp = fpgai2c_reg_get(i2c, FPGAI2C_REG_CONTROL);
    PRINT("FPGAI2C_REG_CONTROL(%d) = 0x%x\n",FPGAI2C_REG_CONTROL,tmp);

    tmp = fpgai2c_reg_get(i2c, FPGAI2C_REG_DATA);
    PRINT("FPGAI2C_REG_DATA   (%d) = 0x%x\n",FPGAI2C_REG_DATA,tmp);

    tmp = fpgai2c_reg_get(i2c, FPGAI2C_REG_CMD);
    PRINT("FPGAI2C_REG_CMD    (%d) = 0x%x\n",FPGAI2C_REG_CMD,tmp);
}

static void fpgai2c_stop(struct fpgalogic_i2c *i2c)
{
    fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_STOP);
}

/*
 * dell_get_mutex must be called prior to calling this function.
 */
static int fpgai2c_poll(struct fpgalogic_i2c *i2c)
{
    u8 stat = fpgai2c_reg_get(i2c, FPGAI2C_REG_STATUS);
    struct i2c_msg *msg = i2c->msg;
    u8 addr;

    /* Ready? */
    if (stat & FPGAI2C_REG_STAT_TIP)
        return -EBUSY;

    if (i2c->state == STATE_DONE || i2c->state == STATE_ERROR) {
        /* Stop has been sent */
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_IACK);
        if (i2c->state == STATE_ERROR)
            return -EIO;
        return 0;
    }

    /* Error? */
    if (stat & FPGAI2C_REG_STAT_ARBLOST) {
        i2c->state = STATE_ERROR;
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_STOP);
        return -EAGAIN;
    }

    if (i2c->state == STATE_INIT) {
        if (stat & FPGAI2C_REG_STAT_BUSY)
            return -EBUSY;

        i2c->state = STATE_ADDR;
    }

    if (i2c->state == STATE_ADDR) {
        /* 10 bit address? */
        if (i2c->msg->flags & I2C_M_TEN) {
            addr = 0xf0 | ((i2c->msg->addr >> 7) & 0x6);
            i2c->state = STATE_ADDR10;
        } else {
            addr = (i2c->msg->addr << 1);
            i2c->state = STATE_START;
        }

        /* Set read bit if necessary */
        addr |= (i2c->msg->flags & I2C_M_RD) ? 1 : 0;

        fpgai2c_reg_set(i2c, FPGAI2C_REG_DATA, addr);
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_START);

        return 0;
    }

    /* Second part of 10 bit addressing */
    if (i2c->state == STATE_ADDR10) {
        fpgai2c_reg_set(i2c, FPGAI2C_REG_DATA, i2c->msg->addr & 0xff);
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_WRITE);

        i2c->state = STATE_START;
        return 0;
    }

    if (i2c->state == STATE_START || i2c->state == STATE_WRITE) {
        i2c->state = (msg->flags & I2C_M_RD) ? STATE_READ : STATE_WRITE;

        if (stat & FPGAI2C_REG_STAT_NACK) {
            i2c->state = STATE_ERROR;
            fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_STOP);
            return -ENXIO;
        }
    } else {
        msg->buf[i2c->pos++] = fpgai2c_reg_get(i2c, FPGAI2C_REG_DATA);
    }

    if (i2c->pos >= msg->len) {
        i2c->nmsgs--;
        i2c->msg++;
        i2c->pos = 0;
        msg = i2c->msg;

        if (i2c->nmsgs) {
            if (!(msg->flags & I2C_M_NOSTART)) {
                i2c->state = STATE_ADDR;
                return 0;
            } else {
                i2c->state = (msg->flags & I2C_M_RD)
                    ? STATE_READ : STATE_WRITE;
            }
        } else {
            i2c->state = STATE_DONE;
            fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_STOP);
            return 0;
        }
    }

    if (i2c->state == STATE_READ) {
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, i2c->pos == (msg->len - 1) ?
                FPGAI2C_REG_CMD_READ_NACK : FPGAI2C_REG_CMD_READ_ACK);
    } else {
        fpgai2c_reg_set(i2c, FPGAI2C_REG_DATA, msg->buf[i2c->pos++]);
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_WRITE);
    }

    return 0;
}

static ssize_t get_mod_msi(struct device *dev, struct device_attribute *devattr, char *buf)
{
	int ind = 0, port_status=0, port_irq_status=0;
    struct fpgapci_dev *fpgapci = (struct fpgapci_dev*) dev_get_drvdata(dev);
	PRINT("%s:xcvr_intr_count:%u\n", __FUNCTION__, fpgapci->xcvr_intr_count);
	for(ind=0;ind<64;ind++)
	{ 
       	port_status = ioread32(fpga_ctl_addr + PORT_STS_OFFSET + (ind*16));
       	port_irq_status = ioread32(fpga_ctl_addr + PORT_IRQ_STS_OFFSET + (ind*16));
		PRINT("%s:port:%d, port_status:%#x, port_irq_status:%#x\n", __FUNCTION__, ind, port_status, port_irq_status);
	}	
	return sprintf(buf,"0x%04x\n",fpgapci->xcvr_intr_count);
}
static DEVICE_ATTR(port_msi, S_IRUGO, get_mod_msi, NULL);

static struct attribute *port_attrs[] = {
    &dev_attr_port_msi.attr,
    NULL,
};

static struct attribute_group port_attr_grp = {
    .attrs = port_attrs,
};


static irqreturn_t fpgaport_1_32_isr(int irq, void *dev)
{
	struct pci_dev *pdev = dev;
    struct fpgapci_dev *fpgapci = (struct fpgapci_dev*) dev_get_drvdata(&pdev->dev);
	int ind = 0, port_status=0, port_irq_status=0;
	for(ind=0;ind<32;ind++)
	{ 
        port_irq_status = ioread32(fpga_ctl_addr + PORT_IRQ_STS_OFFSET + (ind*16));
		if(port_irq_status&(IRQ_LTCH_STS|PRSNT_LTCH_STS))
		{
			PRINT("%s:port:%d, port_status:%#x, port_irq_status:%#x\n", __FUNCTION__, ind, port_status, port_irq_status);
				//write on clear
        	iowrite32( IRQ_LTCH_STS|PRSNT_LTCH_STS,fpga_ctl_addr + PORT_IRQ_STS_OFFSET + (ind*16));
		}
	}	
    fpgapci->xcvr_intr_count++;
	PRINT("%s: xcvr_intr_count:%u\n", __FUNCTION__, fpgapci->xcvr_intr_count);
	sysfs_notify(&pdev->dev.kobj, NULL, "port_msi");
	return IRQ_HANDLED;
}

static irqreturn_t fpgaport_33_64_isr(int irq, void *dev)
{
	struct pci_dev *pdev = dev;
    struct fpgapci_dev *fpgapci = (struct fpgapci_dev*) dev_get_drvdata(&pdev->dev);
	int ind = 0, port_status=0, port_irq_status=0;
	for(ind=32;ind<64;ind++)
	{ 
        port_irq_status = ioread32(fpga_ctl_addr + PORT_IRQ_STS_OFFSET + (ind*16));
		if(port_irq_status| (IRQ_LTCH_STS|PRSNT_LTCH_STS))
		{
			PRINT("%s:port:%d, port_status:%#x, port_irq_status:%#x\n", __FUNCTION__, ind, port_status, port_irq_status);
				//write on clear
        	iowrite32( IRQ_LTCH_STS|PRSNT_LTCH_STS,fpga_ctl_addr + PORT_IRQ_STS_OFFSET + (ind*16));
		}
	}	
    fpgapci->xcvr_intr_count++;
	PRINT("%s: xcvr_intr_count:%u\n", __FUNCTION__, fpgapci->xcvr_intr_count);
	sysfs_notify(&pdev->dev.kobj, NULL, "port_msi");
	return IRQ_HANDLED;
}

static void fpgai2c_process(struct fpgalogic_i2c *i2c)
{
    struct i2c_msg *msg = i2c->msg;
    u8 stat = fpgai2c_reg_get(i2c, FPGAI2C_REG_STATUS);

    PRINT("fpgai2c_process in. status reg :0x%x\n", stat);

    if ((i2c->state == STATE_DONE) || (i2c->state == STATE_ERROR)) {
        /* stop has been sent */
        PRINT("fpgai2c_process FPGAI2C_REG_CMD_IACK stat = 0x%x Set FPGAI2C_REG_CMD(0%x) FPGAI2C_REG_CMD_IACK = 0x%x\n",stat, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_IACK);
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_IACK);
        wake_up(&i2c->wait);
        return;
    }


    /* error? */
    if (stat & FPGAI2C_REG_STAT_ARBLOST) {
        i2c->state = STATE_ERROR;
        PRINT("fpgai2c_process FPGAI2C_REG_STAT_ARBLOST FPGAI2C_REG_CMD_STOP\n");
        fpgai2c_stop(i2c);
        return;
    }

    if ((i2c->state == STATE_START) || (i2c->state == STATE_WRITE)) {
        i2c->state =
            (msg->flags & I2C_M_RD) ? STATE_READ : STATE_WRITE;

        if (stat & FPGAI2C_REG_STAT_NACK) {
            i2c->state = STATE_ERROR;
            fpgai2c_stop(i2c);
            return;
        }
    } else
    {
        msg->buf[i2c->pos++] = fpgai2c_reg_get(i2c, FPGAI2C_REG_DATA);
    }

    /* end of msg? */
    if (i2c->pos == msg->len) {
        i2c->nmsgs--;
        i2c->msg++;
        i2c->pos = 0;
        msg = i2c->msg;

        if (i2c->nmsgs) {    /* end? */
            /* send start? */
            if (!(msg->flags & I2C_M_NOSTART)) {

                u8 addr = (msg->addr << 1);

                if (msg->flags & I2C_M_RD)
                    addr |= 1;

                i2c->state = STATE_START;
                fpgai2c_reg_set(i2c, FPGAI2C_REG_DATA, addr);
                fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD,  FPGAI2C_REG_CMD_START);
                return;
            } else
            {
                i2c->state = (msg->flags & I2C_M_RD)
                    ? STATE_READ : STATE_WRITE;
            }
        } else {
            i2c->state = STATE_DONE;
            fpgai2c_stop(i2c);
            return;
        }
    }

    if (i2c->state == STATE_READ) {
        PRINT("fpgai2c_poll STATE_READ i2c->pos=%d msg->len-1 = 0x%x set FPGAI2C_REG_CMD = 0x%x\n",i2c->pos, msg->len-1,
                i2c->pos == (msg->len-1) ?  FPGAI2C_REG_CMD_READ_NACK : FPGAI2C_REG_CMD_READ_ACK);
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, i2c->pos == (msg->len-1) ?
                FPGAI2C_REG_CMD_READ_NACK : FPGAI2C_REG_CMD_READ_ACK);
    } else {
        PRINT("fpgai2c_process set FPGAI2C_REG_DATA(0x%x)\n",FPGAI2C_REG_DATA);
        fpgai2c_reg_set(i2c, FPGAI2C_REG_DATA, msg->buf[i2c->pos++]);
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_WRITE);
    }
}

static irqreturn_t fpgai2c_isr(int irq, void *dev_id)
{
    struct fpgalogic_i2c *i2c = dev_id;
    fpgai2c_process(i2c);

    return IRQ_HANDLED;
}
void dell_get_mutex(struct fpgalogic_i2c *i2c)
{
    mutex_lock(&i2c->lock);
}

/**
 * dell_release_mutex - release mutex
 */
void dell_release_mutex(struct fpgalogic_i2c *i2c)
{
    mutex_unlock(&i2c->lock);
}

static int fpgai2c_xfer(struct i2c_adapter *adap, struct i2c_msg *msgs, int num)
{
    struct fpgalogic_i2c *i2c = i2c_get_adapdata(adap);
    int ret;
    unsigned long timeout = jiffies + msecs_to_jiffies(1000);

    i2c->msg = msgs;
    i2c->pos = 0;
    i2c->nmsgs = num;
    i2c->state = (use_irq == 1) ? STATE_START : STATE_INIT;

    PRINT("i2c->msg->addr = 0x%x i2c->msg->flags = 0x%x\n",i2c->msg->addr,i2c->msg->flags);
    PRINT("I2C_M_RD = 0x%x i2c->msg->addr << 1 = 0x%x\n",I2C_M_RD,i2c->msg->addr << 1);

    if (!use_irq) {
        /* Handle the transfer */
        while (time_before(jiffies, timeout)) {
            dell_get_mutex(i2c);
            ret = fpgai2c_poll(i2c);
            dell_release_mutex(i2c);

            if (i2c->state == STATE_DONE || i2c->state == STATE_ERROR)
                return (i2c->state == STATE_DONE) ? num : ret;

            if (ret == 0)
                timeout = jiffies + HZ;

            usleep_range(5, 15);
        }

        i2c->state = STATE_ERROR;

        return -ETIMEDOUT;


    } else {
        PRINT("Set FPGAI2C_REG_DATA(0%x) val = 0x%x\n",FPGAI2C_REG_DATA,
                (i2c->msg->addr << 1) |    ((i2c->msg->flags & I2C_M_RD) ? 1:0));

        fpgai2c_reg_set(i2c, FPGAI2C_REG_DATA,
                (i2c->msg->addr << 1) |
                ((i2c->msg->flags & I2C_M_RD) ? 1:0));
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_START);

        /* Interrupt mode */
        if (wait_event_timeout(i2c->wait, (i2c->state == STATE_ERROR) ||
                    (i2c->state == STATE_DONE), HZ))
            return (i2c->state == STATE_DONE) ? num : -EIO;
        else
            return -ETIMEDOUT;
    }
}

static int fpgai2c_init(struct fpgalogic_i2c *i2c)
{
    int prescale;
    int diff;
    u8 ctrl;

    if (i2c->reg_io_width == 0)
        i2c->reg_io_width = 1; /* Set to default value */

    if (!i2c->reg_set || !i2c->reg_get) {
        bool be = 0; //1:big_endian 0:little_endian

        switch (i2c->reg_io_width) {
            case 1:
                i2c->reg_set = fpgai2c_reg_set_8;
                i2c->reg_get = fpgai2c_reg_get_8;
                break;

            case 2:
                i2c->reg_set = be ? fpgai2c_reg_set_16be : fpgai2c_reg_set_16;
                i2c->reg_get = be ? fpgai2c_reg_get_16be : fpgai2c_reg_get_16;
                break;

            case 4:
                i2c->reg_set = be ? fpgai2c_reg_set_32be : fpgai2c_reg_set_32;
                i2c->reg_get = be ? fpgai2c_reg_get_32be : fpgai2c_reg_get_32;
                break;

            default:
                PRINT("Unsupported I/O width (%d)\n",
                        i2c->reg_io_width);
                return -EINVAL;
        }
    }

    ctrl = fpgai2c_reg_get(i2c, FPGAI2C_REG_CONTROL);

    PRINT("%s(), line:%d\n", __func__, __LINE__);
    PRINT("i2c->base = 0x%p\n",i2c->base);

    PRINT("ctrl = 0x%x\n",ctrl);
    PRINT("set ctrl = 0x%x\n",ctrl & ~(FPGAI2C_REG_CTRL_EN|FPGAI2C_REG_CTRL_IEN));

    /* make sure the device is disabled */
    fpgai2c_reg_set(i2c, FPGAI2C_REG_CONTROL, ctrl & ~(FPGAI2C_REG_CTRL_EN|FPGAI2C_REG_CTRL_IEN));

    /*
     *  I2C Frequency depends on host clock
     *  input clock of 100MHz
     *  prescale to 100MHz / ( 5*100kHz) -1 = 199 = 0x4F 100000/(5*100)-1=199=0xc7
     */
    prescale = (i2c->ip_clock_khz / (5 * i2c->bus_clock_khz)) - 1;
    prescale = clamp(prescale, 0, 0xffff);

    diff = i2c->ip_clock_khz / (5 * (prescale + 1)) - i2c->bus_clock_khz;
    if (abs(diff) > i2c->bus_clock_khz / 10) {
        PRINT("Unsupported clock settings: core: %d KHz, bus: %d KHz\n",
                i2c->ip_clock_khz, i2c->bus_clock_khz);
        return -EINVAL;
    }

    fpgai2c_reg_set(i2c, FPGAI2C_REG_PRELOW, prescale & 0xff);
    fpgai2c_reg_set(i2c, FPGAI2C_REG_PREHIGH, prescale >> 8);

    /* Init the device */
    fpgai2c_reg_set(i2c, FPGAI2C_REG_CMD, FPGAI2C_REG_CMD_IACK);
    if (!use_irq)
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CONTROL, ctrl | FPGAI2C_REG_CTRL_EN);
    else
        fpgai2c_reg_set(i2c, FPGAI2C_REG_CONTROL, ctrl | FPGAI2C_REG_CTRL_IEN | FPGAI2C_REG_CTRL_EN);

    fpgai2c_dump(i2c);

    /* Initialize interrupt handlers if not already done */
    init_waitqueue_head(&i2c->wait);

    return 0;
}


static u32 fpgai2c_func(struct i2c_adapter *adap)
{
    return I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL;
}

static const struct i2c_algorithm fpgai2c_algorithm = {
    .master_xfer = fpgai2c_xfer,
    .functionality = fpgai2c_func,
};

static int  i2c_pci_add_bus (struct i2c_adapter *adap)
{
    int ret = 0;
    /* Register new adapter */
    adap->algo = &fpgai2c_algorithm;
    ret = i2c_add_numbered_adapter(adap);
    return ret;
}

static int i2c_init_internal_data(void)
{
    int i;
    PRINT("%s(), line:%d\n", __func__, __LINE__);

    for( i = 0; i < total_i2c_pci_bus; i++ )
    {
        fpgalogic_i2c[i].reg_shift = 0; /* 8 bit registers */
        fpgalogic_i2c[i].reg_io_width = 1; /* 8 bit read/write */
        fpgalogic_i2c[i].timeout = 500;//1000;//1ms
        fpgalogic_i2c[i].ip_clock_khz = 100000;//100000;/* input clock of 100MHz */
        fpgalogic_i2c[i].bus_clock_khz = 100;
        fpgalogic_i2c[i].base = fpga_base_addr + i*FPGALOGIC_CH_OFFSET;
        mutex_init(&fpgalogic_i2c[i].lock);
        fpgai2c_init(&fpgalogic_i2c[i]);
    }

    return 0;
}


static int i2c_pci_init (void)
{
    int i;

    if (num_bus == 0) {
        board_rev_type = ioread32(fpga_ctl_addr + MB_BRD_REV_TYPE);

        if ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_00) {
            num_bus = I2C_PCI_MAX_BUS_REV00;
        } else if (((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_01) ||
                ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_02) ||
                ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_03)) {
            switch (board_rev_type & MB_BRD_TYPE_MASK){
                case BRD_TYPE_S5212_NON_NEBS:
                case BRD_TYPE_S5212_NEBS:
                    num_bus = I2C_PCI_BUS_NUM_5;
                    break;
                case BRD_TYPE_S5224_NON_NEBS:
                case BRD_TYPE_S5224_NEBS:
                    num_bus = I2C_PCI_BUS_NUM_7;
                    break;
                case BRD_TYPE_Z9232_NON_NEBS:
                case BRD_TYPE_Z9232_NEBS:
                case BRD_TYPE_S5232_NON_NEBS:
                case BRD_TYPE_S5232_NEBS:
                    num_bus = I2C_PCI_BUS_NUM_8;
                    break;
                case BRD_TYPE_S5248_NON_NEBS:
                case BRD_TYPE_S5248_NEBS:
                    num_bus = I2C_PCI_BUS_NUM_10;
                    break;
                case BRD_TYPE_Z9264_NON_NEBS:
                case BRD_TYPE_Z9264_NEBS:
                    num_bus = I2C_PCI_BUS_NUM_12;
                    break;
                case BRD_TYPE_S5296_NON_NEBS:
                case BRD_TYPE_S5296_NEBS:
                    num_bus = I2C_PCI_BUS_NUM_16;
                    break;
                default:
                    num_bus = I2C_PCI_BUS_NUM_16;
                    printk("Wrong BRD_TYPE: 0x%x\n", board_rev_type);
                    break;
            }
        } else {
            printk("Wrong board_rev_type 0x%x\n", board_rev_type);
        }
    }

    printk("board_rev_type 0x%x, num_bus 0x%x\n", board_rev_type, num_bus);
    total_i2c_pci_bus = num_bus;

    memset (&i2c_pci_adap, 0, sizeof(i2c_pci_adap));
    memset (&fpgalogic_i2c, 0, sizeof(fpgalogic_i2c));
    for(i=0; i < i2c_bus_controller_numb; i++)
        mutex_init(&i2c_xfer_lock[i]);

    /* Initialize driver's itnernal data structures */
    i2c_init_internal_data();

    for (i = 0 ; i < total_i2c_pci_bus; i ++) {

        i2c_pci_adap[i].owner = THIS_MODULE;
        i2c_pci_adap[i].class = I2C_CLASS_HWMON | I2C_CLASS_SPD;

        i2c_pci_adap[i].algo_data = &fpgalogic_i2c[i];
        /* /dev/i2c-600 ~ /dev/i2c-615 for FPGA LOGIC I2C channel  controller 1-7  */
        i2c_pci_adap[i].nr = i+600;
        sprintf( i2c_pci_adap[ i ].name, "i2c-pci-%d", i );
        /* Add the bus via the algorithm code */
        if( i2c_pci_add_bus( &i2c_pci_adap[ i ] ) != 0 )
        {
            PRINT("Cannot add bus %d to algorithm layer\n", i );
            return( -ENODEV );
        }
        i2c_set_adapdata(&i2c_pci_adap[i], &fpgalogic_i2c[i]);

        PRINT( "Registered bus id: %s\n", kobject_name(&i2c_pci_adap[ i ].dev.kobj));
    }

    return 0;
}

static void i2c_pci_deinit(void)
{
    int i;
    for( i = 0; i < total_i2c_pci_bus; i++ ){
        i2c_del_adapter(&i2c_pci_adap[i]);
    }

}

/* Find upstream PCIe root node.
 * Used for re-training and disabling AER. */
static struct pci_dev* find_upstream_dev (struct pci_dev *dev)
{
    struct pci_bus *bus = 0;
    struct pci_dev *bridge = 0;
    struct pci_dev *cur = 0;
    int found_dev = 0;

    bus = dev->bus;
    if (bus == 0) {
        PRINT ( "Device doesn't have an associated bus!\n");
        return 0;
    }

    bridge = bus->self;
    if (bridge == 0) {
        PRINT ( "Can't get the bridge for the bus!\n");
        return 0;
    }

    PRINT ( "Upstream device %x/%x, bus:slot.func %02x:%02x.%02x\n",
            bridge->vendor, bridge->device,
            bridge->bus->number, PCI_SLOT(bridge->devfn), PCI_FUNC(bridge->devfn));

    PRINT ( "List of downstream devices:");
    list_for_each_entry (cur, &bus->devices, bus_list) {
        if (cur != 0) {
            PRINT ( "  %x/%x", cur->vendor, cur->device);
            if (cur == dev) {
                found_dev = 1;
            }
        }
    }
    PRINT ( "\n");
    if (found_dev) {
        return bridge;
    } else {
        PRINT ( "Couldn't find upstream device!\n");
        return 0;
    }
}


static int scan_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev)
{
    int i;

    for (i = 0; i < PCI_NUM_BARS; i++) {
        unsigned long bar_start = pci_resource_start(dev, i);
        if (bar_start) {
            unsigned long bar_end = pci_resource_end(dev, i);
            unsigned long bar_flags = pci_resource_flags(dev, i);
            PRINT ( "BAR[%d] 0x%08lx-0x%08lx flags 0x%08lx",
                    i, bar_start, bar_end, bar_flags);
        }
    }

    return 0;
}


/**
 * Map the device memory regions into kernel virtual address space
 * after verifying their sizes respect the minimum sizes needed, given
 * by the bar_min_len[] array.
 */
static int map_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev)
{
    int i;

    for (i = 0; i < PCI_NUM_BARS; i++){
        phys_addr_t bar_start = pci_resource_start(dev, i);
        phys_addr_t bar_end = pci_resource_end(dev, i);
        unsigned long bar_length = bar_end - bar_start + 1;
        fpgapci->bar_length[i] = bar_length;


        if (!bar_start || !bar_end) {
            fpgapci->bar_length[i] = 0;
            continue;
        }

        if (bar_length < 1) {
            PRINT ( "BAR #%d length is less than 1 byte\n", i);
            continue;
        }

        PRINT ( "bar_start=%llx, bar_end=%llx, bar_length=%lx, flag=%lx\n", bar_start,
                bar_end, bar_length, pci_resource_flags(dev, i));

        /* map the device memory or IO region into kernel virtual
         * address space */
        fpgapci->bar[i] = ioremap_nocache (bar_start + FPGALOGIC_I2C_BASE, I2C_PCI_MAX_BUS * FPGALOGIC_CH_OFFSET);

        if (!fpgapci->bar[i]) {
            PRINT ( "Could not map BAR #%d.\n", i);
            return -1;
        }

        PRINT ( "BAR[%d] mapped at 0x%p with length %lu.", i,
                fpgapci->bar[i], bar_length);

        if(i == 0)  //FPGA register is in the BAR[0]
        {

            fpga_phys_addr = bar_start;
            fpga_ctl_addr = ioremap_nocache (bar_start, FPGA_CTL_REG_SIZE);
            fpga_base_addr = fpgapci->bar[i];
        }

        PRINT ( "BAR[%d] mapped at 0x%p with length %lu.\n", i,
                fpgapci->bar[i], bar_length);
    }
    return 0;
}

static void free_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev)
{
    int i;

    for (i = 0; i < PCI_NUM_BARS; i++) {
        if (fpgapci->bar[i]) {
            pci_iounmap(dev, fpgapci->bar[i]);
            fpgapci->bar[i] = NULL;
        }
    }
}

#define FPGA_PCI_NAME "FPGA_PCI"

/**
 * @brief Register specific function with msi interrupt line
 * @param dev Pointer to pci-device, which should be allocated
 * @param int interrupt number relative to global interrupt number
 * @return Returns error code or zero if success
 * */
static int register_intr_handler(struct pci_dev *dev, int irq_num_id)
{
    int err = 0;
    struct fpgapci_dev *fpgapci = 0;

    fpgapci = (struct fpgapci_dev*) dev_get_drvdata(&dev->dev);
    if (fpgapci == 0) {
        PRINT ( ": fpgapci_dev is 0\n");
        return err;
    }

    if ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_00) {
        /* Request interrupt line for unique function
         * alternatively function will be called from free_irq as well
         * with flag IRQF_SHARED */
        switch(irq_num_id) {
            /* Currently we only support test vector 2 for FPGA Logic I2C channel
             * controller 1-7  interrupt*/
	    	case FPGA_MSI_VECTOR_ID_4: 
                err = request_irq(dev->irq + irq_num_id, fpgaport_1_32_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, dev);
        		PRINT ( "%d: fpgapci_dev: irq: %d, %d\n", __LINE__, dev->irq, irq_num_id);
                fpgapci->irq_assigned++;
				break;
	    	case FPGA_MSI_VECTOR_ID_5: 
                err = request_irq(dev->irq + irq_num_id, fpgaport_33_64_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, dev);
        		PRINT ( "%d: fpgapci_dev: irq: %d, %d\n", __LINE__, dev->irq, irq_num_id);
                fpgapci->irq_assigned++;
				break;
            case FPGA_MSI_VECTOR_ID_8:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[0]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_9:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[1]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_10:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[2]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_11:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[3]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_12:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[4]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_13:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[5]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_14:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[6]);
                fpgapci->irq_assigned++;
                break;

            default:
                PRINT("No more interrupt handler for number (%d)\n",
                        dev->irq + irq_num_id);
                break;
        }
    } else if (((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_01) ||
            ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_02) ||
            ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_03)) {
        /* FPGA SPEC 4.3.1.34, First i2c channel mapped to vector 8 */
        switch (irq_num_id) {
	    	case FPGA_MSI_VECTOR_ID_4: 
                err = request_irq(dev->irq + irq_num_id, fpgaport_1_32_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, dev);
        		PRINT ( "%d: fpgapci_dev: irq: %d, %d\n", __LINE__, dev->irq, irq_num_id);
                fpgapci->irq_assigned++;
				break;
	    	case FPGA_MSI_VECTOR_ID_5: 
                err = request_irq(dev->irq + irq_num_id, fpgaport_33_64_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, dev);
        		PRINT ( "%d: fpgapci_dev: irq: %d, %d\n", __LINE__, dev->irq, irq_num_id);
                fpgapci->irq_assigned++;
				break;
            case FPGA_MSI_VECTOR_ID_8:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[0]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_9:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[1]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_10:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[2]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_11:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[3]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_12:
                err = request_irq(dev->irq + irq_num_id, fpgai2c_isr, IRQF_EARLY_RESUME,
                        FPGA_PCI_NAME, &fpgalogic_i2c[4]);
                fpgapci->irq_assigned++;
                break;
            case FPGA_MSI_VECTOR_ID_13:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_5) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[5]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_14:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_5) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[6]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_15:
                /*it is an external interrupt number. Ignore this case */
                break;
            case FPGA_MSI_VECTOR_ID_16:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_7) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[7]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_17:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_8) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[8]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_18:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_8) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[9]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_19:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_10) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[10]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_20:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_10) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[11]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_21:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_12) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[12]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_22:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_12) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[13]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_23:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_12) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[14]);
                    fpgapci->irq_assigned++;
                }
                break;
            case FPGA_MSI_VECTOR_ID_24:
                if (total_i2c_pci_bus > I2C_PCI_BUS_NUM_12) {
                    err = request_irq(dev->irq + irq_num_id, fpgai2c_isr,
                            IRQF_EARLY_RESUME, FPGA_PCI_NAME, &fpgalogic_i2c[15]);
                    fpgapci->irq_assigned++;
                }
                break;

            default:
                PRINT("No more interrupt handler for number (%d)\n",
                        dev->irq + irq_num_id);
                break;
        }
    }

    return err;
}
/* Mask for MSI Multi message enable bits */
#define     MSI_MME                 0x70
/**
 * These enums define the type of interrupt scheme that the overall
 * system uses.
 */
enum fpga_irq_type {
    INT_MSI_SINGLE,
    INT_MSI_MULTI,
    INT_MSIX,
    INT_NONE,
    INT_FENCE    /* Last item to guard from loop run-overs */
};
/**
 * @def PCI_DEVICE_STATUS
 * define the offset for STS register
 * from the start of PCI config space as specified in the
 * NVME_Comliance 1.0b. offset 06h:STS - Device status.
 * This register has error status for NVME PCI Exress
 * Card. After reading data from this reagister, the driver
 * will identify if any error is set during the operation and
 * report as kernel alert message.
 */
#define PCI_DEVICE_STATUS               0x6
/**
 * @def NEXT_MASK
 * This indicates the location of the next capability item
 * in the list.
 */
#define NEXT_MASK            0xFF00
/**
 * @def MSIXCAP_ID
 * This bit indicates if the pointer leading to this position
 * is a capability.
 */
#define MSIXCAP_ID            0x11
/**
 * @def MSICAP_ID
 * This bit indicates if the pointer leading to this position
 * is a capability.
 */
#define MSICAP_ID            0x5

/**
 * @def CL_MASK
 * This bit position indicates Capabilities List of the controller
 * The controller should support the PCI Power Management cap as a
 * minimum.
 */
#define CL_MASK              0x0010

/**
 * @def CAP_REG
 * Set to offset defined in NVME Spec 1.0b.
 */
#define CAP_REG                0x34
static void msi_set_enable(struct pci_dev *dev, int enable)
{
    int pos,maxvec;
    u16 control;
    int request_private_bits = 4;

    pos = pci_find_capability(dev, PCI_CAP_ID_MSI);

    if (pos) {
        pci_read_config_word(dev, pos + PCI_MSI_FLAGS, &control);
        maxvec = 1 << ((control & PCI_MSI_FLAGS_QMASK) >> 1);
        PRINT("control = 0x%x maxvec = 0x%x\n", control, maxvec);
        control &= ~PCI_MSI_FLAGS_ENABLE;


        /*
         * The PCI 2.3 spec mandates that there are at most 32
         * interrupts. If this device asks for more, only give it one.
         */
        if (request_private_bits > 5) {
            request_private_bits = 0;
        }

        /* Update the number of IRQs the device has available to it */
        control &= ~PCI_MSI_FLAGS_QSIZE;
        control |= (request_private_bits << 4);

        pci_write_config_word(dev, pos + PCI_MSI_FLAGS, control);
    }
}
/**
 * @brief Enables pcie-device and claims/remaps neccessary bar resources
 * @param dev Pointer to pci-device, which should be allocated
 * @return Returns error code or zero if success
 * */
static int fpgapci_setup_device(struct fpgapci_dev *fpgapci,struct pci_dev *dev)
{
    int err = 0;

    /* wake up the pci device */
    err = pci_enable_device(dev);
    if(err) {
        PRINT("failed to enable pci device %d\n", err);
        goto error_pci_en;
    }

    /* on platforms with buggy ACPI, pdev->msi_enabled may be set to
     * allow pci_enable_device to work. This indicates INTx was not routed
     * and only MSI should be used
     */

    pci_set_master(dev);

    /* Setup the BAR memory regions */
    err = pci_request_regions(dev, DRIVER_NAME);
    if (err) {
        PRINT("failed to enable pci device %d\n", err);
        goto error_pci_req;
    }

    scan_bars(fpgapci, dev);

    if (map_bars(fpgapci, dev)) {
        goto fail_map_bars;
    }

    i2c_pci_init();

    return 0;
    /* ERROR HANDLING */
fail_map_bars:
    pci_release_regions(dev);
error_pci_req:
    pci_disable_device(dev);
error_pci_en:
    return -ENODEV;
}

static int fpgapci_configure_msi(struct fpgapci_dev *fpgapci,struct pci_dev *dev)
{
    int err = 0, i;
    int request_vec;

    msi_set_enable(dev,1);
    PRINT("Check MSI capability after msi_set_enable\n");


    /*Above 4.1.12*/
    request_vec = total_i2c_pci_bus;
    err = pci_alloc_irq_vectors(dev, request_vec, pci_msi_vec_count(dev),
            PCI_IRQ_MSI);//PCI_IRQ_AFFINITY | PCI_IRQ_MSI);

    if (err <= 0) {
        PRINT("Cannot set MSI vector (%d)\n", err);
        goto error_no_msi;
    } else {
        PRINT("Got %d MSI vectors starting at %d\n", err, dev->irq);
        if ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_00) {
            if (err < MSI_VECTOR_REV_00) {
                goto error_disable_msi;
            }
        } else if (((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_01) ||
                ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_02) ||
                ((board_rev_type & MB_BRD_REV_MASK) == MB_BRD_REV_03)) {
            if (err < MSI_VECTOR_REV_01) {
                goto error_disable_msi;
            }
        }
    }
    fpgapci->irq_first = dev->irq;
    fpgapci->irq_length = err;
    fpgapci->irq_assigned = 0;


    for(i = 0; i < fpgapci->irq_length; i++) {
        err = register_intr_handler(dev, i);
        if (err) {
            PRINT("Cannot request Interrupt number %d\n", i);
            goto error_pci_req_irq;
        }
    }

    return 0;

error_pci_req_irq:
    for(i = 0; i < fpgapci->irq_assigned; i++)
    {
        PRINT("free_irq %d i =%d\n",fpgapci->irq_first + i,i);
        if (i < 7)
            free_irq(fpgapci->irq_first + 8 + i, &fpgalogic_i2c[i]);
        else
            free_irq(fpgapci->irq_first + 8 + i + 1, &fpgalogic_i2c[i]);
    }
error_disable_msi:
    pci_disable_msi(fpgapci->pci_dev);
error_no_msi:
    return -ENOSPC;
}

static int fpgapci_probe(struct pci_dev *dev, const struct pci_device_id *id)
{
    struct fpgapci_dev *fpgapci = 0;
    int status = 0;

#ifdef TEST
    PRINT ( " vendor = 0x%x, device = 0x%x, class = 0x%x, bus:slot.func = %02x:%02x.%02x\n",
            dev->vendor, dev->device, dev->class,
            dev->bus->number, PCI_SLOT(dev->devfn), PCI_FUNC(dev->devfn));
#endif
    fpgapci = kzalloc(sizeof(struct fpgapci_dev), GFP_KERNEL);

    if (!fpgapci) {
        PRINT( "Couldn't allocate memory!\n");
        goto fail_kzalloc;
    }

    fpgapci->pci_dev = dev;
    dev_set_drvdata(&dev->dev, (void*)fpgapci);

    fpgapci->upstream = find_upstream_dev (dev);
    status = sysfs_create_group(&dev->dev.kobj, &port_attr_grp);
    if (status) {
        printk(KERN_INFO "%s:Cannot create sysfs\n", __FUNCTION__);
    }

    if(fpgapci_setup_device(fpgapci,dev)) {
        goto error_no_device;
    }

    if (use_irq) {
        if(fpgapci_configure_msi(fpgapci,dev)) {
            goto error_cannot_configure;
        }
    }


    return 0;
    /* ERROR HANDLING */
error_cannot_configure:
    printk("error_cannot_configure\n");
    free_bars (fpgapci, dev);
    pci_release_regions(dev);
    pci_disable_device(dev);
error_no_device:
    i2c_pci_deinit();
    printk("error_no_device\n");
fail_kzalloc:
    return -1;


}

static void fpgapci_remove(struct pci_dev *dev)
{
    struct fpgapci_dev *fpgapci = 0;
    int i;
    PRINT (": dev is %p\n", dev);

    if (dev == 0) {
        PRINT ( ": dev is 0\n");
        return;
    }

    fpgapci = (struct fpgapci_dev*) dev_get_drvdata(&dev->dev);
    if (fpgapci == 0) {
        PRINT ( ": fpgapci_dev is 0\n");
        return;
    }
    i2c_pci_deinit();
    //
    if (use_irq)
    {
        for(i = 0; i < fpgapci->irq_assigned; i++)
        {
            PRINT("free_irq %d i =%d\n",fpgapci->irq_first + i,i);
            if (i < 7)
                free_irq(fpgapci->irq_first + 8 + i, &fpgalogic_i2c[i]);
            else
                free_irq(fpgapci->irq_first + 8 + i + 1, &fpgalogic_i2c[i]);
        }
    }
    pci_disable_msi(fpgapci->pci_dev);
    free_bars (fpgapci, dev);
    pci_disable_device(dev);
    pci_release_regions(dev);

    kfree (fpgapci);
}

static const struct pci_device_id fpgapci_ids[] = {
    {PCI_DEVICE(PCI_VENDOR_ID_XILINX, DEVICE)},
    {0, },
};

MODULE_DEVICE_TABLE(pci, fpgapci_ids);

static struct pci_driver fpgapci_driver = {
    .name = DRIVER_NAME,
    .id_table = fpgapci_ids,
    .probe = fpgapci_probe,
    .remove = fpgapci_remove,
    /* resume, suspend are optional */
};

/* Initialize the driver module (but not any device) and register
 * the module with the kernel PCI subsystem. */
static int __init fpgapci_init(void)
{

    if (pci_register_driver(&fpgapci_driver)) {
        PRINT("pci_unregister_driver\n");
        pci_unregister_driver(&fpgapci_driver);
        return -ENODEV;
    }

    return 0;
}

static void __exit fpgapci_exit(void)
{
    PRINT ("fpgapci_exit");

    /* unregister this driver from the PCI bus driver */
    pci_unregister_driver(&fpgapci_driver);

}


module_init (fpgapci_init);
module_exit (fpgapci_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("joyce_yu@dell.com");
MODULE_DESCRIPTION ("Driver for FPGA Logic I2C bus");
MODULE_SUPPORTED_DEVICE ("FPGA Logic I2C bus");
