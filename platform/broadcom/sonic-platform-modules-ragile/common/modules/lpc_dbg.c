#include <linux/version.h>
#if LINUX_VERSION_CODE > KERNEL_VERSION(4, 19, 0)
#include <linux/uaccess.h>
#endif

#include <asm/uaccess.h>
#include <linux/kernel.h> /* Wd're doing kernel work */
#include <linux/module.h> /* specifically, a module */
#include <linux/types.h>
#include <linux/init.h>   /* Need for the macros */
#include <linux/moduleparam.h>
#include <linux/fs.h>
#include <linux/ioport.h>
#include <linux/io.h>
#include <linux/pci.h>
#include <linux/sched.h>
#include <net/sock.h>
#include <net/genetlink.h>
#include <linux/netlink.h>
#include <linux/miscdevice.h>
#include "lpc_dbg.h"

typedef struct rg_lpc_device_s {
    u16 base;
    u16 size;
    u8  type;
    u8  id;
    u8  lpc_pci_addr;
} rg_lpc_device_t;

typedef enum rg_lpc_dev_type_s {
    LPC_DEVICE_CPLD         = 1,
    LPC_DEVICE_FPGA         = 2,
} rg_lpc_dev_type_t;

#define MAX_LPC_DEV_NUM                 (4)
#define LPC_PCI_CFG_BASE(__lgir)        ((0x84) + ((__lgir) * 4))
#define MAX_CPLD_REG_SIZE               (0x100)
#define MAX_FPGA_REG_SIZE               (0x100) //#  fix compile actual value  0x10000
#define LPC_GET_CPLD_ID(addr)           ((addr >> 16) & 0xff)
#define LPC_GET_CPLD_OFFSET(addr)       ((addr) & 0xff)

int lpc_dbg_verbose = 0;
int lpc_dbg_error = 0;
int lpc_dbg_info = 0;
module_param(lpc_dbg_verbose, int, S_IRUGO | S_IWUSR);
module_param(lpc_dbg_error, int, S_IRUGO | S_IWUSR);
module_param(lpc_dbg_info, int, S_IRUGO | S_IWUSR);


#define LPC_DBG_VERBOSE(fmt, args...) do {                                        \
    if (lpc_dbg_verbose) { \
        printk(KERN_ERR "[LPC_DBG][VERBOSE][func:%s line:%d]\r\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

#define LPC_DBG_ERROR(fmt, args...) do {                                        \
    if (lpc_dbg_error) { \
        printk(KERN_ERR "[LPC_DBG][ERROR][func:%s line:%d]\r\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

#define LPC_DBG_INFO(fmt, args...) do {                                        \
    if (lpc_dbg_info) { \
        printk(KERN_ERR ""fmt, ## args); \
    } \
} while (0)

static rg_lpc_device_t g_rg_lpc_dev_default[] = {
    {.base = 0x700, .size = MAX_CPLD_REG_SIZE, .type = LPC_DEVICE_CPLD, .id = 0, .lpc_pci_addr = 0x84},
    {.base = 0x900, .size = MAX_CPLD_REG_SIZE, .type = LPC_DEVICE_CPLD, .id = 1, .lpc_pci_addr = 0x88},
    {.base = 0xb00, .size = MAX_CPLD_REG_SIZE, .type = LPC_DEVICE_CPLD, .id = 2, .lpc_pci_addr = 0x90},
};

static rg_lpc_device_t *g_rg_lpc_dev = g_rg_lpc_dev_default;

static rg_lpc_device_t* lpc_get_device_info(int type, int id)
{
    int i;
    int size;

    size = ARRAY_SIZE(g_rg_lpc_dev_default);
    for (i = 0; i < size; i++) {
        if ((g_rg_lpc_dev[i].type == type) && (g_rg_lpc_dev[i].id == id)) {
            return &g_rg_lpc_dev[i];
        }
    }

    return NULL;
}


int lpc_cpld_read(int address, u8 *val)
{
    int cpld_id;
    rg_lpc_device_t *info;

    cpld_id = LPC_GET_CPLD_ID(address);
    info = lpc_get_device_info(LPC_DEVICE_CPLD, cpld_id);
    if (info == NULL) {
        LPC_DBG_ERROR("lpc_get_device_info addr 0x%x id %d failed.\r\n", address, cpld_id);
        return -1;
    }

    *val = inb(info->base + LPC_GET_CPLD_OFFSET(address));
    LPC_DBG_VERBOSE("Leave info->base 0x%x, addr 0x%x, cpld_id %d, val 0x%x.\r\n", info->base, address, cpld_id, *val);
    return 0;
}

int lpc_cpld_write(int address, u8 reg_val)
{
    int cpld_id;
    rg_lpc_device_t *info;

    cpld_id = LPC_GET_CPLD_ID(address);
    info = lpc_get_device_info(LPC_DEVICE_CPLD, cpld_id);
    if (info == NULL) {
        LPC_DBG_ERROR("lpc_get_device_info addr 0x%x id %d failed.\r\n", address, cpld_id);
        return -1;
    }

    outb(reg_val, info->base + LPC_GET_CPLD_OFFSET(address));
    LPC_DBG_VERBOSE("Leave info->base 0x%x, addr 0x%x, cpld_id %d, val 0x%x.\r\n", info->base, address, cpld_id, reg_val);
    return 0;
}

int lpc_fpga_read(int address, u8 *val)
{
    return -1;
}

int lpc_fpga_write(int address, u8 reg_val)
{
    return -1;
}

static ssize_t lpc_misc_cpld_dev_read (struct file *file, char __user *buf, size_t count,
        loff_t *offset)
{
    int ret;
    u8 value8[MAX_CPLD_REG_SIZE];
    int i;

    if ((count > MAX_CPLD_REG_SIZE)
            || ((LPC_GET_CPLD_OFFSET(file->f_pos) + count) > MAX_CPLD_REG_SIZE)) {
        return -EFAULT;
    }

    for (i = 0; i < count; i++) {
        ret = lpc_cpld_read((int)(file->f_pos + i), &value8[i]);
        if (ret) {
            LPC_DBG_ERROR("lpc_cpld_read i %d addr 0x%x failed ret %d.\n",
                    i, ((unsigned int)file->f_pos + i), ret);
            return i;
        }
    }

    if (copy_to_user(buf, value8, count)) {
        return -EFAULT;
    }

    return count;
}


static ssize_t lpc_misc_cpld_dev_write (struct file *file, const char __user *buf, size_t count,
        loff_t *offset)
{
    u8 value8[MAX_CPLD_REG_SIZE];
    int i;
    int ret;

    if ((count > MAX_CPLD_REG_SIZE)
            || ((LPC_GET_CPLD_OFFSET(file->f_pos) + count) > MAX_CPLD_REG_SIZE)) {
        return -EFAULT;
    }

    if (copy_from_user(value8, buf, count)) {
        return -EFAULT;
    }

    for (i = 0; i < count; i++) {
        ret = lpc_cpld_write((int)(file->f_pos + i), value8[i]);
        if (ret) {
            LPC_DBG_ERROR("lpc_cpld_write i %d addr 0x%x value 0x%x failed ret %d.\n",
                    i, (unsigned int)file->f_pos + i, value8[i], ret);
            return i;
        }
    }

    return count;
}


static loff_t lpc_misc_cpld_dev_llseek(struct file *file, loff_t offset, int origin)
{
    loff_t ret;

#if LINUX_VERSION_CODE < KERNEL_VERSION(4,0,36)
    mutex_lock(&file->f_path.dentry->d_inode->i_mutex);
#else
    /*  do noting add tjm */
    inode_lock(file_inode(file));
#endif

    switch (origin) {
        case 0:
            file->f_pos = offset;
            ret = file->f_pos;
            break;
        case 1:
            file->f_pos += offset;
            ret = file->f_pos;
            break;
        default:
            ret = -EINVAL;
    }

#if LINUX_VERSION_CODE < KERNEL_VERSION(4,0,36)
    mutex_unlock(&file->f_path.dentry->d_inode->i_mutex);
#else
    /*  do noting add tjm */
    inode_unlock(file_inode(file));
#endif


    return ret;
}


static long lpc_misc_cpld_dev_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    return -1;
}

static int lpc_misc_cpld_dev_open(struct inode *inode, struct file *file)
{
    file->private_data = NULL;
    file->f_pos = 0;
    return 0;

}

static int lpc_misc_cpld_dev_release(struct inode *inode, struct file *file)
{
    file->private_data = NULL;
    file->f_pos = 0;
    return 0;
}

static const struct file_operations lpc_misc_cpld_dev_fops = {
    .owner      = THIS_MODULE,
    .llseek     = lpc_misc_cpld_dev_llseek,
    .read       = lpc_misc_cpld_dev_read,
    .write      = lpc_misc_cpld_dev_write,
    .unlocked_ioctl = lpc_misc_cpld_dev_ioctl,
    .open       = lpc_misc_cpld_dev_open,
    .release    = lpc_misc_cpld_dev_release,
};

static ssize_t lpc_misc_fpga_dev_read (struct file *file, char __user *buf, size_t count,
        loff_t *offset)
{
    int ret;
    u8 value8[MAX_FPGA_REG_SIZE];
    int i;

    if ((count > MAX_FPGA_REG_SIZE) || ((file->f_pos + count) > MAX_FPGA_REG_SIZE)) {
        return -EFAULT;
    }

    for (i = 0; i < count; i++) {
        ret = lpc_fpga_read((int)(file->f_pos + i), &value8[i]);
        if (ret) {
            LPC_DBG_ERROR("lpc_fpga_read i %d addr 0x%x failed ret %d.\n",
                    i, ((unsigned int)file->f_pos + i), ret);
            return i;
        }

    }

    if (copy_to_user(buf, value8, count)) {
        return -EFAULT;
    }

    return count;
}


static ssize_t lpc_misc_fpga_dev_write (struct file *file, const char __user *buf, size_t count,
        loff_t *offset)
{
    int ret;
    u8 value8[MAX_FPGA_REG_SIZE];
    int i;

    if ((count > MAX_FPGA_REG_SIZE) || ((file->f_pos + count) > MAX_FPGA_REG_SIZE)) {
        return -EFAULT;
    }

    if (copy_from_user(value8, buf, count)) {
        return -EFAULT;
    }

    for (i = 0; i < count; i++) {
        ret = lpc_fpga_write((int)(file->f_pos + i), value8[i]);
        if (ret) {
            LPC_DBG_ERROR("lpc_fpga_write i %d addr 0x%x value 0x%x failed ret %d.\n",
                    i, (int)(file->f_pos + i), value8[i], ret);
            return i;
        }
    }

    return count;
}


static loff_t lpc_misc_fpga_dev_llseek(struct file *file, loff_t offset, int origin)
{
    loff_t ret;

#if LINUX_VERSION_CODE < KERNEL_VERSION(4,0,36)
    mutex_lock(&file->f_path.dentry->d_inode->i_mutex);
#else
    /*  do noting add tjm */
    inode_lock(file_inode(file));
#endif

    switch (origin) {
        case 0:
            file->f_pos = offset;
            ret = file->f_pos;
            break;
        case 1:
            file->f_pos += offset;
            ret = file->f_pos;
            break;
        default:
            ret = -EINVAL;
    }

#if LINUX_VERSION_CODE < KERNEL_VERSION(4,0,36)
    mutex_unlock(&file->f_path.dentry->d_inode->i_mutex);
#else
    /*  do noting add tjm */
    inode_unlock(file_inode(file));
#endif


    return ret;
}


static long lpc_misc_fpga_dev_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    return -1;
}

static int lpc_misc_fpga_dev_open(struct inode *inode, struct file *file)
{
    file->private_data = NULL;
    file->f_pos = 0;
    return 0;

}

static int lpc_misc_fpga_dev_release(struct inode *inode, struct file *file)
{
    file->private_data = NULL;
    file->f_pos = 0;
    return 0;
}

static const struct file_operations lpc_misc_fpga_dev_fops = {
    .owner      = THIS_MODULE,
    .llseek     = lpc_misc_fpga_dev_llseek,
    .read       = lpc_misc_fpga_dev_read,
    .write      = lpc_misc_fpga_dev_write,
    .unlocked_ioctl = lpc_misc_fpga_dev_ioctl,
    .open       = lpc_misc_fpga_dev_open,
    .release    = lpc_misc_fpga_dev_release,
};

static struct miscdevice lpc_misc_cpld_dev = {
    .minor  = MISC_DYNAMIC_MINOR,
    .name   = "lpc_cpld",
    .fops   = &lpc_misc_cpld_dev_fops,
};

static struct miscdevice lpc_misc_fpga_dev = {
    .minor  = MISC_DYNAMIC_MINOR,
    .name   = "lpc_fpga",
    .fops   = &lpc_misc_fpga_dev_fops,
};

static int lpc_misc_drv_init(void)
{
    if (misc_register(&lpc_misc_cpld_dev) != 0) {
        LPC_DBG_ERROR("Register %s failed.\r\n", lpc_misc_cpld_dev.name);
        return -ENXIO;
    }

    if (misc_register(&lpc_misc_fpga_dev) != 0) {
        LPC_DBG_ERROR("Register %s failed.\r\n", lpc_misc_fpga_dev.name);
        return -ENXIO;
    }
    return 0;
}

static void lpc_misc_drv_exit(void)
{
    misc_deregister(&lpc_misc_cpld_dev);
    misc_deregister(&lpc_misc_fpga_dev);
}

#define LPC_MAKE_PCI_IO_RANGE(__base)      ((0xfc0001) | ((__base) & (0xFFFC)))

static int lpc_pci_cfg_init(struct pci_dev *pdev,
        const struct pci_device_id *id)
{
    int i;
    int size;

    size = ARRAY_SIZE(g_rg_lpc_dev_default);

    for (i = 0; i < size; i++) {
        pci_write_config_dword(pdev, g_rg_lpc_dev[i].lpc_pci_addr, LPC_MAKE_PCI_IO_RANGE(g_rg_lpc_dev[i].base));
        LPC_DBG_VERBOSE("set lpc pci cfg[addr: 0x%x, value:0x%x].\n", LPC_PCI_CFG_BASE(i), LPC_MAKE_PCI_IO_RANGE(g_rg_lpc_dev[i].base));
        if (!request_region(g_rg_lpc_dev[i].base, g_rg_lpc_dev[i].size, "rg_lpc")) {
            LPC_DBG_ERROR("request_region [0x%x][0x%x] failed!\n", g_rg_lpc_dev[i].base, g_rg_lpc_dev[i].size);
            return -EBUSY;
        }
    }

    return 0;
}

static void lpc_pci_cfg_exit(void)
{
    int i;
    int size;

    size = ARRAY_SIZE(g_rg_lpc_dev_default);
    for (i = 0; i < size; i++) {
        release_region(g_rg_lpc_dev[i].base, g_rg_lpc_dev[i].size);
    }
    return;
}

static int rg_lpc_cpld_probe(struct pci_dev *pdev,
        const struct pci_device_id *id)
{
    int ret;

    LPC_DBG_VERBOSE("Enter.\n");
    ret = lpc_pci_cfg_init(pdev, id);
    if (ret) {
        LPC_DBG_ERROR("lpc_pci_cfg_init failed ret %d.\n", ret);
        return ret;
    }

    ret = lpc_misc_drv_init();
    if (ret) {
        LPC_DBG_ERROR("lpc_misc_drv_init failed ret %d.\n", ret);
        return ret;
    }
    LPC_DBG_VERBOSE("Leave success\n");

    return 0;
}

static void rg_lpc_cpld_remove(struct pci_dev *pdev)
{
    LPC_DBG_VERBOSE("Enter.\n");
    lpc_misc_drv_exit();
    lpc_pci_cfg_exit();
    LPC_DBG_VERBOSE("Leave.\n");
}


#define PCI_VENDOR_ID_D1527_LPC             (0x8c54)
#define PCI_VENDOR_ID_C3000_LPC             (0x19dc)

#if 0
static const struct pci_device_id rg_lpc_cpld_pcidev_id[] = {
    { PCI_DEVICE(PCI_VENDOR_ID_INTEL, PCI_VENDOR_ID_C3000_LPC) },
    { PCI_DEVICE(PCI_VENDOR_ID_INTEL, PCI_VENDOR_ID_D1527_LPC) },
    { 0, }
};
MODULE_DEVICE_TABLE(pci, rg_lpc_cpld_pcidev_id);

static struct pci_driver rg_lpc_driver = {
    .name = "rg_lpc",
    .id_table = rg_lpc_cpld_pcidev_id,
    .probe = rg_lpc_cpld_probe,
    .remove = rg_lpc_cpld_remove,
};

module_pci_driver(rg_lpc_driver);
#else
static int __init lpc_dbg_init(void)
{
    struct pci_dev *pdev = NULL;
    int ret;

    LPC_DBG_VERBOSE("Enter.\n");

    pdev = pci_get_device(PCI_VENDOR_ID_INTEL, PCI_VENDOR_ID_D1527_LPC, pdev);
    if (!pdev) {
        LPC_DBG_ERROR("pci_get_device(0x8086, 0x8c54) failed!\n");
        return 0;
    }

    ret = rg_lpc_cpld_probe(pdev, NULL);
    LPC_DBG_VERBOSE("Leave ret %d.\n", ret);
    return ret;
}

static void __exit lpc_dbg_exit(void)
{
    LPC_DBG_VERBOSE("Enter.\n");
    rg_lpc_cpld_remove(NULL);
    LPC_DBG_VERBOSE("Leave.\n");
}



module_init(lpc_dbg_init);
module_exit(lpc_dbg_exit);

#endif
MODULE_LICENSE("GPL");
MODULE_AUTHOR("support <support@ragile.com>");

