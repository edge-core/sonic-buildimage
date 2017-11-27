#include <linux/device.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sysfs.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/dmi.h>
#include <linux/version.h>
#include <linux/ctype.h>
#include <linux/platform_device.h>
#include <linux/i2c.h>
#include <linux/i2c/pca954x.h>
#include <linux/i2c-mux.h>
#include <linux/i2c-mux-gpio.h>
#include <linux/i2c/sff-8436.h>

#define BUS3_DEV_NUM 9
#define BUS4_DEV_NUM 6
#define BUS5_DEV_NUM 32
#define DEFAULT_NUM  1
#define BUS3_BASE_NUM 30
#define BUS4_BASE_NUM 40
#define BUS5_BASE_NUM 50

#define BUS3_MUX_REG 0x21
#define BUS4_MUX_REG 0x21
#define BUS5_MUX_REG 0x20

#define TEMP_FAN_VAL  0x06
#define FANIO_CTL_VAL 0x07
#define FAN_CTRL_VAL  0x05
#define PSU1_VAL      0x00
#define PSU2_VAL      0x20
#define HOT_SWAP1_VAL 0x10
#define HOT_SWAP2_VAL 0x30
#define FAN_EEPROM1_VAL   0x00
#define FAN_EEPROM2_VAL   0x01
#define FAN_EEPROM3_VAL   0x02
#define FAN_EEPROM4_VAL   0x03
#define FAN_EEPROM5_VAL   0x04

#define SWPLD_REG         0x31
#define SWPLD_SFP_MUX_REG 0x20

#define SYS_LED_REG      0x1C
#define FAN1_LED_REG     0x1D
#define FAN2_LED_REG     0x1E

#define SFP_PRESENCE_1    0x38
#define SFP_PRESENCE_2    0x39
#define SFP_PRESENCE_3    0x3A
#define SFP_PRESENCE_4    0x3B

#define SFP_LP_MODE_1     0x34
#define SFP_LP_MODE_2     0x35
#define SFP_LP_MODE_3     0x36
#define SFP_LP_MODE_4     0x37

#define SFP_RESET_1       0x3C
#define SFP_RESET_2       0x3D
#define SFP_RESET_3       0x3E
#define SFP_RESET_4       0x3F

#define SFP_RESPONSE_1    0x30
#define SFP_RESPONSE_2    0x31
#define SFP_RESPONSE_3    0x32
#define SFP_RESPONSE_4    0x33

#define SFF8436_INFO(data) \
    .type = "sff8436", .addr = 0x50, .platform_data = (data)

#define SFF_8346_PORT(eedata) \
    .byte_len = 256, .page_size = 1, .flags = SFF_8436_FLAG_READONLY
	
#define ag9032v1_i2c_device_num(NUM){                                         \
        .name                   = "delta-ag9032v1-i2c-device",                \
        .id                     = NUM,                                        \
        .dev                    = {                                           \
                    .platform_data = &ag9032v1_i2c_device_platform_data[NUM], \
                    .release       = device_release,                          \
        },                                                                    \
}

/*Define struct to get client of i2c_new_deivce */
struct i2c_client * i2c_client_9547;

enum{
    BUS0 = 0,
    BUS1,
    BUS2,
    BUS3,
    BUS4,
    BUS5,
    BUS6,
    BUS7,
};

unsigned char reverse_8bits(unsigned char c)
{
        unsigned char s = 0;
        int i;
        for (i = 0; i < 8; ++i) {
                s <<= 1;
                s |= c & 1;
                c >>= 1;
        }
        return s;
}
/*----------------   I2C device   - start   ------------- */
static void device_release(struct device *dev)
{
    return;
}

struct i2c_device_platform_data {
    int parent;
    struct i2c_board_info           info;
    struct i2c_client              *client;
};
/* pca9547 - add 8 bus */
static struct pca954x_platform_mode pca954x_mode[] = {
  { .adap_id = 2,
    .deselect_on_exit = 1,
  },
  { .adap_id = 3,
    .deselect_on_exit = 1,
  },
  { .adap_id = 4,
    .deselect_on_exit = 1,
  },
  { .adap_id = 5,
    .deselect_on_exit = 1,
  },
  { .adap_id = 6,
    .deselect_on_exit = 1,
  },
  { .adap_id = 7,
    .deselect_on_exit = 1,
  },
  { .adap_id = 8,
    .deselect_on_exit = 1,
  },
  { .adap_id = 9,
    .deselect_on_exit = 1,
  },
};

static struct pca954x_platform_data pca954x_data = {
  .modes = pca954x_mode,
  .num_modes = ARRAY_SIZE(pca954x_mode),
};

static struct i2c_board_info __initdata i2c_info_pca9547[] =
{
        {
            I2C_BOARD_INFO("pca9547", 0x71),
            .platform_data = &pca954x_data, 
        },
};


static struct sff_8436_platform_data sff_8436_port[] = {
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
    { SFF_8346_PORT() },
};

static struct i2c_device_platform_data ag9032v1_i2c_device_platform_data[] = {
    {
        /* tmp75 (0x4d) */
        .parent = 2,
        .info = { I2C_BOARD_INFO("tmp75", 0x4d) },
        .client = NULL,
    },
    {
        /* id eeprom (0x53) */
        .parent = 2,
        .info = { I2C_BOARD_INFO("24c02", 0x53) },
        .client = NULL,
    },
    {
        /* tmp75 (0x4c) */
        .parent = 7,
        .info = { I2C_BOARD_INFO("tmp75", 0x4c) },
        .client = NULL,
    },
    {
        /* tmp75 (0x4d) */
        .parent = 7,
        .info = { I2C_BOARD_INFO("tmp75", 0x4d) },
        .client = NULL,
    },
    {
        /* tmp75 (0x4e) */
        .parent = 7,
        .info = { I2C_BOARD_INFO("tmp75", 0x4e) },
        .client = NULL,
    },
    { 
        /* tmp75 (0x4f) */
        .parent = 30, 
        .info = { I2C_BOARD_INFO("tmp75", 0x4f) },
        .client = NULL,
    },
    { 
        /* FAN 1 Controller (0x2c) */
        .parent = 37, 
        .info = { I2C_BOARD_INFO("emc2305", 0x2c) },
        .client = NULL,
    },
    { 
        /* FAN 2 Controller (0x2d) */
        .parent = 38, 
        .info = { I2C_BOARD_INFO("emc2305", 0x2d) },
        .client = NULL,
    },
    {
        /* psu 1 (0x58) */
        .parent = 40,
        .info = { .type = "dni_ag9032v1_psu", .addr = 0x58, .platform_data = 0 },
        .client = NULL,
    },
    {
        /* psu 2 (0x58) */
        .parent = 41,
        .info = { .type = "dni_ag9032v1_psu", .addr = 0x58, .platform_data = 1 },
        .client = NULL,
    },
    {
        /* hot-swap 1 (0x40) */
        .parent = 42,
        .info = { .type = "ltc4215", .addr = 0x40, .platform_data = 0 },
        .client = NULL,
    },
    {
        /* hot-swap 2 (0x40) */
        .parent = 43,
        .info = { .type = "ltc4215", .addr = 0x40, .platform_data = 1 },
        .client = NULL,
    },
    {
        /* qsfp 1 (0x50) */
        .parent = 50,
        .info = { SFF8436_INFO(&sff_8436_port[0]) },
        .client = NULL,
    },
    {
        /* qsfp 2 (0x50) */
        .parent = 51,
        .info = { SFF8436_INFO(&sff_8436_port[1]) },
        .client = NULL,
    },
    {
        /* qsfp 3 (0x50) */
        .parent = 52,
        .info = { SFF8436_INFO(&sff_8436_port[2]) },
        .client = NULL,
    },
    {
        /* qsfp 4 (0x50) */
        .parent = 53,
        .info = { SFF8436_INFO(&sff_8436_port[3]) },
        .client = NULL,
    },
    {
        /* qsfp 5 (0x50) */
        .parent = 54,
        .info = { SFF8436_INFO(&sff_8436_port[4]) },
        .client = NULL,
    },
    {
        /* qsfp 6 (0x50) */
        .parent = 55,
        .info = { SFF8436_INFO(&sff_8436_port[5]) },
        .client = NULL,
    },
    {
        /* qsfp 7 (0x50) */
        .parent = 56,
        .info = { SFF8436_INFO(&sff_8436_port[6]) },
        .client = NULL,
    },
    {
        /* qsfp 8 (0x50) */
        .parent = 57,
        .info = { SFF8436_INFO(&sff_8436_port[7]) },
        .client = NULL,
    },
    {
        /* qsfp 9 (0x50) */
        .parent = 58,
        .info = { SFF8436_INFO(&sff_8436_port[8]) },
        .client = NULL,
    },
    {
        /* qsfp 10 (0x50) */
        .parent = 59,
        .info = { SFF8436_INFO(&sff_8436_port[9]) },
        .client = NULL,
    },
    {
        /* qsfp 11 (0x50) */
        .parent = 60,
        .info = { SFF8436_INFO(&sff_8436_port[10]) },
        .client = NULL,
    },
    {
        /* qsfp 12 (0x50) */
        .parent = 61,
        .info = { SFF8436_INFO(&sff_8436_port[11]) },
        .client = NULL,
    },
    {
        /* qsfp 13 (0x50) */
        .parent = 62,
        .info = { SFF8436_INFO(&sff_8436_port[12]) },
        .client = NULL,
    },
    {
        /* qsfp 14 (0x50) */
        .parent = 63,
        .info = { SFF8436_INFO(&sff_8436_port[13]) },
        .client = NULL,
    },
    {
        /* qsfp 15 (0x50) */
        .parent = 64,
        .info = { SFF8436_INFO(&sff_8436_port[14]) },
        .client = NULL,
    },
    {
        /* qsfp 16 (0x50) */
        .parent = 65,
        .info = { SFF8436_INFO(&sff_8436_port[15]) },
        .client = NULL,
    },
    {
        /* qsfp 17 (0x50) */
        .parent = 66,
        .info = { SFF8436_INFO(&sff_8436_port[16]) },
        .client = NULL,
    },
    {
        /* qsfp 18 (0x50) */
        .parent = 67,
        .info = { SFF8436_INFO(&sff_8436_port[17]) },
        .client = NULL,
    },
    {
        /* qsfp 19 (0x50) */
        .parent = 68,
        .info = { SFF8436_INFO(&sff_8436_port[18]) },
        .client = NULL,
    },
    {
        /* qsfp 20 (0x50) */
        .parent = 69,
        .info = { SFF8436_INFO(&sff_8436_port[19]) },
        .client = NULL,
    },
    {
        /* qsfp 21 (0x50) */
        .parent = 70,
        .info = { SFF8436_INFO(&sff_8436_port[20]) },
        .client = NULL,
    },
    {
        /* qsfp 22 (0x50) */
        .parent = 71,
        .info = { SFF8436_INFO(&sff_8436_port[21]) },
        .client = NULL,
    },
    {
        /* qsfp 23 (0x50) */
        .parent = 72,
        .info = { SFF8436_INFO(&sff_8436_port[22]) },
        .client = NULL,
    },
    {
        /* qsfp 24 (0x50) */
        .parent = 73,
        .info = { SFF8436_INFO(&sff_8436_port[23]) },
        .client = NULL,
    },
    {
        /* qsfp 25 (0x50) */
        .parent = 74,
        .info = { SFF8436_INFO(&sff_8436_port[24]) },
        .client = NULL,
    },
    {
        /* qsfp 26 (0x50) */
        .parent = 75,
        .info = { SFF8436_INFO(&sff_8436_port[25]) },
        .client = NULL,
    },
    {
        /* qsfp 27 (0x50) */
        .parent = 76,
        .info = { SFF8436_INFO(&sff_8436_port[26]) },
        .client = NULL,
    },
    {
        /* qsfp 28 (0x50) */
        .parent = 77,
        .info = { SFF8436_INFO(&sff_8436_port[27]) },
        .client = NULL,
    },
    {
        /* qsfp 29 (0x50) */
        .parent = 78,
        .info = { SFF8436_INFO(&sff_8436_port[28]) },
        .client = NULL,
    },
    {
        /* qsfp 30 (0x50) */
        .parent = 79,
        .info = { SFF8436_INFO(&sff_8436_port[29]) },
        .client = NULL,
    },
    {
        /* qsfp 31 (0x50) */
        .parent = 80,
        .info = { SFF8436_INFO(&sff_8436_port[30]) },
        .client = NULL,
    },
    {
        /* qsfp 32 (0x50) */
        .parent = 81,
        .info = { SFF8436_INFO(&sff_8436_port[31]) },
        .client = NULL,
    },
};


static struct platform_device ag9032v1_i2c_device[] = {
    ag9032v1_i2c_device_num(0),
    ag9032v1_i2c_device_num(1),
    ag9032v1_i2c_device_num(2),
    ag9032v1_i2c_device_num(3),
    ag9032v1_i2c_device_num(4),
    ag9032v1_i2c_device_num(5),
    ag9032v1_i2c_device_num(6),
    ag9032v1_i2c_device_num(7),
    ag9032v1_i2c_device_num(8),
    ag9032v1_i2c_device_num(9),
    ag9032v1_i2c_device_num(10),
    ag9032v1_i2c_device_num(11),
    ag9032v1_i2c_device_num(12),
    ag9032v1_i2c_device_num(13),
    ag9032v1_i2c_device_num(14),
    ag9032v1_i2c_device_num(15),
    ag9032v1_i2c_device_num(16),
    ag9032v1_i2c_device_num(17),
    ag9032v1_i2c_device_num(18),
    ag9032v1_i2c_device_num(19),
    ag9032v1_i2c_device_num(20),
    ag9032v1_i2c_device_num(21),
    ag9032v1_i2c_device_num(22),
    ag9032v1_i2c_device_num(23),
    ag9032v1_i2c_device_num(24),
    ag9032v1_i2c_device_num(25),
    ag9032v1_i2c_device_num(26),
    ag9032v1_i2c_device_num(27),
    ag9032v1_i2c_device_num(28),
    ag9032v1_i2c_device_num(29),
    ag9032v1_i2c_device_num(30),
    ag9032v1_i2c_device_num(31),
    ag9032v1_i2c_device_num(32),
    ag9032v1_i2c_device_num(33),
    ag9032v1_i2c_device_num(34),
    ag9032v1_i2c_device_num(35),
    ag9032v1_i2c_device_num(36),
    ag9032v1_i2c_device_num(37),
    ag9032v1_i2c_device_num(38),
    ag9032v1_i2c_device_num(39),
    ag9032v1_i2c_device_num(40),
    ag9032v1_i2c_device_num(41),
    ag9032v1_i2c_device_num(42),
    ag9032v1_i2c_device_num(43),
};

/*----------------   I2C device   - end   ------------- */

/*----------------   I2C driver   - start   ------------- */
static int __init i2c_device_probe(struct platform_device *pdev)
{
    struct i2c_device_platform_data *pdata;
    struct i2c_adapter *parent;

    pdata = pdev->dev.platform_data;
    if (!pdata) {
        dev_err(&pdev->dev, "Missing platform data\n");
        return -ENODEV;
    }

    parent = i2c_get_adapter(pdata->parent);
    if (!parent) {
        dev_err(&pdev->dev, "Parent adapter (%d) not found\n",
            pdata->parent);
        return -ENODEV;
    }

    pdata->client = i2c_new_device(parent, &pdata->info);
    if (!pdata->client) {
        dev_err(&pdev->dev, "Failed to create i2c client %s at %d\n",
            pdata->info.type, pdata->parent);
        return -ENODEV;
    }

    return 0;
}

static int __exit i2c_deivce_remove(struct platform_device *pdev)
{
    struct i2c_adapter *parent;
    struct i2c_device_platform_data *pdata;

    pdata = pdev->dev.platform_data;
    if (!pdata) {
        dev_err(&pdev->dev, "Missing platform data\n");
        return -ENODEV;
    }

    if (pdata->client) {
        parent = i2c_get_adapter(pdata->parent);
        i2c_unregister_device(pdata->client);
        i2c_put_adapter(parent);
    }

    return 0;
}
static struct platform_driver i2c_device_driver = {
    .probe = i2c_device_probe,
    .remove = __exit_p(i2c_deivce_remove),
    .driver = {
        .owner = THIS_MODULE,
        .name = "delta-ag9032v1-i2c-device",
    }
};

/*----------------   I2C driver   - end   ------------- */

/*----------------    CPLD - start   ------------- */

/*    CPLD  -- device   */

enum cpld_type {
    system_cpld,
};

struct cpld_platform_data {
    int reg_addr;
    struct i2c_client *client;
};

static struct cpld_platform_data ag9032v1_cpld_platform_data[] = {
    [system_cpld] = {
        .reg_addr = SWPLD_REG,
    },
};

static struct platform_device ag9032v1_cpld = {
    .name               = "delta-ag9032v1-cpld",
    .id                 = 0,
    .dev                = {
                .platform_data   = ag9032v1_cpld_platform_data,
                .release         = device_release
    },
};

static ssize_t get_present(struct device *dev, struct device_attribute \
                            *dev_attr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_PRESENCE_1);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data = (u32)reverse_8bits(ret) & 0xff;
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_PRESENCE_2);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 8;
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_PRESENCE_3);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 16;
        
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_PRESENCE_4);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 24;
        
    return sprintf(buf, "0x%08x\n", data); //return 32bits data
}

static ssize_t get_lpmode(struct device *dev, struct device_attribute *devattr, char *buf) 
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_LP_MODE_1);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data = (u32)(reverse_8bits(ret) & 0xff);
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_LP_MODE_2);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 8;
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_LP_MODE_3);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 16;
        
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_LP_MODE_4);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 24;
        
    return sprintf(buf, "0x%08x\n", data); //return 32bits data
}

static ssize_t set_lpmode(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count) 
{
    unsigned long data;
    int err;
    struct cpld_platform_data *pdata = dev->platform_data;

    err = kstrtoul(buf, 16, &data);
    if (err)
        return err;
    
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_LP_MODE_1, (u8)reverse_8bits(data & 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_LP_MODE_2, (u8)(reverse_8bits(data >> 8) & 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_LP_MODE_3, (u8)(reverse_8bits(data >> 16) & 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_LP_MODE_4, (u8)(reverse_8bits(data >> 24) & 0xff));

    return count;
}

static ssize_t get_reset(struct device *dev, struct device_attribute *devattr, char *buf) 
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESET_1);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data = (u32)(reverse_8bits(ret) & 0xff);
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESET_2);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 8;
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESET_3);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 16;
        
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESET_4);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 24;
 
    return sprintf(buf, "0x%08x\n", data); //return 32bits data
}

static ssize_t set_reset(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count) 
{
    unsigned long data;
    int err;
    struct cpld_platform_data *pdata = dev->platform_data;

    err = kstrtoul(buf, 16, &data);
    if (err)
        return err;

    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESET_1, (u8)reverse_8bits(data & 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESET_2, (u8)reverse_8bits((data >> 8)& 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESET_3, (u8)reverse_8bits((data >> 16) & 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESET_4, (u8)reverse_8bits((data >> 24) & 0xff));

    return count;
}

static ssize_t get_response(struct device *dev, struct device_attribute *devattr, char *buf) 
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESPONSE_1);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data = (u32)(reverse_8bits(ret) & 0xff);
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESPONSE_2);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 8;
 
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESPONSE_3);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 16;
        
    ret = i2c_smbus_read_byte_data(pdata[system_cpld].client, SFP_RESPONSE_4);
    if (ret < 0)
        return sprintf(buf, "error number(%ld)",ret);
    data |= (u32)(reverse_8bits(ret) & 0xff) << 24;
 
    return sprintf(buf, "0x%08x\n", data); //return 32bits data
}

static ssize_t set_response(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count) 
{
    unsigned long data;
    int err;
    struct cpld_platform_data *pdata = dev->platform_data;

    err = kstrtoul(buf, 16, &data);
    if (err)
        return err;

    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESPONSE_1, (u8)reverse_8bits(data & 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESPONSE_2, (u8)reverse_8bits((data >> 8)& 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESPONSE_3, (u8)reverse_8bits((data >> 16) & 0xff));
    i2c_smbus_write_byte_data(pdata[system_cpld].client, SFP_RESPONSE_4, (u8)reverse_8bits((data >> 24) & 0xff));

    return count;
}
	
struct platform_led_status{
	int reg_data;
	char *led_status;
	int led_id;
};
	
static struct platform_led_status led_info[] = {
    {
		.reg_data = 0x40,
		.led_status = "pwr1_green",
		.led_id = 0,
	},
	{
		.reg_data = 0x80,
		.led_status = "pwr1_amber",
		.led_id = 0,
	},
	{
		.reg_data = 0x00,
		.led_status = "pwr1_off",
		.led_id = 0,
	},
	{
		.reg_data = 0xc0,
		.led_status = "pwr1_off",
		.led_id = 0,
	},
    {
		.reg_data = 0x10,
		.led_status = "pwr2_green",
		.led_id = 1,
	},
	{
		.reg_data = 0x20,
		.led_status = "pwr2_amber",
		.led_id = 1,
	},
	{
		.reg_data = 0x00,
		.led_status = "pwr2_off",
		.led_id = 1,
	},
	{
		.reg_data = 0x30,
		.led_status = "pwr2_off",
		.led_id = 1,
	},
	{
		.reg_data = 0x04,               
		.led_status = "sys_green",
		.led_id = 2,
	},
	{
		.reg_data = 0x08,
		.led_status = "sys_blinking_green",
		.led_id = 2,
	},
	{
		.reg_data = 0x0c,
		.led_status = "sys_red",
		.led_id = 2,
	},
	{
		.reg_data = 0x00,
		.led_status = "sys_off",
		.led_id = 2,
	},	
	{
		.reg_data = 0x01, 
		.led_status = "fan_green",
		.led_id = 3,
	},
	{
		.reg_data = 0x02,
		.led_status = "fan_amber",
		.led_id = 3,
	},
	{
		.reg_data = 0x00,
		.led_status = "fan_off",
		.led_id = 3,
	},
	{
		.reg_data = 0x03,
		.led_status = "fan_off",
		.led_id = 3,
	},
	{
		.reg_data = 0x40,
		.led_status = "fan1_green",
		.led_id = 4,
	},
	{
		.reg_data = 0x80,
		.led_status = "fan1_red",
		.led_id = 4,
	},
	{
		.reg_data = 0x00,
		.led_status = "fan1_off",
		.led_id = 4,
	},
	{
		.reg_data = 0x10,
		.led_status = "fan2_green",
		.led_id = 5,
	},
	{
		.reg_data = 0x20,
		.led_status = "fan2_red",
		.led_id = 5,
	},
	{
		.reg_data = 0x00,
		.led_status = "fan2_off",
		.led_id = 5,
	},	
	{
		.reg_data = 0x04,
		.led_status = "fan3_green",
	    .led_id = 6,
	},
	{
		.reg_data = 0x08,
		.led_status = "fan3_red",
		.led_id = 6,
	},
	{
		.reg_data = 0x00,
		.led_status = "fan3_off",
		.led_id = 6,
	},
	{
		.reg_data = 0x01,
		.led_status = "fan4_green",
		.led_id = 7,
	},
	{
		.reg_data = 0x02,
		.led_status = "fan4_red",
		.led_id = 7,
	},
	{
		.reg_data = 0x00,
		.led_status = "fan4_off",
		.led_id = 7,
	},
	{
		.reg_data = 0x40,
		.led_status = "fan5_green",
		.led_id = 8,
	},
	{
		.reg_data = 0x80,
		.led_status = "fan5_red",
		.led_id = 8,
	},
	{
		.reg_data = 0x00,
		.led_status = "fan5_off",
		.led_id = 8,
	},
};
	
struct platform_led_data{
	int reg_addr;	
	int mask;		
};
	
static struct platform_led_data led_data[] = {	
	{
		.reg_addr = SYS_LED_REG,
		.mask = 0xc0,		
	},
	{
		.reg_addr = SYS_LED_REG,
        .mask = 0x30,		
	},
	{
		.reg_addr = SYS_LED_REG,
        .mask = 0x0c,		
	},
	{
		.reg_addr = SYS_LED_REG,
        .mask = 0x03,
	},
	{
		.reg_addr = FAN1_LED_REG,
        .mask = 0xc0,		
	},
	{
		.reg_addr = FAN1_LED_REG,
        .mask = 0x30,		
	},
	{
		.reg_addr = FAN1_LED_REG,
        .mask = 0x0c,		
	},	
	{
		.reg_addr = FAN1_LED_REG,
        .mask = 0x03,		
	},
	{
    	.reg_addr = FAN2_LED_REG,
        .mask = 0xc0,		
	},
};
	

static ssize_t get_led_color(struct device *dev, struct device_attribute *devattr, char *buf)
{
    char str[9][20] = {0};
    int board_data;
	int led_data_number;
	int led_info_number;
    struct cpld_platform_data *pdata = dev->platform_data;
	
	for(led_data_number = 0; led_data_number < ARRAY_SIZE(led_data); led_data_number++){	
        board_data = i2c_smbus_read_byte_data(pdata[system_cpld].client, led_data[led_data_number].reg_addr);	
		if(board_data >= 0){
		    board_data &= led_data[led_data_number].mask;		
		    for(led_info_number = 0; led_info_number < ARRAY_SIZE(led_info); led_info_number++){
	            if (led_data_number == led_info[led_info_number].led_id){
                    if(board_data == led_info[led_info_number].reg_data){					
	                sprintf(str[led_data_number], "%s", led_info[led_info_number].led_status);
				    }
			    }		
		    }
		}
		else
			printk( KERN_ERR "Missing LED board data\n");
	}		    		
	return sprintf(buf,"%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n",str[0],str[1],str[2],str[3],str[4],str[5],str[6],str[7],str[8]);
}

static ssize_t set_led_color(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
	int led_info_number;
	int led_data_number;
	int str_compar;
	int led_reg_value;
    struct cpld_platform_data *pdata = dev->platform_data;
		
	for(led_info_number = 0; led_info_number < ARRAY_SIZE(led_info); led_info_number++){
		str_compar = strncmp(buf,led_info[led_info_number].led_status,strlen(led_info[led_info_number].led_status));
		if(str_compar == 0){									
			for(led_data_number = 0; led_data_number < ARRAY_SIZE(led_data); led_data_number++){				
			    if(led_info[led_info_number].led_id == led_data_number){
					led_reg_value = i2c_smbus_read_byte_data(pdata[system_cpld].client, led_data[led_data_number].reg_addr);
                    if(led_reg_value >= 0){					
			            led_reg_value &= (~led_data[led_data_number].mask);					
				        led_reg_value |= led_info[led_info_number].reg_data;					
					    i2c_smbus_write_byte_data(pdata[system_cpld].client, (u8)(led_data[led_data_number].reg_addr & 0xff), (u8)(led_reg_value & 0xff));
					}
					else
						printk( KERN_ERR "Missing LED reg. data\n");
				}
		    }
		}
	}
    return count;
}


static DEVICE_ATTR(sfp_present,  S_IRUGO,           get_present,   NULL         );
static DEVICE_ATTR(sfp_lpmode,   S_IWUSR | S_IRUGO, get_lpmode,    set_lpmode   );
static DEVICE_ATTR(sfp_reset,    S_IWUSR | S_IRUGO, get_reset,     set_reset    );
static DEVICE_ATTR(sfp_response, S_IWUSR | S_IRUGO, get_response,  set_response );
static DEVICE_ATTR(led_control,  S_IRUGO | S_IWUSR, get_led_color, set_led_color);

static struct attribute *ag9032v1_cpld_attrs[] = {
    &dev_attr_sfp_response.attr,    
    &dev_attr_sfp_present.attr,
    &dev_attr_sfp_lpmode.attr,
    &dev_attr_sfp_reset.attr,
    &dev_attr_led_control.attr,
    NULL,
};

static struct attribute_group ag9032v1_cpld_attr_grp = {
    .attrs = ag9032v1_cpld_attrs,
};

/*    CPLD  -- driver   */
static int __init cpld_probe(struct platform_device *pdev)
{
    struct cpld_platform_data *pdata;
    struct i2c_adapter *parent;
    int ret;
    pdata = pdev->dev.platform_data;
    if (!pdata) {
        dev_err(&pdev->dev, "CPLD platform data not found\n");
        return -ENODEV;
    }

    parent = i2c_get_adapter(BUS6);
    if (!parent) {
        printk(KERN_WARNING "Parent adapter (%d) not found\n",BUS6);
        return -ENODEV;
    }

    pdata[system_cpld].client = i2c_new_dummy(parent, pdata[system_cpld].reg_addr);
    if (!pdata[system_cpld].client) {
        printk(KERN_WARNING "Fail to create dummy i2c client for addr %d\n", pdata[system_cpld].reg_addr);
        goto error;
    }

    ret = sysfs_create_group(&pdev->dev.kobj, &ag9032v1_cpld_attr_grp);
   if (ret) {
        printk(KERN_WARNING "Fail to create cpld attribute group");
        goto error;
   }

    return 0;

error:    
    i2c_unregister_device(pdata[system_cpld].client);
    i2c_put_adapter(parent);
    
    return -ENODEV; 
}

static int __exit cpld_remove(struct platform_device *pdev)
{
    struct i2c_adapter *parent = NULL;
    struct cpld_platform_data *pdata = pdev->dev.platform_data;
    sysfs_remove_group(&pdev->dev.kobj, &ag9032v1_cpld_attr_grp);

    if (!pdata) {
        dev_err(&pdev->dev, "Missing platform data\n");
    } 
    else {
        if (pdata[system_cpld].client) {
            if (!parent) {
                parent = (pdata[system_cpld].client)->adapter;
            }
        i2c_unregister_device(pdata[system_cpld].client);
        }
    }
    i2c_put_adapter(parent);

    return 0;
}

static struct platform_driver cpld_driver = {
    .probe  = cpld_probe,
    .remove = __exit_p(cpld_remove),
    .driver = {
        .owner  = THIS_MODULE,
        .name   = "delta-ag9032v1-cpld",
    },
};

/*----------------    CPLD  - end   ------------- */

/*----------------    MUX   - start   ------------- */

struct swpld_mux_platform_data {
    int parent;
    int base_nr;
    int reg_addr;
    struct i2c_client *cpld;
};

struct swpld_mux {
    struct i2c_adapter *parent;
    struct i2c_adapter **child;
    struct swpld_mux_platform_data data;
};
static struct swpld_mux_platform_data ag9032v1_swpld_mux_platform_data[] = {
    {
        .parent         = BUS3, 
        .base_nr        = BUS3_BASE_NUM, 
        .cpld           = NULL,
        .reg_addr       = BUS3_MUX_REG ,// the i2c register address which for select mux TEMP(FAN)
    },
    {
        .parent         = BUS4,
        .base_nr        = BUS4_BASE_NUM ,
        .cpld           = NULL,
        .reg_addr       = BUS4_MUX_REG ,
    },
    {
        .parent         = BUS5,
        .base_nr        = BUS5_BASE_NUM ,
        .cpld           = NULL,
        .reg_addr       = BUS5_MUX_REG ,
    },
};

static struct platform_device ag9032v1_swpld_mux[] = {
    {
        .name           = "delta-ag9032v1-swpld-mux",
        .id             = 0,
        .dev            = {
                .platform_data   = &ag9032v1_swpld_mux_platform_data[0],
                .release         = device_release,
        },
    },
    {
        .name           = "delta-ag9032v1-swpld-mux",
        .id             = 1,
        .dev            = {
                .platform_data   = &ag9032v1_swpld_mux_platform_data[1],
                .release         = device_release,
        },
    },
    {
        .name           = "delta-ag9032v1-swpld-mux",
        .id             = 2,
        .dev            = {
                .platform_data   = &ag9032v1_swpld_mux_platform_data[2],
                .release         = device_release,
        },
    },
};

static int cpld_reg_write_byte(struct i2c_client *client, u8 regaddr, u8 val)
{
    union i2c_smbus_data data;

    data.byte = val;
    return client->adapter->algo->smbus_xfer(client->adapter, client->addr,
                                             client->flags,
                                             I2C_SMBUS_WRITE,
                                             regaddr, I2C_SMBUS_BYTE_DATA, &data);
}

static int swpld_mux_select(struct i2c_adapter *adap, void *data, u8 chan)
{
    struct swpld_mux *mux = data;
    u8 swpld_mux_val=0; 

    if ( mux->data.base_nr == BUS3_BASE_NUM )
    {
        switch (chan) {  
            case 0:
                swpld_mux_val = TEMP_FAN_VAL;
                break;
            case 1:
                swpld_mux_val = FAN_EEPROM1_VAL;
                break;
            case 2:
                swpld_mux_val = FAN_EEPROM2_VAL;
                break;
            case 3:
                swpld_mux_val = FAN_EEPROM3_VAL;
                break;
            case 4:
                swpld_mux_val = FAN_EEPROM4_VAL;
                break;
            case 5:
                swpld_mux_val = FAN_EEPROM5_VAL;
                break;
            case 6:
                swpld_mux_val = FANIO_CTL_VAL;
                break;
            case 7:
            case 8:
                swpld_mux_val = FAN_CTRL_VAL; 
                break;
        }
    }
    else if ( mux->data.base_nr == BUS4_BASE_NUM )
    {
        switch (chan) {
            case 0:
                swpld_mux_val = PSU1_VAL;
                break;
            case 1:
                swpld_mux_val = PSU2_VAL;
                break;
            case 2:
                swpld_mux_val = HOT_SWAP1_VAL; 
                break;
            case 3:
                swpld_mux_val = HOT_SWAP2_VAL;  
                break;
        }
    }
    else if ( mux->data.base_nr == BUS5_BASE_NUM ){
        if (chan < 9){
            swpld_mux_val = (u8)(chan) + 0x01;
        }
        else if (8 < chan && chan < 19){
            swpld_mux_val = (u8)(chan - 9) + 0x10;
        }
        else if (18 < chan && chan < 29){
            swpld_mux_val = (u8)(chan - 19) + 0x20;
        }
        else if (28 < chan && chan < 39){
            swpld_mux_val = (u8)(chan - 29) + 0x30;
        }
        else{
            swpld_mux_val = 0x00;
        }
    }
    else
    {
        swpld_mux_val = 0x00;
    }
    return cpld_reg_write_byte(mux->data.cpld, mux->data.reg_addr, (u8)(swpld_mux_val & 0xff));
}

static int __init swpld_mux_probe(struct platform_device *pdev)
{
    struct swpld_mux *mux;
    struct swpld_mux_platform_data *pdata;
    struct i2c_adapter *parent;
    int i, ret, dev_num;

    pdata = pdev->dev.platform_data;
    if (!pdata) {
        dev_err(&pdev->dev, "SWPLD platform data not found\n");
        return -ENODEV;
    }

    parent = i2c_get_adapter(pdata->parent);
    if (!parent) {
        dev_err(&pdev->dev, "Parent adapter (%d) not found\n", pdata->parent);
        return -ENODEV;
    }
    /* Judge bus number to decide how many devices*/
    switch (pdata->parent) {
        case BUS3:
            dev_num = BUS3_DEV_NUM;
            break;
        case BUS4:
            dev_num = BUS4_DEV_NUM;
            break;
        case BUS5:
            dev_num = BUS5_DEV_NUM; 
            break;
        default :
            dev_num = DEFAULT_NUM;  
            break;
    }

    mux = kzalloc(sizeof(*mux), GFP_KERNEL);
    if (!mux) {
        ret = -ENOMEM;
        printk(KERN_ERR "Failed to allocate memory for mux\n");
        goto alloc_failed;
    }

    mux->parent = parent;
    mux->data = *pdata;
    mux->child = kzalloc(sizeof(struct i2c_adapter *) * dev_num, GFP_KERNEL);
    if (!mux->child) {
        ret = -ENOMEM;
        printk(KERN_ERR "Failed to allocate memory for device on mux\n");
        goto alloc_failed2;
    }

    for (i = 0; i < dev_num; i++) {
        int nr = pdata->base_nr + i;
        unsigned int class = 0;

        mux->child[i] = i2c_add_mux_adapter(parent, &pdev->dev, mux,
                           nr, i, class,
                           swpld_mux_select, NULL);
        if (!mux->child[i]) {
            ret = -ENODEV;
            dev_err(&pdev->dev, "Failed to add adapter %d\n", i);
            goto add_adapter_failed;
        }
    }

    platform_set_drvdata(pdev, mux);
    return 0;

add_adapter_failed:
    for (; i > 0; i--)
        i2c_del_mux_adapter(mux->child[i - 1]);
    kfree(mux->child);
alloc_failed2:
    kfree(mux);
alloc_failed:
    i2c_put_adapter(parent);

    return ret;
}


static int __exit swpld_mux_remove(struct platform_device *pdev)
{
    int i;
    struct swpld_mux *mux = platform_get_drvdata(pdev);
    struct swpld_mux_platform_data *pdata;
    struct i2c_adapter *parent;
    int dev_num;

    pdata = pdev->dev.platform_data;
    if (!pdata) {
        dev_err(&pdev->dev, "SWPLD platform data not found\n");
        return -ENODEV;
    }

    parent = i2c_get_adapter(pdata->parent);
    if (!parent) {
        dev_err(&pdev->dev, "Parent adapter (%d) not found\n",
            pdata->parent);
        return -ENODEV;
    }
    switch (pdata->parent) {
        case BUS3:
            dev_num = BUS3_DEV_NUM;
            break;
        case BUS4:
            dev_num = BUS4_DEV_NUM;
            break;
        case BUS5:
            dev_num = BUS5_DEV_NUM; 
            break;
        default :
            dev_num = DEFAULT_NUM;  
            break;
    }

    for (i = 0; i < dev_num; i++)
        i2c_del_mux_adapter(mux->child[i]);

    platform_set_drvdata(pdev, NULL);
    i2c_put_adapter(mux->parent);
    kfree(mux->child);
    kfree(mux);

    return 0;
}

static struct platform_driver swpld_mux_driver = {
    .probe  = swpld_mux_probe,
    .remove = __exit_p(swpld_mux_remove), /* TODO */
    .driver = {
        .owner  = THIS_MODULE,
        .name   = "delta-ag9032v1-swpld-mux",
    },
};
/*----------------    MUX   - end   ------------- */

/*----------------   module initialization     ------------- */
static void __init delta_ag9032v1_platform_init(void)
{
    struct i2c_client *client;
    struct i2c_adapter *adapter;
    struct cpld_platform_data *cpld_pdata;
    struct swpld_mux_platform_data *swpld_pdata;
    int ret,i = 0;
    printk("ag9032v1_platform module initialization\n");
    
    //Use pca9547 in i2c_mux_pca954x.c
    adapter = i2c_get_adapter(BUS1); 
    //client = i2c_new_device(adapter, &i2c_info_pca9547[0]);
    i2c_client_9547 = i2c_new_device(adapter, &i2c_info_pca9547[0]);
	
    i2c_put_adapter(adapter);

    // set the CPLD prob and  remove
    ret = platform_driver_register(&cpld_driver);
    if (ret) {
        printk(KERN_WARNING "Fail to register cpld driver\n");
        goto error_cpld_driver;
    }
    // register the mux prob which call the CPLD
    ret = platform_driver_register(&swpld_mux_driver);
    if (ret) {
        printk(KERN_WARNING "Fail to register swpld mux driver\n");
        goto error_swpld_mux_driver;
    }

    // register the i2c devices    
    ret = platform_driver_register(&i2c_device_driver);
    if (ret) {
        printk(KERN_WARNING "Fail to register i2c device driver\n");
        goto error_i2c_device_driver;
    }

    // register the CPLD
    ret = platform_device_register(&ag9032v1_cpld);
    if (ret) {
        printk(KERN_WARNING "Fail to create cpld device\n");
        goto error_ag9032v1_cpld;
    }
    // link the CPLD and the Mux
    cpld_pdata = ag9032v1_cpld.dev.platform_data;

    for (i = 0; i < ARRAY_SIZE(ag9032v1_swpld_mux); i++)
    {
        swpld_pdata = ag9032v1_swpld_mux[i].dev.platform_data;
        swpld_pdata->cpld = cpld_pdata[system_cpld].client;  
        ret = platform_device_register(&ag9032v1_swpld_mux[i]);          
        if (ret) {
            printk(KERN_WARNING "Fail to create swpld mux %d\n", i);
            goto error_ag9032v1_swpld_mux;
        }
    }

    for (i = 0; i < ARRAY_SIZE(ag9032v1_i2c_device); i++)
    {
        ret = platform_device_register(&ag9032v1_i2c_device[i]);
        if (ret) {
            printk(KERN_WARNING "Fail to create i2c device %d\n", i);
            goto error_ag9032v1_i2c_device;
        }
    }

    if (ret)
        goto error_ag9032v1_swpld_mux;

    return 0;

error_ag9032v1_i2c_device:
    i--;
    for (; i >= 0; i--) {
        platform_device_unregister(&ag9032v1_i2c_device[i]);
    }
    i = ARRAY_SIZE(ag9032v1_swpld_mux);    
error_ag9032v1_swpld_mux:
    i--;
    for (; i >= 0; i--) {
        platform_device_unregister(&ag9032v1_swpld_mux[i]);
    }
    platform_driver_unregister(&ag9032v1_cpld);
error_ag9032v1_cpld:
    platform_driver_unregister(&i2c_device_driver);
error_i2c_device_driver:
    platform_driver_unregister(&swpld_mux_driver);
error_swpld_mux_driver:
    platform_driver_unregister(&cpld_driver);
error_cpld_driver:
    return ret;
}

static void __exit delta_ag9032v1_platform_exit(void)
{
    int i = 0;

    for ( i = 0; i < ARRAY_SIZE(ag9032v1_i2c_device); i++ ) {
        platform_device_unregister(&ag9032v1_i2c_device[i]);
    }

    for (i = 0; i < ARRAY_SIZE(ag9032v1_swpld_mux); i++) {
        platform_device_unregister(&ag9032v1_swpld_mux[i]);
    }

    platform_device_unregister(&ag9032v1_cpld);
    platform_driver_unregister(&i2c_device_driver);
    platform_driver_unregister(&cpld_driver);
    platform_driver_unregister(&swpld_mux_driver);

    i2c_unregister_device(i2c_client_9547);
}

module_init(delta_ag9032v1_platform_init);
module_exit(delta_ag9032v1_platform_exit);

MODULE_DESCRIPTION("DNI ag9032v1 Platform Support");
MODULE_AUTHOR("Neal Tai <neal.tai@deltaww.com>");
MODULE_LICENSE("GPL");    
