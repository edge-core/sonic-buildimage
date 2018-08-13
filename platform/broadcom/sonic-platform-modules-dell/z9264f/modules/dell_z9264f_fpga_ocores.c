 /*
 * Copyright (C) 2018 Joyce Yu <Joyce_Yu@Dell.com>
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

/**
 * @file fpga_ocores.c
 * @brief This is a driver to interface with Linux Open Cores driver for FPGA i2c access
 *
 */

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

#define DRIVER_NAME       "fpgapci"
#define PCI_NUM_BARS 4

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

};

static int use_irq = 0;
module_param(use_irq, int, 0644);
MODULE_PARM_DESC(use_irq, "Get an use_irq value from user...\n");


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


/* Static function declarations */
static int  fpgapci_probe(struct pci_dev *dev, const struct pci_device_id *id);
static void fpgapci_remove(struct pci_dev *dev);

static int  scan_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev);
static int  map_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev);
static void free_bars(struct fpgapci_dev *fpgapci, struct pci_dev *dev);


//#define kernel_debug

struct ocores_i2c {
    void __iomem *base;
    u32 reg_shift;
    u32 reg_io_width;
    wait_queue_head_t wait;
    //struct i2c_adapter adap;
    struct i2c_msg *msg;
    int pos;
    int nmsgs;
    int state; /* see STATE_ */
    //struct clk *clk;
    int ip_clock_khz;
    int bus_clock_khz;
    void (*setreg)(struct ocores_i2c *i2c, int reg, u8 value);
    u8 (*getreg)(struct ocores_i2c *i2c, int reg);
    u32 timeout;
    struct mutex lock;
};
/* registers */
#define OCI2C_PRELOW        0
#define OCI2C_PREHIGH       1
#define OCI2C_CONTROL       2
#define OCI2C_DATA          3
#define OCI2C_CMD           4 /* write only */
#define OCI2C_STATUS        4 /* read only, same address as OCI2C_CMD */
#define OCI2C_VER           5



#define OCI2C_CTRL_IEN      0x40
#define OCI2C_CTRL_EN       0x80

#define OCI2C_CMD_START     0x91
#define OCI2C_CMD_STOP      0x41
#define OCI2C_CMD_READ      0x21
#define OCI2C_CMD_WRITE     0x11
#define OCI2C_CMD_READ_ACK  0x21
#define OCI2C_CMD_READ_NACK 0x29
#define OCI2C_CMD_IACK      0x01

#define OCI2C_STAT_IF       0x01
#define OCI2C_STAT_TIP      0x02
#define OCI2C_STAT_ARBLOST  0x20
#define OCI2C_STAT_BUSY     0x40
#define OCI2C_STAT_NACK     0x80

/* SR[7:0] - Status register */
#define OCI2C_SR_RXACK  (1 << 7) /* Receive acknowledge from slave Â‘1Â’ = No acknowledge received*/
#define OCI2C_SR_BUSY   (1 << 6) /* Busy, I2C bus busy (as defined by start / stop bits) */
#define OCI2C_SR_AL     (1 << 5) /* Arbitration lost - core lost arbitration */
#define OCI2C_SR_TIP    (1 << 1) /* Transfer in progress */
#define OCI2C_SR_IF     (1 << 0) /* Interrupt flag */

#if 0
#define STATE_DONE      0
#define STATE_START     1
#define STATE_WRITE     2
#define STATE_READ      3
#define STATE_ERROR     4
#else
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
#endif

#define TYPE_OCORES     0
#define TYPE_GRLIB      1

/*I2C_CH1 Offset address from PCIE BAR 0*/
#define OCORES_I2C_BASE     0x00006000
#define OCORES_CH_OFFSET    0x10

#define i2c_bus_controller_numb 1
#define I2C_PCI_MAX_BUS  (16)
#define CLS_I2C_CLOCK_LEGACY   0
#define CLS_I2C_CLOCK_PRESERVE (~0U)

static struct ocores_i2c    opencores_i2c[I2C_PCI_MAX_BUS];
static struct i2c_adapter       i2c_pci_adap[I2C_PCI_MAX_BUS];
static struct mutex i2c_xfer_lock[I2C_PCI_MAX_BUS];

static void oc_setreg_8(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite8(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_16(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite16(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_32(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite32(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_16be(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite16be(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_32be(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite32be(value, i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_8(struct ocores_i2c *i2c, int reg)
{
    return ioread8(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_16(struct ocores_i2c *i2c, int reg)
{
    return ioread16(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_32(struct ocores_i2c *i2c, int reg)
{
    return ioread32(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_16be(struct ocores_i2c *i2c, int reg)
{
    return ioread16be(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_32be(struct ocores_i2c *i2c, int reg)
{
    return ioread32be(i2c->base + (reg << i2c->reg_shift));
}

static inline void oc_setreg(struct ocores_i2c *i2c, int reg, u8 value)
{
    i2c->setreg(i2c, reg, value);
}

static inline u8 oc_getreg(struct ocores_i2c *i2c, int reg)
{
    return i2c->getreg(i2c, reg);
}


static void ocores_dump(struct ocores_i2c *i2c)
//static void __maybe_unused ocores_dump(struct ocores_i2c *i2c)
{
    u8 tmp;

    printk(KERN_DEBUG "Opencores register dump:\n");

    tmp = oc_getreg(i2c, OCI2C_PRELOW);
    printk(KERN_DEBUG "OCI2C_PRELOW (%d) = 0x%x\n",OCI2C_PRELOW,tmp);

    tmp = oc_getreg(i2c, OCI2C_PREHIGH);
    printk(KERN_DEBUG "OCI2C_PREHIGH(%d) = 0x%x\n",OCI2C_PREHIGH,tmp);

    tmp = oc_getreg(i2c, OCI2C_CONTROL);
    printk(KERN_DEBUG "OCI2C_CONTROL(%d) = 0x%x\n",OCI2C_CONTROL,tmp);

    tmp = oc_getreg(i2c, OCI2C_DATA);
    printk(KERN_DEBUG "OCI2C_DATA   (%d) = 0x%x\n",OCI2C_DATA,tmp);

    tmp = oc_getreg(i2c, OCI2C_CMD);
    printk(KERN_DEBUG "OCI2C_CMD    (%d) = 0x%x\n",OCI2C_CMD,tmp);
}

static void ocores_stop(struct ocores_i2c *i2c)
{
    //unsigned long time_out = jiffies + msecs_to_jiffies(i2c->timeout);
    oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_STOP);
}

/*
 * dell_get_mutex must be called prior to calling this function.
 */
static int ocores_poll(struct ocores_i2c *i2c)
{
    u8 stat = oc_getreg(i2c, OCI2C_STATUS);
    struct i2c_msg *msg = i2c->msg;
    u8 addr;

    /* Ready? */
    if (stat & OCI2C_STAT_TIP)
        return -EBUSY;

    if (i2c->state == STATE_DONE || i2c->state == STATE_ERROR) {
        /* Stop has been sent */
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_IACK);
        if (i2c->state == STATE_ERROR)
            return -EIO;
        return 0;
    }

    /* Error? */
    if (stat & OCI2C_STAT_ARBLOST) {
        i2c->state = STATE_ERROR;
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_STOP);
        return -EAGAIN;
    }

    if (i2c->state == STATE_INIT) {
        if (stat & OCI2C_STAT_BUSY)
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

        oc_setreg(i2c, OCI2C_DATA, addr);
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_START);

        return 0;
    }

    /* Second part of 10 bit addressing */
    if (i2c->state == STATE_ADDR10) {
        oc_setreg(i2c, OCI2C_DATA, i2c->msg->addr & 0xff);
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_WRITE);

        i2c->state = STATE_START;
        return 0;
    }

    if (i2c->state == STATE_START || i2c->state == STATE_WRITE) {
        i2c->state = (msg->flags & I2C_M_RD) ? STATE_READ : STATE_WRITE;

        if (stat & OCI2C_STAT_NACK) {
            i2c->state = STATE_ERROR;
            oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_STOP);
            return -ENXIO;
        }
    } else {
        msg->buf[i2c->pos++] = oc_getreg(i2c, OCI2C_DATA);
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
            oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_STOP);
            return 0;
        }
    }

    if (i2c->state == STATE_READ) {
        oc_setreg(i2c, OCI2C_CMD, i2c->pos == (msg->len - 1) ?
                OCI2C_CMD_READ_NACK : OCI2C_CMD_READ_ACK);
    } else {
        oc_setreg(i2c, OCI2C_DATA, msg->buf[i2c->pos++]);
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_WRITE);
    }

    return 0;
}

static void ocores_process(struct ocores_i2c *i2c)
{
    struct i2c_msg *msg = i2c->msg;
    u8 stat = oc_getreg(i2c, OCI2C_STATUS);
    //unsigned long timeout = jiffies + msecs_to_jiffies(1000);

    printk(KERN_DEBUG "ocores_process in. status reg :0x%x\n", stat);
    if ((i2c->state == STATE_DONE) || (i2c->state == STATE_ERROR)) {
        /* stop has been sent */
        printk(KERN_DEBUG "ocores_process OCI2C_CMD_IACK stat = 0x%x Set OCI2C_CMD(0%x) OCI2C_CMD_IACK = 0x%x\n",stat, OCI2C_CMD, OCI2C_CMD_IACK);
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_IACK);
        wake_up(&i2c->wait);
        return;
    }

    /* error? */
    if (stat & OCI2C_STAT_ARBLOST) {
        i2c->state = STATE_ERROR;
        printk(KERN_DEBUG "ocores_process OCI2C_STAT_ARBLOST OCI2C_CMD_STOP\n");
        ocores_stop(i2c);
        return;
    }

    if ((i2c->state == STATE_START) || (i2c->state == STATE_WRITE)) {
        i2c->state =
            (msg->flags & I2C_M_RD) ? STATE_READ : STATE_WRITE;
        printk(KERN_DEBUG "ocores_process i2c->state =%d\n",i2c->state);

        if (stat & OCI2C_STAT_NACK) {
            i2c->state = STATE_ERROR;
            printk(KERN_DEBUG "ocores_process OCI2C_STAT_NACK OCI2C_CMD_STOP\n");
            ocores_stop(i2c);//oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_STOP);
            return;
        }
    } else
    {
        msg->buf[i2c->pos++] = oc_getreg(i2c, OCI2C_DATA);
        printk(KERN_DEBUG "ocores_process oc_getreg OCI2C_DATA(0x%x) msg->buf[%d] = 0x%x\n",OCI2C_DATA, i2c->pos, msg->buf[i2c->pos]);
    }

    /* end of msg? */
    if (i2c->pos == msg->len) {
        i2c->nmsgs--;
        i2c->msg++;
        i2c->pos = 0;
        msg = i2c->msg;

        if (i2c->nmsgs) {   /* end? */
            /* send start? */
            if (!(msg->flags & I2C_M_NOSTART)) {
                //addr = i2c_8bit_addr_from_msg(msg);
                u8 addr = (msg->addr << 1);

                if (msg->flags & I2C_M_RD)
                    addr |= 1;

                i2c->state = STATE_START;
                printk(KERN_DEBUG "Set OCI2C_CMD(0%x) addr = 0x%x\n",OCI2C_CMD, addr);
                oc_setreg(i2c, OCI2C_DATA, addr);
                printk(KERN_DEBUG "Set OCI2C_CMD(0%x) OCI2C_CMD_START = 0x%x\n",OCI2C_CMD, OCI2C_CMD_START);
                oc_setreg(i2c, OCI2C_CMD,  OCI2C_CMD_START);
                return;
            } else
            {
                i2c->state = (msg->flags & I2C_M_RD)
                    ? STATE_READ : STATE_WRITE;
                printk(KERN_DEBUG "ocores_process end i2c->state =%d\n",i2c->state);
            }
        } else {
            i2c->state = STATE_DONE;
            printk(KERN_DEBUG "ocores_process end i2c->state = STATE_DONE ocores_stop\n");
            ocores_stop(i2c);//oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_STOP);
            return;
        }
    }

    if (i2c->state == STATE_READ) {
        printk(KERN_DEBUG "ocores_poll STATE_READ i2c->pos=%d msg->len-1 = 0x%x set OCI2C_CMD = 0x%x\n",i2c->pos, msg->len-1,
                i2c->pos == (msg->len-1) ?  OCI2C_CMD_READ_NACK : OCI2C_CMD_READ_ACK);
        oc_setreg(i2c, OCI2C_CMD, i2c->pos == (msg->len-1) ?
                OCI2C_CMD_READ_NACK : OCI2C_CMD_READ_ACK);
    } else {
        printk(KERN_DEBUG "ocores_process set OCI2C_DATA(0x%x)\n",OCI2C_DATA);
        oc_setreg(i2c, OCI2C_DATA, msg->buf[i2c->pos++]);
        printk(KERN_DEBUG "ocores_process set OCI2C_CMD(0x%x) OCI2C_CMD_WRITE = 0x%x\n",OCI2C_CMD, OCI2C_CMD_WRITE);
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_WRITE);
    }
}

static irqreturn_t ocores_isr(int irq, void *dev_id)
{
    struct ocores_i2c *i2c = dev_id;
    ocores_process(i2c);

    return IRQ_HANDLED;
}
void dell_get_mutex(struct ocores_i2c *i2c)
{
    mutex_lock(&i2c->lock);
}

/**
 * dell_release_mutex - release mutex
 */
void dell_release_mutex(struct ocores_i2c *i2c)
{
    mutex_unlock(&i2c->lock);
}

static int ocores_xfer(struct i2c_adapter *adap, struct i2c_msg *msgs, int num)
{
    struct ocores_i2c *i2c = i2c_get_adapdata(adap);
    unsigned long orig_jiffies;
    int ret;
    unsigned long timeout = jiffies + msecs_to_jiffies(1000);
    //printk("%s(), line:%d\n", __func__, __LINE__);

    i2c->msg = msgs;
    i2c->pos = 0;
    i2c->nmsgs = num;
    i2c->state = (use_irq == 1) ? STATE_START : STATE_INIT;

    //printk(KERN_DEBUG "i2c->msg->addr = 0x%x i2c->msg->flags = 0x%x\n",i2c->msg->addr,i2c->msg->flags);
    //printk(KERN_DEBUG "I2C_M_RD = 0x%x i2c->msg->addr << 1 = 0x%x\n",I2C_M_RD,i2c->msg->addr << 1);

    //ocores_dump(i2c);
    if (!use_irq) {
        /* Handle the transfer */
        while (time_before(jiffies, timeout)) {
            dell_get_mutex(i2c);
            ret = ocores_poll(i2c);
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
        printk(KERN_DEBUG "Set OCI2C_DATA(0%x) val = 0x%x\n",OCI2C_DATA,
                (i2c->msg->addr << 1) | ((i2c->msg->flags & I2C_M_RD) ? 1:0));
        oc_setreg(i2c, OCI2C_DATA,
                (i2c->msg->addr << 1) |
                ((i2c->msg->flags & I2C_M_RD) ? 1:0));
        printk(KERN_DEBUG "Set OCI2C_CMD(0%x) val = 0x%x\n",OCI2C_CMD, OCI2C_CMD_START);
        oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_START);

        /* Interrupt mode */
        if (wait_event_timeout(i2c->wait, (i2c->state == STATE_ERROR) ||
                    (i2c->state == STATE_DONE), HZ))
            return (i2c->state == STATE_DONE) ? num : -EIO;
        else
            return -ETIMEDOUT;
    }
}

static int ocores_init(struct ocores_i2c *i2c)
{
    int prescale;
    int diff;
    u8 ctrl;

    if (i2c->reg_io_width == 0)
        i2c->reg_io_width = 1; /* Set to default value */

    if (!i2c->setreg || !i2c->getreg) {
        bool be = 0; //1:big_endian 0:little_endian

        switch (i2c->reg_io_width) {
            case 1:
                i2c->setreg = oc_setreg_8;
                i2c->getreg = oc_getreg_8;
                break;

            case 2:
                i2c->setreg = be ? oc_setreg_16be : oc_setreg_16;
                i2c->getreg = be ? oc_getreg_16be : oc_getreg_16;
                break;

            case 4:
                i2c->setreg = be ? oc_setreg_32be : oc_setreg_32;
                i2c->getreg = be ? oc_getreg_32be : oc_getreg_32;
                break;

            default:
                printk(KERN_ERR "Unsupported I/O width (%d)\n",
                        i2c->reg_io_width);
                return -EINVAL;
        }
    }

    ctrl = oc_getreg(i2c, OCI2C_CONTROL);
    printk(KERN_DEBUG "%s(), line:%d\n", __func__, __LINE__);
    printk(KERN_DEBUG "i2c->base = 0x%p\n",i2c->base);

    printk(KERN_DEBUG "ctrl = 0x%x\n",ctrl);
    printk(KERN_DEBUG "set ctrl = 0x%x\n",ctrl & ~(OCI2C_CTRL_EN|OCI2C_CTRL_IEN));

    /* make sure the device is disabled */
    oc_setreg(i2c, OCI2C_CONTROL, ctrl & ~(OCI2C_CTRL_EN|OCI2C_CTRL_IEN));

    /*
     *  IÃ‚Â²C Frequency depends on host clock
     *  input clock of 100MHz
     *  prescale to 100MHz / ( 5*100kHz) -1 = 199 = 0x4F 100000/(5*100)-1=199=0xc7
     */
    printk(KERN_DEBUG "calculate prescale\n");
    prescale = (i2c->ip_clock_khz / (5 * i2c->bus_clock_khz)) - 1;
    printk(KERN_DEBUG "calculate prescale = 0x%x\n",prescale);
    prescale = clamp(prescale, 0, 0xffff);
    printk(KERN_DEBUG "calculate clamp prescale = 0x%x\n",prescale);

    diff = i2c->ip_clock_khz / (5 * (prescale + 1)) - i2c->bus_clock_khz;
    printk(KERN_DEBUG "calculate diff = 0x%x\n",diff);
    if (abs(diff) > i2c->bus_clock_khz / 10) {
        printk(KERN_ERR "Unsupported clock settings: core: %d KHz, bus: %d KHz\n",
                i2c->ip_clock_khz, i2c->bus_clock_khz);
        return -EINVAL;
    }

    printk(KERN_DEBUG "OCI2C_PRELOW(%d) set = 0x%x\n",OCI2C_PRELOW,prescale & 0xff);
    oc_setreg(i2c, OCI2C_PRELOW, prescale & 0xff);
    printk(KERN_DEBUG "OCI2C_PRHIGH(%d) set = 0x%x\n",OCI2C_PREHIGH,prescale >> 8);
    oc_setreg(i2c, OCI2C_PREHIGH, prescale >> 8);

    printk(KERN_DEBUG "Init the device\n");
    /* Init the device */
    oc_setreg(i2c, OCI2C_CMD, OCI2C_CMD_IACK);
    printk(KERN_DEBUG "OCI2C_CONTROL(0x%x) set: 0x%x\n", OCI2C_CONTROL, ctrl | OCI2C_CTRL_IEN | OCI2C_CTRL_EN);
    if (!use_irq)
        oc_setreg(i2c, OCI2C_CONTROL, ctrl | OCI2C_CTRL_EN);
    else
        oc_setreg(i2c, OCI2C_CONTROL, ctrl | OCI2C_CTRL_IEN | OCI2C_CTRL_EN);

    //ocores_dump(i2c);

    /* Initialize interrupt handlers if not already done */
    init_waitqueue_head(&i2c->wait);

    return 0;
}


static u32 ocores_func(struct i2c_adapter *adap)
{
    return I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL;
}

static const struct i2c_algorithm ocores_algorithm = {
    .master_xfer = ocores_xfer,
    .functionality = ocores_func,
};

static int  i2c_pci_add_bus (struct i2c_adapter *adap)
{
    int ret = 0;
    /* Register new adapter */
    adap->algo = &ocores_algorithm;
    ret = i2c_add_numbered_adapter(adap);
    return ret;
}

static int i2c_init_internal_data(void)
{
    int i;
    printk(KERN_DEBUG "%s(), line:%d\n", __func__, __LINE__);

    for( i = 0; i < I2C_PCI_MAX_BUS; i++ )
    {
        opencores_i2c[i].reg_shift = 0; /* 8 bit registers */
        opencores_i2c[i].reg_io_width = 1; /* 8 bit read/write */
        opencores_i2c[i].timeout = 1000;//1ms
        opencores_i2c[i].ip_clock_khz = 100000;/* input clock of 100MHz */
        opencores_i2c[i].bus_clock_khz = 100;
        //opencores_i2c[i].base = fpga_base_addr + OCORES_I2C_BASE + i*OCORES_CH_OFFSET;
        opencores_i2c[i].base = fpga_base_addr + i*OCORES_CH_OFFSET;
        mutex_init(&opencores_i2c[i].lock);
        ocores_init(&opencores_i2c[i]);
    }

#if 0
    printk(KERN_DEBUG "FPGA PCIE access test\n");
    writel(0xdeadbeef, fpga_base_addr + 0x04);
    printk(KERN_DEBUG "%s(), fpga_base_addr + 0x8000:0x%x\n", __func__, readl(fpga_base_addr + 0x8000));
    printk(KERN_DEBUG "%s(), SCRTCH_REG:0x%x\n", __func__, readl(fpga_base_addr + 0x04));
#endif
    return 0;
}


static int i2c_pci_init (void)
{
    int i;

    memset (&i2c_pci_adap,      0, sizeof(i2c_pci_adap));
    memset (&opencores_i2c, 0, sizeof(opencores_i2c));
    for(i=0; i < i2c_bus_controller_numb; i++)
        mutex_init(&i2c_xfer_lock[i]);

    /* Initialize driver's itnernal data structures */
    i2c_init_internal_data();

    for (i = 0 ; i < I2C_PCI_MAX_BUS ; i ++) {

        i2c_pci_adap[i].owner = THIS_MODULE;
        i2c_pci_adap[i].class = I2C_CLASS_HWMON | I2C_CLASS_SPD;

        i2c_pci_adap[i].algo_data = &opencores_i2c[i];
        /* /dev/i2c-600 ~ /dev/i2c-600  for Open core I2C channel  controller 1-7  */
        i2c_pci_adap[i].nr = i+600;
        sprintf( i2c_pci_adap[ i ].name, "i2c-pci-%d", i );
        /* Add the bus via the algorithm code */
        if( i2c_pci_add_bus( &i2c_pci_adap[ i ] ) != 0 )
        {
            printk(KERN_ERR "Cannot add bus %d to algorithm layer\n", i );
            return( -ENODEV );
        }
        i2c_set_adapdata(&i2c_pci_adap[i], &opencores_i2c[i]);
        printk( KERN_DEBUG "Registered bus id: %s\n", kobject_name(&i2c_pci_adap[ i ].dev.kobj));
    }

    return 0;
}

static void i2c_pci_deinit(void)
{
    int i;
    for( i = 0; i < I2C_PCI_MAX_BUS; i++ ){
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
        printk (KERN_DEBUG "Device doesn't have an associated bus!\n");
        return 0;
    }

    bridge = bus->self;
    if (bridge == 0) {
        printk (KERN_DEBUG "Can't get the bridge for the bus!\n");
        return 0;
    }

    printk (KERN_DEBUG "Upstream device %x/%x, bus:slot.func %02x:%02x.%02x\n",
            bridge->vendor, bridge->device,
            bridge->bus->number, PCI_SLOT(bridge->devfn), PCI_FUNC(bridge->devfn));

    printk (KERN_DEBUG "List of downstream devices:");
    list_for_each_entry (cur, &bus->devices, bus_list) {
        if (cur != 0) {
            printk (KERN_DEBUG "  %x/%x", cur->vendor, cur->device);
            if (cur == dev) {
                found_dev = 1;
            }
        }
    }
    printk (KERN_DEBUG "\n");
    if (found_dev) {
        return bridge;
    } else {
        printk (KERN_DEBUG "Couldn't find upstream device!\n");
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
            printk (KERN_DEBUG "BAR[%d] 0x%08lx-0x%08lx flags 0x%08lx",
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
            printk ( "BAR #%d length is less than 1 byte\n", i);
            continue;
        }

        //printk ( "bar_start=%llx, bar_end=%llx, bar_length=%lx, flag=%lx\n", bar_start,
        //      bar_end, bar_length, pci_resource_flags(dev, i));

        /* map the device memory or IO region into kernel virtual
         * address space */
        fpgapci->bar[i] = ioremap_nocache (bar_start + OCORES_I2C_BASE, I2C_PCI_MAX_BUS * OCORES_CH_OFFSET);
        if (!fpgapci->bar[i]) {
            printk ( "Could not map BAR #%d.\n", i);
            return -1;
        }

        //printk ( "BAR[%d] mapped at 0x%p with length %lu.", i,
        //      fpgapci->bar[i], bar_length);

        if(i == 0)  //FPGA register is in the BAR[0]
        {
            fpga_phys_addr = bar_start;
            fpga_base_addr = fpgapci->bar[i];
        }

        printk (KERN_DEBUG "BAR[%d] mapped at 0x%p with length %lu.\n", i,
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
static int register_intr_handler(struct pci_dev *dev, int c)
{
    int err = 0;
    struct fpgapci_dev *fpgapci = 0;

    fpgapci = (struct fpgapci_dev*) dev_get_drvdata(&dev->dev);
    if (fpgapci == 0) {
        printk (KERN_ERR ": fpgapci_dev is 0\n");
        return err;
    }


    /* Request interrupt line for unique function
     * alternatively function will be called from free_irq as well with flag IRQF_SHARED */
    switch(c) {
        /*Currently we only support test vector 2 for Open core I2C channel  controller 1-7  interrupt*/
        case 0:
            err = request_irq(dev->irq + c, ocores_isr, IRQF_EARLY_RESUME, FPGA_PCI_NAME, &opencores_i2c[0]);
            fpgapci->irq_assigned++;
            printk(KERN_DEBUG "Interrupt Line %d assigned with return value %d\n", dev->irq + c, err);
            break;

        default:
            printk(KERN_DEBUG "No more interrupt handler for number (%d)\n", dev->irq + c);
            break;
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
    printk(KERN_DEBUG "pos = 0x%x\n", pos);
    if (pos) {
        pci_read_config_word(dev, pos + PCI_MSI_FLAGS, &control);
        maxvec = 1 << ((control & PCI_MSI_FLAGS_QMASK) >> 1);
        printk(KERN_DEBUG "control = 0x%x maxvec = 0x%x\n", control, maxvec);
        control &= ~PCI_MSI_FLAGS_ENABLE;
#if 0
        if (enable)
            control |= PCI_MSI_FLAGS_ENABLE;
#else
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
#endif

        pci_write_config_word(dev, pos + PCI_MSI_FLAGS, control);
    }
}
static void msi_setup_enable(struct pci_dev *dev, int request_private_bits)
{
    int pos,maxvec;
    u16 control;
    int configured_private_bits = 4;

    pos = pci_find_capability(dev, PCI_CAP_ID_MSI);

    /*
     * Read the MSI config to figure out how many IRQs this device
     * wants.  Most devices only want 1, which will give
     * configured_private_bits and request_private_bits equal 0.
     */
    pci_read_config_word(dev, pos + PCI_MSI_FLAGS, &control);

    /*
     * If the number of private bits has been configured then use
     * that value instead of the requested number. This gives the
     * driver the chance to override the number of interrupts
     * before calling pci_enable_msi().
     */
    configured_private_bits = (control & PCI_MSI_FLAGS_QSIZE) >> 4;
    if (configured_private_bits == 0) {
        /* Nothing is configured, so use the hardware requested size */
        request_private_bits = (control & PCI_MSI_FLAGS_QMASK) >> 1;
    }
    else {
        /*
         * Use the number of configured bits, assuming the
         * driver wanted to override the hardware request
         * value.
         */
        request_private_bits = configured_private_bits;
    }

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
/**
 * @brief Enables pcie-device and claims/remaps neccessary bar resources
 * @param dev Pointer to pci-device, which should be allocated
 * @return Returns error code or zero if success
 * */
static int claim_device(struct fpgapci_dev *fpgapci,struct pci_dev *dev)
{
    int err = 0;
    u16 msi_offset;
    u16 mc_val;

    /* wake up the pci device */
    err = pci_enable_device(dev);
    if(err) {
        printk(KERN_ERR "failed to enable pci device %d\n", err);
        goto error_pci_en;
    }

    /* on platforms with buggy ACPI, pdev->msi_enabled may be set to
     * allow pci_enable_device to work. This indicates INTx was not routed
     * and only MSI should be used
     */

    //dev->msi_enabled = 0;
    pci_set_master(dev);

    /* Setup the BAR memory regions */
    err = pci_request_regions(dev, DRIVER_NAME);
    if (err) {
        printk(KERN_ERR "failed to enable pci device %d\n", err);
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
/**
 * @brief Configures pcie-device and bit_mask settings
 * @param dev Pointer to pci-device, which should be allocated
 * @return Returns error code or zero if success
 * */
static int configure_device(struct pci_dev *dev)
{
    return 0;
}


/*
 * Check if the controller supports the interrupt type requested. If it
 * supports returns the offset, otherwise it will return invalid for the
 * caller to indicate that the controller does not support the capability
 * type.
 */
int check_cntlr_cap(struct pci_dev *dev, enum fpga_irq_type cap_type,
        u16 *offset)
{
    u16 val = 0;
    u16 pci_offset = 0;
    int ret_val = -EINVAL;

    if (pci_read_config_word(dev, PCI_DEVICE_STATUS, &val) < 0) {
        printk(KERN_ERR "pci_read_config failed...\n");
        return -EINVAL;
    }
    printk(KERN_DEBUG "PCI_DEVICE_STATUS = 0x%X\n", val);
    if (!(val & CL_MASK)) {
        printk(KERN_ERR "Controller does not support Capability list...\n");
        return -EINVAL;
    } else {
        if (pci_read_config_word(dev, CAP_REG, &pci_offset) < 0) {
            printk(KERN_ERR "pci_read_config failed...\n");
            return -EINVAL;
        }
    }
    printk(KERN_DEBUG "pci_offset = 0x%x\n", pci_offset);
    /* Interrupt Type MSI-X*/
    if (cap_type == INT_MSIX) {
        /* Loop through Capability list */
        while (pci_offset) {//0x40
            if (pci_read_config_word(dev, pci_offset, &val) < 0) {
                printk(KERN_ERR "pci_read_config failed...\n");
                return -EINVAL;
            }
            /* exit when we find MSIX_capbility offset */
            if ((val & ~NEXT_MASK) == MSIXCAP_ID) {
                /* write msix cap offset */
                *offset = pci_offset;
                ret_val = 1;
                /* break from while loop */
                break;
            }
            /* Next Capability offset. */
            pci_offset = (val & NEXT_MASK) >> 8;
        } /* end of while loop */

    } else if (cap_type == INT_MSI_SINGLE || cap_type == INT_MSI_MULTI) {
        /* Loop through Capability list */
        while (pci_offset) {//0x40
            if (pci_read_config_word(dev, pci_offset, &val) < 0) {
                printk(KERN_ERR "pci_read_config failed...\n");
                return -EINVAL;
            }
            printk(KERN_DEBUG "val = 0x%x ~NEXT_MASK= 0x%x val & ~NEXT_MASK = 0x%x\n", val,~NEXT_MASK, val & ~NEXT_MASK);
            /* exit when we find MSIX_capbility offset */
            if ((val & ~NEXT_MASK) == MSICAP_ID) {
                /* write the msi offset */
                *offset = pci_offset;
                ret_val = 1;
                printk(KERN_DEBUG "*offset = 0x%x\n", *offset);
                /* break from while loop */
                break;
            }
            /* Next Capability offset. */
            pci_offset = (val & NEXT_MASK) >> 8;
            printk(KERN_DEBUG "Next Capability offset pci_offset = 0x%x\n", pci_offset);
        } /* end of while loop */

    } else {
        printk(KERN_DEBUG "Invalid capability type specified...\n");
        ret_val = -EINVAL;
    }

    return ret_val;
}

static int claim_msi(struct fpgapci_dev *fpgapci,struct pci_dev *dev)
{
    int err = 0, i;
    int nvec, request_vec;
    u16 msi_offset;
    u16 mc_val;

    /* set up MSI interrupt vector to max size */
    nvec = pci_msi_vec_count(dev);
    printk(KERN_DEBUG "Have %d MSI vectors\n", nvec);
#if 0
#if (LINUX_VERSION_CODE >= KERNEL_VERSION(3, 16, 0))// || defined(WITH_BACKPORTS)
    err = pci_enable_msi_range(dev, nvec, nvec);
#else
    err = pci_enable_msi_block(dev, nvec + 1);
#endif
#endif
    printk(KERN_DEBUG "Check MSI capability\n");
    /* Check if the card Supports MSI capability */
    if (check_cntlr_cap(dev, INT_MSI_MULTI, &msi_offset) < 0) {
        printk(KERN_ERR "Controller does not support for MSI capability!!\n");
        return -EINVAL;
    }
    /* compute MSI MC offset if MSI is supported */
    printk(KERN_DEBUG "check_cntlr_cap return msi_offset = 0x%x\n", msi_offset);
    msi_offset += 2;
    printk(KERN_DEBUG "msi_offset = 0x%x\n", msi_offset);
    /* Read MSI-MC value */
    pci_read_config_word(dev, msi_offset, &mc_val);
    printk(KERN_DEBUG "read msi_offset(0x%x) mc_val  = 0x%x\n", msi_offset, mc_val);
    printk(KERN_DEBUG "(1 << ((mc_val & MSI_MME) >> 4)) = 0x%x\n",(1 << ((mc_val & MSI_MME) >> 4)));
    if (nvec > (1 << ((mc_val & MSI_MME) >> 4))) { // power 2
        printk(KERN_DEBUG "IRQs = %d exceed MSI MME = %d\n", nvec,
                (1 << ((mc_val & MSI_MME) >> 4)));
        /* does not support the requested irq's*/
    }
    msi_set_enable(dev,1);
    printk(KERN_DEBUG "Check MSI capability after msi_set_enable\n");

    /* Check if the card Supports MSI capability */
    if (check_cntlr_cap(dev, INT_MSI_MULTI, &msi_offset) < 0) {
        printk(KERN_DEBUG "Controller does not support for MSI capability!!\n");
        return -EINVAL;
    }
    /* compute MSI MC offset if MSI is supported */
    printk(KERN_DEBUG "check_cntlr_cap return msi_offset = 0x%x\n", msi_offset);
    msi_offset += 2;
    printk(KERN_DEBUG "msi_offset = 0x%x\n", msi_offset);
    /* Read MSI-MC value */
    pci_read_config_word(dev, msi_offset, &mc_val);
    printk(KERN_DEBUG "read msi_offset(0x%x) mc_val  = 0x%x\n", msi_offset, mc_val);

    printk(KERN_DEBUG "(1 << ((mc_val & MSI_MME) >> 4)) = 0x%x\n",(1 << ((mc_val & MSI_MME) >> 4)));
    if (nvec > (1 << ((mc_val & MSI_MME) >> 4))) { // power 2
        printk(KERN_DEBUG "IRQs = %d exceed MSI MME = %d\n", nvec,
                (1 << ((mc_val & MSI_MME) >> 4)));
        /* does not support the requested irq's*/
    }

    /*Above 4.1.12*/
#if 1
    request_vec = 1;
    err = pci_alloc_irq_vectors(dev, request_vec, pci_msi_vec_count(dev),
            PCI_IRQ_MSI);//PCI_IRQ_AFFINITY | PCI_IRQ_MSI);
#endif

    if (err <= 0) {
        printk(KERN_ERR "Cannot set MSI vector (%d)\n", err);
        goto error_no_msi;
    } else {
        printk(KERN_ERR  "Got %d MSI vectors starting at %d\n", err, dev->irq);
    }
    fpgapci->irq_first = dev->irq;
    fpgapci->irq_length = err;
    fpgapci->irq_assigned = 0;


    for(i = 0; i < fpgapci->irq_length; i++) {
        err = register_intr_handler(dev, i);
        if (err) {
            printk(KERN_ERR "Cannot request Interrupt number %d\n", i);
            goto error_pci_req_irq;
        }
    }

    return 0;

error_pci_req_irq:
    //for(i = i-1; i >= 0; i--)
    free_irq(fpgapci->irq_first + 0, &opencores_i2c[0]);
    pci_disable_msi(fpgapci->pci_dev);
error_no_msi:
    return -ENOSPC;
}

static int fpgapci_probe(struct pci_dev *dev, const struct pci_device_id *id)
{
    struct fpgapci_dev *fpgapci = 0;

    printk (KERN_DEBUG " vendor = 0x%x, device = 0x%x, class = 0x%x, bus:slot.func = %02x:%02x.%02x\n",
            dev->vendor, dev->device, dev->class,
            dev->bus->number, PCI_SLOT(dev->devfn), PCI_FUNC(dev->devfn));

    fpgapci = kzalloc(sizeof(struct fpgapci_dev), GFP_KERNEL);

    if (!fpgapci) {
        printk(KERN_ERR "Couldn't allocate memory!\n");
        goto fail_kzalloc;
    }

    fpgapci->pci_dev = dev;
    dev_set_drvdata(&dev->dev, (void*)fpgapci);

    fpgapci->upstream = find_upstream_dev (dev);

    if(claim_device(fpgapci,dev)) {
        goto error_no_device;
    }

    if(configure_device(dev)) {
        goto error_cannot_configure;
    }
    if (use_irq) {
        if(claim_msi(fpgapci,dev)) {
            goto error_cannot_configure;
        }
    }


    return 0;
    /* ERROR HANDLING */
error_cannot_configure:
    printk(KERN_ERR "error_cannot_configure\n");
    free_bars (fpgapci, dev);
    pci_release_regions(dev);
    pci_disable_device(dev);
error_no_device:
    i2c_pci_deinit();
    printk(KERN_ERR "error_no_device\n");
fail_kzalloc:
    return -1;
}

static void fpgapci_remove(struct pci_dev *dev)
{
    struct fpgapci_dev *fpgapci = 0;
    //int i;
    printk (KERN_DEBUG ": dev is %p\n", dev);

    if (dev == 0) {
        printk (KERN_ERR ": dev is 0\n");
        return;
    }

    fpgapci = (struct fpgapci_dev*) dev_get_drvdata(&dev->dev);
    if (fpgapci == 0) {
        printk (KERN_ERR ": fpgapci_dev is 0\n");
        return;
    }
    i2c_pci_deinit();
    if (use_irq)
        free_irq(fpgapci->irq_first + 0, &opencores_i2c[0]);
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
        printk(KERN_DEBUG "pci_unregister_driver\n");
        pci_unregister_driver(&fpgapci_driver);
        return -ENODEV;
    }

    return 0;
}

static void __exit fpgapci_exit(void)
{
    printk (KERN_DEBUG "fpgapci_exit");
    /* unregister this driver from the PCI bus driver */
    pci_unregister_driver(&fpgapci_driver);

}


module_init (fpgapci_init);
module_exit (fpgapci_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Joyce_Yu@Dell.com");
MODULE_DESCRIPTION ("Driver for FPGA Opencores I2C bus");
MODULE_SUPPORTED_DEVICE ("FPGA Opencores I2C bus");


