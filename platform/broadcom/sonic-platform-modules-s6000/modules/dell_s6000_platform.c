#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sysfs.h>
#include <linux/slab.h>
#include <linux/stat.h>
#include <linux/i2c.h>
#include <linux/i2c-mux.h>
#include <linux/i2c-mux-gpio.h>
#include <linux/platform_device.h>
#include <linux/i2c/sff-8436.h>
#include <linux/delay.h>

#define S6000_MUX_BASE_NR   10
#define QSFP_MODULE_BASE_NR 20

/* 74CBTLV3253 Dual 1-of-4 multiplexer/demultiplexer */
#define MUX_CHANNEL_NUM     2

#define CPLD_DEVICE_NUM     3
#define QSFP_MODULE_NUM     16
#define QSFP_DEVICE_NUM     2

#define SFF8436_INFO(data) \
    .type = "sff8436", .addr = 0x50, .platform_data = (data)

#define SFF_8346_PORT(eedata) \
    .byte_len = 128, .page_size = 1, .flags = SFF_8436_FLAG_READONLY

static void device_release(struct device *dev)
{
    return;
}

/*
 * S6000 74CBTLV3253 MUX
 */
static const unsigned s6000_mux_gpios[] = {
    1, 2
};

static const unsigned s6000_mux_values[] = {
    0, 1, 2, 3
};

static struct i2c_mux_gpio_platform_data s6000_mux_platform_data = {
    .parent             = 2,
    .base_nr            = S6000_MUX_BASE_NR,
    .values             = s6000_mux_values,
    .n_values           = ARRAY_SIZE(s6000_mux_values),
    .gpios              = s6000_mux_gpios,
    .n_gpios            = ARRAY_SIZE(s6000_mux_gpios),
    .idle               = 0,
};

static struct platform_device s6000_mux = {
    .name               = "i2c-mux-gpio",
    .id                 = 0,
    .dev                = {
                .platform_data   = &s6000_mux_platform_data,
                .release          = device_release
    },
};

/*
 * S6000 CPLD
 */

enum cpld_type {
    system_cpld,
    master_cpld,
    slave_cpld,
};

struct cpld_platform_data {
    int reg_addr;
    struct i2c_client *client;
};

static struct cpld_platform_data s6000_cpld_platform_data[] = {
    [system_cpld] = {
        .reg_addr = 0x31,
    },

    [master_cpld] = {
        .reg_addr = 0x32,
    },

    [slave_cpld] = {
        .reg_addr = 0x33,
    },
};

static struct platform_device s6000_cpld = {
    .name               = "dell-s6000-cpld",
    .id                 = 0,
    .dev                = {
                .platform_data   = s6000_cpld_platform_data,
                .release         = device_release
    },
};

/*
 * S6000 QSFP MUX
 */

struct qsfp_mux_platform_data {
    int parent;
    int base_nr;
    int reg_addr;
    struct i2c_client *cpld;
};

struct qsfp_mux {
    struct i2c_adapter *parent;
    struct i2c_adapter **child;
    struct qsfp_mux_platform_data data;
};
static struct qsfp_mux_platform_data s6000_qsfp_mux_platform_data[] = {
    {
        .parent         = S6000_MUX_BASE_NR + 2,
        .base_nr        = QSFP_MODULE_BASE_NR,
        .cpld           = NULL,
        .reg_addr       = 0x0,
    },
    {
        .parent         = S6000_MUX_BASE_NR + 3,
        .base_nr        = QSFP_MODULE_BASE_NR + QSFP_MODULE_NUM,
        .cpld           = NULL,
        .reg_addr       = 0xa,
    },
};

static struct platform_device s6000_qsfp_mux[] = {
    {
        .name           = "dell-s6000-qsfp-mux",
        .id             = 0,
        .dev            = {
                .platform_data   = &s6000_qsfp_mux_platform_data[0],
                .release         = device_release,
        },
    },
    {
        .name           = "dell-s6000-qsfp-mux",
        .id             = 1,
        .dev            = {
                .platform_data   = &s6000_qsfp_mux_platform_data[1],
                .release         = device_release,
        },
    },
};

/*
 * S6000 I2C DEVICES
 */

struct i2c_device_platform_data {
    int parent;
    struct i2c_board_info           info;
    struct i2c_client              *client;
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

static struct i2c_device_platform_data s6000_i2c_device_platform_data[] = {
    {
        /* PSU 1 FRU EEPROM */
        .parent = 1,
        .info = { I2C_BOARD_INFO("24c02", 0x50) },
        .client = NULL,
    },
    {
        /* PSU 2 FRU EEPROM */
        .parent = 1,
        .info = { I2C_BOARD_INFO("24c02", 0x51) },
    },
    {
        /* PSU 1 PMBUS */
        .parent = 1,
        .info = { I2C_BOARD_INFO("dni_dps460", 0x58) },
    },
    {
        /* PSU 2 PMBUS */
        .parent = 1,
        .info = { I2C_BOARD_INFO("dni_dps460", 0x59) },
    },
    {
        /* TEMP Sensor EMC1428-7 */
        .parent = S6000_MUX_BASE_NR,
        .info = { I2C_BOARD_INFO("emc1403", 0x4d) },
    },
    {
        /* JEDEC JC 42.4 compliant temperature sensors */
        .parent = S6000_MUX_BASE_NR,
        .info = { I2C_BOARD_INFO("jc42", 0x18) },
    },
    {
        /* DDR3 MODULE SPD */
        .parent = S6000_MUX_BASE_NR,
        .info = { I2C_BOARD_INFO("spd", 0x50) } ,
    },
    {
        /*
         * ID EEPROM
         * AT24C64D-SSHM-T
         */
        .parent = S6000_MUX_BASE_NR,
        .info = { I2C_BOARD_INFO("24c02", 0x53) } ,
    },
    {
        /*
         * FAN Tray Controller 1
         * MAX6620ATI+T
         */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("max6620", 0x29) },
    },
    {
        /*
         * FAN Tray Controller 2
         * MAX6620ATI+T
         */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("max6620", 0x2a) },
    },
    {
        /*
         * Hot-Swap PSU 1
         * LTC1451UFD#TRPBF
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("ltc4215", 0x40) },
    },
    {
        /*
         * Hot-Swap PSU 2
         * LTC1451UFD#TRPBF
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("ltc4215", 0x42) },
    },
    {
        /*
         * Temp Sensor MAC
         * TMP75AIDR
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("tmp75", 0x4c) },
    },
    {
        /*
         * Temp Sensor NIC
         * TMP75AIDR
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("tmp75", 0x4d) },
    },
    {
        /*
         * Temp Sensor AMB
         * TMP75AIDR
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("tmp75", 0x4e) },
    },
    {
        /*
         * FAN Tray 1 EEPROM
         * M24C02-WMN6TP
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("24c02", 0x51) },
    },
    {
        /*
         * FAN Tray 2 EEPROM
         * M24C02-WMN6TP
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("24c02", 0x52) },
    },
    {
        /*
         * FAN Tray 3 EEPROM
         * M24C02-WMN6TP
        */
        .parent = S6000_MUX_BASE_NR + 1,
        .info = { I2C_BOARD_INFO("24c02", 0x53) },
    },
    /* QSFP Modules */
    {
        .parent = QSFP_MODULE_BASE_NR,
        .info = { SFF8436_INFO(&sff_8436_port[0]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 1,
        .info = { SFF8436_INFO(&sff_8436_port[1]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 2,
        .info = { SFF8436_INFO(&sff_8436_port[2]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 3,
        .info = { SFF8436_INFO(&sff_8436_port[3]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 4,
        .info = { SFF8436_INFO(&sff_8436_port[4]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 5,
        .info = { SFF8436_INFO(&sff_8436_port[5]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 6,
        .info = { SFF8436_INFO(&sff_8436_port[6]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 7,
        .info = { SFF8436_INFO(&sff_8436_port[7]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 8,
        .info = { SFF8436_INFO(&sff_8436_port[8]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 9,
        .info = { SFF8436_INFO(&sff_8436_port[9]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 10,
        .info = { SFF8436_INFO(&sff_8436_port[10]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 11,
        .info = { SFF8436_INFO(&sff_8436_port[11]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 12,
        .info = { SFF8436_INFO(&sff_8436_port[12]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 13,
        .info = { SFF8436_INFO(&sff_8436_port[13]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 14,
        .info = { SFF8436_INFO(&sff_8436_port[14]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 15,
        .info = { SFF8436_INFO(&sff_8436_port[15]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 16,
        .info = { SFF8436_INFO(&sff_8436_port[16]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 17,
        .info = { SFF8436_INFO(&sff_8436_port[17]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 18,
        .info = { SFF8436_INFO(&sff_8436_port[18]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 19,
        .info = { SFF8436_INFO(&sff_8436_port[19]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 20,
        .info = { SFF8436_INFO(&sff_8436_port[20]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 21,
        .info = { SFF8436_INFO(&sff_8436_port[21]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 22,
        .info = { SFF8436_INFO(&sff_8436_port[22]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 23,
        .info = { SFF8436_INFO(&sff_8436_port[23]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 24,
        .info = { SFF8436_INFO(&sff_8436_port[24]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 25,
        .info = { SFF8436_INFO(&sff_8436_port[25]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 26,
        .info = { SFF8436_INFO(&sff_8436_port[26]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 27,
        .info = { SFF8436_INFO(&sff_8436_port[27]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 28,
        .info = { SFF8436_INFO(&sff_8436_port[28]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 29,
        .info = { SFF8436_INFO(&sff_8436_port[29]) },
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 30,
        .info = { SFF8436_INFO(&sff_8436_port[30]) },
        .client = NULL,
    },
    {
        .parent = QSFP_MODULE_BASE_NR + 31,
        .info = { SFF8436_INFO(&sff_8436_port[31]) },
        .client = NULL,
    },
};

static struct platform_device s6000_i2c_device[] = {
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 0,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[0],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 1,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[1],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 2,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[2],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 3,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[3],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 4,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[4],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 5,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[5],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 6,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[6],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 7,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[7],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 8,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[8],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 9,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[9],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 10,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[10],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 11,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[11],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 12,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[12],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 13,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[13],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 14,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[14],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 15,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[15],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 16,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[16],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 17,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[17],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 18,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[18],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 19,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[19],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 20,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[20],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 21,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[21],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 22,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[22],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 23,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[23],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 24,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[24],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 25,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[25],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 26,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[26],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 27,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[27],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 28,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[28],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 29,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[29],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 30,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[30],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 31,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[31],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 32,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[32],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 33,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[33],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 34,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[34],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 35,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[35],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 36,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[36],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 37,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[37],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 38,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[38],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 39,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[39],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 40,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[40],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 41,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[41],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 42,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[42],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 43,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[43],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 44,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[44],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 45,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[45],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 46,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[46],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 47,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[47],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 48,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[48],
                    .release       = device_release,
        },
    },
    {
        .name                   = "dell-s6000-i2c-device",
        .id                     = 49,
        .dev                    = {
                    .platform_data = &s6000_i2c_device_platform_data[49],
                    .release       = device_release,
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

static int qsfp_mux_select(struct i2c_adapter *adap, void *data, u32 chan)
{
    struct qsfp_mux *mux = data;
    unsigned short mask = ~(unsigned short)(1 << chan);

    cpld_reg_write_byte(mux->data.cpld, mux->data.reg_addr, (u8)(mask & 0xff));
    return cpld_reg_write_byte(mux->data.cpld, mux->data.reg_addr + 1, (u8)(mask >> 8));
}

static int __init qsfp_mux_probe(struct platform_device *pdev)
{
    struct qsfp_mux *mux;
    struct qsfp_mux_platform_data *pdata;
    struct i2c_adapter *parent;
    int i, ret;

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

    mux = kzalloc(sizeof(*mux), GFP_KERNEL);
    if (!mux) {
        ret = -ENOMEM;
        goto alloc_failed;
    }

    mux->parent = parent;
    mux->data = *pdata;
    mux->child = kzalloc(sizeof(struct i2c_adapter *) * QSFP_MODULE_NUM, GFP_KERNEL);
    if (!mux->child) {
        ret = -ENOMEM;
        goto alloc_failed2;
    }

    for (i = 0; i < QSFP_MODULE_NUM; i++) {
        int nr = pdata->base_nr + i;
        unsigned int class = 0;

        mux->child[i] = i2c_add_mux_adapter(parent, &pdev->dev, mux,
                           nr, i, class,
                           qsfp_mux_select, NULL);
        if (!mux->child[i]) {
            ret = -ENODEV;
            dev_err(&pdev->dev, "Failed to add adapter %d\n", i);
            goto add_adapter_failed;
        }
    }

    dev_info(&pdev->dev, "16 port mux on %s adapter\n", parent->name);

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

static int __exit qsfp_mux_remove(struct platform_device *pdev)
{
    int i;
    struct qsfp_mux *mux = platform_get_drvdata(pdev);

    for (i = 0; i < QSFP_MODULE_NUM; i++)
        i2c_del_mux_adapter(mux->child[i]);

    platform_set_drvdata(pdev, NULL);
    i2c_put_adapter(mux->parent);
    kfree(mux->child);
    kfree(mux);

    return 0;
}

static struct platform_driver qsfp_mux_driver = {
    .probe  = qsfp_mux_probe,
    .remove = __exit_p(qsfp_mux_remove), /* TODO */
    .driver = {
        .owner  = THIS_MODULE,
        .name   = "dell-s6000-qsfp-mux",
    },
};

/* TODO */
/* module_platform_driver */

static ssize_t get_modsel(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x0);
    if (ret < 0)
        return sprintf(buf, "na");
    data = (u32)ret & 0xff;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x1);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 8;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0xa);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 16;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0xb);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 24;

    return sprintf(buf, "0x%08x\n", data);
}

static ssize_t get_lpmode(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x2);
    if (ret < 0)
        return sprintf(buf, "na");
    data = (u32)ret & 0xff;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x3);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 8;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0xc);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 16;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0xd);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 24;

    return sprintf(buf, "0x%08x\n", data);
}

static ssize_t set_lpmode(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    unsigned long data;
    int err;
    struct cpld_platform_data *pdata = dev->platform_data;

    err = kstrtoul(buf, 16, &data);
    if (err)
        return err;

    i2c_smbus_write_byte_data(pdata[slave_cpld].client, 0x2, (u8)(data & 0xff));
    i2c_smbus_write_byte_data(pdata[slave_cpld].client, 0x3, (u8)((data >> 8) & 0xff));
    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0xc, (u8)((data >> 16) & 0xff));
    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0xd, (u8)((data >> 24) & 0xff));

    return count;
}

static ssize_t get_reset(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x6);
    if (ret < 0)
        return sprintf(buf, "na");
    data = (u32)ret & 0xff;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x7);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 8;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x10);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 16;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x11);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 24;

    return sprintf(buf, "0x%08x\n", data);
}

static ssize_t set_reset(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    unsigned long data;
    int err;
    struct cpld_platform_data *pdata = dev->platform_data;

    err = kstrtoul(buf, 16, &data);
    if (err)
        return err;

    i2c_smbus_write_byte_data(pdata[slave_cpld].client, 0x6, (u8)(data & 0xff));
    i2c_smbus_write_byte_data(pdata[slave_cpld].client, 0x7, (u8)((data >> 8)& 0xff));
    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x10, (u8)((data >> 16) & 0xff));
    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x11, (u8)((data >> 24) & 0xff));

    return count;
}

static ssize_t get_modprs(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x4);
    if (ret < 0)
        return sprintf(buf, "read error");
    data = (u32)ret & 0xff;

    ret = i2c_smbus_read_byte_data(pdata[slave_cpld].client, 0x5);
    if (ret < 0)
        return sprintf(buf, "read error");
    data |= (u32)(ret & 0xff) << 8;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0xe);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 16;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0xf);
    if (ret < 0)
        return sprintf(buf, "na");
    data |= (u32)(ret & 0xff) << 24;

    return sprintf(buf, "0x%08x\n", data);
}

static ssize_t set_power_reset(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    unsigned long data;
    int err;
    struct cpld_platform_data *pdata = dev->platform_data;

    err = kstrtoul(buf, 10, &data);
    if (err)
        return err;

    if (data)
    {
        i2c_smbus_write_byte_data(pdata[system_cpld].client, 0x1, (u8)(0xfd));
    }

    return count;
}

static ssize_t get_power_reset(struct device *dev, struct device_attribute *devattr, char *buf)
{
    return sprintf(buf, "0\n");
}

static ssize_t get_fan_prs(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x8);
    if (ret < 0)
        return sprintf(buf, "read error");
    data = (u32)((ret & 0xc0) >> 6);

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x9);
    if (ret < 0)
        return sprintf(buf, "read error");
    data |= (u32)((ret & 0x01) << 2);
    data = ~data & 0x7;

    return sprintf(buf, "0x%x\n", data);
}

static ssize_t get_psu0_prs(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x3);
    if (ret < 0)
        return sprintf(buf, "read error");

    if (!(ret & 0x80))
        data = 1;

    return sprintf(buf, "%d\n", data);
}

static ssize_t get_psu1_prs(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x3);
    if (ret < 0)
        return sprintf(buf, "read error");

    if (!(ret & 0x08))
        data = 1;

    return sprintf(buf, "%d\n", data);
}

static ssize_t get_psu0_status(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x3);
    if (ret < 0)
        return sprintf(buf, "read error");

    if (!(ret & 0x40))
        data = 1;

    return sprintf(buf, "%d\n", data);
}

static ssize_t get_psu1_status(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x3);
    if (ret < 0)
        return sprintf(buf, "read error");

    if (!(ret & 0x04))
        data = 1;

    return sprintf(buf, "%d\n", data);
}

static ssize_t get_system_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0x60) >> 5;

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "blink_green\n");
            break;
        case 1:
            ret = sprintf(buf, "green\n");
            break;
        case 2:
            ret = sprintf(buf, "yellow\n");
            break;
        default:
            ret = sprintf(buf, "blink_yellow\n");
    }

    return ret;
}

static ssize_t set_system_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "blink_green", 11))
    {
        data = 0;
    }
    else if (!strncmp(buf, "green", 5))
    {
        data = 1;
    }
    else if (!strncmp(buf, "yellow", 6))
    {
        data = 2;
    }
    else if (!strncmp(buf, "blink_yellow", 12))
    {
        data = 3;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x7, (u8)((ret & 0x9F) | (data << 5)));

    return count;
}

static ssize_t get_locator_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0x18) >> 3;

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "off\n");
            break;
        case 1:
            ret = sprintf(buf, "blink_blue\n");
            break;
        case 2:
            ret = sprintf(buf, "blue\n");
            break;
        default:
            ret = sprintf(buf, "invalid\n");
    }

    return ret;
}

static ssize_t set_locator_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "off", 3))
    {
        data = 0;
    }
    else if (!strncmp(buf, "blink_blue", 10))
    {
        data = 1;
    }
    else if (!strncmp(buf, "blue", 4))
    {
        data = 2;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x7, (u8)((ret & 0xE7) | (data << 3)));

    return count;
}

static ssize_t get_power_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0x06) >> 1;

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "off\n");
            break;
        case 1:
            ret = sprintf(buf, "yellow\n");
            break;
        case 2:
            ret = sprintf(buf, "green\n");
            break;
        default:
            ret = sprintf(buf, "blink_yellow\n");
    }

    return ret;
}

static ssize_t set_power_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "off", 3))
    {
        data = 0;
    }
    else if (!strncmp(buf, "yellow", 6))
    {
        data = 1;
    }
    else if (!strncmp(buf, "green", 5))
    {
        data = 2;
    }
    else if (!strncmp(buf, "blink_yellow", 12))
    {
        data = 3;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x7, (u8)((ret & 0xF9) | (data << 1)));

    return count;
}

static ssize_t get_master_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0x1);

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "green\n");
            break;
        default:
            ret = sprintf(buf, "off\n");
            break;
    }

    return ret;
}

static ssize_t set_master_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "green", 5))
    {
        data = 0;
    }
    else if (!strncmp(buf, "off", 3))
    {
        data = 1;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x7);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x7, (u8)((ret & 0xFE) | data));

    return count;
}

static ssize_t get_fan_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x9);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0x18) >> 3;

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "off\n");
            break;
        case 1:
            ret = sprintf(buf, "yellow\n");
            break;
        case 2:
            ret = sprintf(buf, "green\n");
            break;
        default:
            ret = sprintf(buf, "blink_yellow\n");
    }

    return ret;
}

static ssize_t set_fan_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "off", 3))
    {
        data = 0;
    }
    else if (!strncmp(buf, "yellow", 6))
    {
        data = 1;
    }
    else if (!strncmp(buf, "green", 5))
    {
        data = 2;
    }
    else if (!strncmp(buf, "blink_yellow", 12))
    {
        data = 3;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x9);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x9, (u8)((ret & 0xE7) | (data << 3)));

    return count;
}

static ssize_t get_fan0_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x8);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0x3);

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "off\n");
            break;
        case 1:
            ret = sprintf(buf, "green\n");
            break;
        case 2:
            ret = sprintf(buf, "yellow\n");
            break;
        default:
            ret = sprintf(buf, "unknown\n");
    }

    return ret;
}

static ssize_t set_fan0_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "off", 3))
    {
        data = 0;
    }
    else if (!strncmp(buf, "yellow", 6))
    {
        data = 2;
    }
    else if (!strncmp(buf, "green", 5))
    {
        data = 1;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x8);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x8, (u8)((ret & 0xFC) | data));

    return count;
}


static ssize_t get_fan1_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x8);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0xc) >> 2;

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "off\n");
            break;
        case 1:
            ret = sprintf(buf, "green\n");
            break;
        case 2:
            ret = sprintf(buf, "yellow\n");
            break;
        default:
            ret = sprintf(buf, "unknown\n");
    }

    return ret;
}

static ssize_t set_fan1_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "off", 3))
    {
        data = 0;
    }
    else if (!strncmp(buf, "yellow", 6))
    {
        data = 2;
    }
    else if (!strncmp(buf, "green", 5))
    {
        data = 1;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x8);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x8, (u8)((ret & 0xF3) | (data << 2)));

    return count;
}

static ssize_t get_fan2_led(struct device *dev, struct device_attribute *devattr, char *buf)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x8);
    if (ret < 0)
        return sprintf(buf, "read error");

    data = (u32)(ret & 0x30) >> 4;

    switch (data)
    {
        case 0:
            ret = sprintf(buf, "off\n");
            break;
        case 1:
            ret = sprintf(buf, "green\n");
            break;
        case 2:
            ret = sprintf(buf, "yellow\n");
            break;
        default:
            ret = sprintf(buf, "unknown\n");
    }

    return ret;
}

static ssize_t set_fan2_led(struct device *dev, struct device_attribute *devattr, const char *buf, size_t count)
{
    int ret;
    u32 data = 0;
    struct cpld_platform_data *pdata = dev->platform_data;

    if (!strncmp(buf, "off", 3))
    {
        data = 0;
    }
    else if (!strncmp(buf, "yellow", 6))
    {
        data = 2;
    }
    else if (!strncmp(buf, "green", 5))
    {
        data = 1;
    }
    else
    {
        return -1;
    }

    ret = i2c_smbus_read_byte_data(pdata[master_cpld].client, 0x8);
    if (ret < 0)
        return ret;

    i2c_smbus_write_byte_data(pdata[master_cpld].client, 0x8, (u8)((ret & 0xCF) | (data << 4)));

    return count;
}

static DEVICE_ATTR(qsfp_modsel, S_IRUGO, get_modsel, NULL);
static DEVICE_ATTR(qsfp_modprs, S_IRUGO, get_modprs, NULL);
static DEVICE_ATTR(qsfp_lpmode, S_IRUGO | S_IWUSR, get_lpmode, set_lpmode);
static DEVICE_ATTR(qsfp_reset,  S_IRUGO | S_IWUSR, get_reset, set_reset);
static DEVICE_ATTR(power_reset, S_IRUGO | S_IWUSR, get_power_reset, set_power_reset);
static DEVICE_ATTR(fan_prs, S_IRUGO, get_fan_prs, NULL);
static DEVICE_ATTR(psu0_prs, S_IRUGO, get_psu0_prs, NULL);
static DEVICE_ATTR(psu1_prs, S_IRUGO, get_psu1_prs, NULL);
static DEVICE_ATTR(psu0_status, S_IRUGO, get_psu0_status, NULL);
static DEVICE_ATTR(psu1_status, S_IRUGO, get_psu1_status, NULL);
static DEVICE_ATTR(system_led, S_IRUGO | S_IWUSR, get_system_led, set_system_led);
static DEVICE_ATTR(locator_led, S_IRUGO | S_IWUSR, get_locator_led, set_locator_led);
static DEVICE_ATTR(power_led, S_IRUGO | S_IWUSR, get_power_led, set_power_led);
static DEVICE_ATTR(master_led, S_IRUGO | S_IWUSR, get_master_led, set_master_led);
static DEVICE_ATTR(fan_led, S_IRUGO | S_IWUSR, get_fan_led, set_fan_led);
static DEVICE_ATTR(fan0_led, S_IRUGO | S_IWUSR, get_fan0_led, set_fan0_led);
static DEVICE_ATTR(fan1_led, S_IRUGO | S_IWUSR, get_fan1_led, set_fan1_led);
static DEVICE_ATTR(fan2_led, S_IRUGO | S_IWUSR, get_fan2_led, set_fan2_led);

static struct attribute *s6000_cpld_attrs[] = {
    &dev_attr_qsfp_modsel.attr,
    &dev_attr_qsfp_lpmode.attr,
    &dev_attr_qsfp_reset.attr,
    &dev_attr_qsfp_modprs.attr,
    &dev_attr_power_reset.attr,
    &dev_attr_fan_prs.attr,
    &dev_attr_psu0_prs.attr,
    &dev_attr_psu1_prs.attr,
    &dev_attr_psu0_status.attr,
    &dev_attr_psu1_status.attr,
    &dev_attr_system_led.attr,
    &dev_attr_locator_led.attr,
    &dev_attr_power_led.attr,
    &dev_attr_master_led.attr,
    &dev_attr_fan_led.attr,
    &dev_attr_fan0_led.attr,
    &dev_attr_fan1_led.attr,
    &dev_attr_fan2_led.attr,
    NULL,
};

static struct attribute_group s6000_cpld_attr_grp = {
    .attrs = s6000_cpld_attrs,
};

static int __init cpld_probe(struct platform_device *pdev)
{
    struct cpld_platform_data *pdata;
    struct i2c_adapter *parent;
    int i;
    int ret;

    pdata = pdev->dev.platform_data;
    if (!pdata) {
        dev_err(&pdev->dev, "Missing platform data\n");
        return -ENODEV;
    }

    parent = i2c_get_adapter(S6000_MUX_BASE_NR);
    if (!parent) {
        printk(KERN_WARNING "Parent adapter (%d) not found\n",
            S6000_MUX_BASE_NR);
        return -ENODEV;
    }

    for (i = 0; i < CPLD_DEVICE_NUM; i++) {
        pdata[i].client = i2c_new_dummy(parent, pdata[i].reg_addr);
        if (!pdata[i].client) {
            printk(KERN_WARNING "Fail to create dummy i2c client for addr %d\n", pdata[i].reg_addr);
            goto error;
        }
    }

    ret = sysfs_create_group(&pdev->dev.kobj, &s6000_cpld_attr_grp);
    if (ret)
        goto error;

    return 0;

error:
    i--;
    for (; i >= 0; i--) {
        if (pdata[i].client) {
            i2c_unregister_device(pdata[i].client);
        }
    }

    i2c_put_adapter(parent);

    return -ENODEV;
}

static int __exit cpld_remove(struct platform_device *pdev)
{
    int i;
    struct i2c_adapter *parent = NULL;
    struct cpld_platform_data *pdata = pdev->dev.platform_data;

    sysfs_remove_group(&pdev->dev.kobj, &s6000_cpld_attr_grp);

    if (!pdata) {
        dev_err(&pdev->dev, "Missing platform data\n");
    } else {
        for (i = 0; i < CPLD_DEVICE_NUM; i++) {
            if (pdata[i].client) {
                if (!parent) {
                    parent = (pdata[i].client)->adapter;
                }
                i2c_unregister_device(pdata[i].client);
            }
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
        .name   = "dell-s6000-cpld",
    },
};

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
        .name = "dell-s6000-i2c-device",
    }
};

static int __init dell_s6000_platform_init(void)
{
    int ret = 0;
    struct cpld_platform_data *cpld_pdata;
    struct qsfp_mux_platform_data *qsfp_pdata;
    int i;

    printk("delll_s6000_platform module initialization\n");

    mdelay(10000);

    ret = platform_driver_register(&cpld_driver);
    if (ret) {
        printk(KERN_WARNING "Fail to register cpld driver\n");
        goto error_cpld_driver;
    }

    ret = platform_driver_register(&qsfp_mux_driver);
    if (ret) {
        printk(KERN_WARNING "Fail to register qsfp mux driver\n");
        goto error_qsfp_mux_driver;
    }

    ret = platform_driver_register(&i2c_device_driver);
    if (ret) {
        printk(KERN_WARNING "Fail to register i2c device driver\n");
        goto error_i2c_device_driver;
    }

    ret = platform_device_register(&s6000_mux);
    if (ret) {
        printk(KERN_WARNING "Fail to create gpio mux\n");
        goto error_mux;
    }

    ret = platform_device_register(&s6000_cpld);
    if (ret) {
        printk(KERN_WARNING "Fail to create cpld device\n");
        goto error_cpld;
    }

    cpld_pdata = s6000_cpld.dev.platform_data;
    qsfp_pdata = s6000_qsfp_mux[0].dev.platform_data;
    qsfp_pdata->cpld = cpld_pdata[slave_cpld].client;
    qsfp_pdata = s6000_qsfp_mux[1].dev.platform_data;
    qsfp_pdata->cpld = cpld_pdata[master_cpld].client;

    for (i = 0; i < QSFP_DEVICE_NUM; i++) {
        ret = platform_device_register(&s6000_qsfp_mux[i]);
        if (ret) {
            printk(KERN_WARNING "fail to create qsfp mux %d\n", i);
            goto error_qsfp_mux;
        }
    }

    for (i = 0; i < ARRAY_SIZE(s6000_i2c_device_platform_data); i++) {
        ret = platform_device_register(&s6000_i2c_device[i]);
        if (ret) {
            printk(KERN_WARNING "fail to create qsfp mux %d\n", i);
            goto error_i2c_device;
        }
    }

    if (ret)
        goto error_qsfp_mux;

    return 0;

error_i2c_device:
    i--;
    for (; i >= 0; i--) {
        platform_device_unregister(&s6000_i2c_device[i]);
    }
    i = QSFP_DEVICE_NUM;
error_qsfp_mux:
    i--;
    for (; i >= 0; i--) {
        platform_device_unregister(&s6000_qsfp_mux[i]);
    }
    platform_device_unregister(&s6000_cpld);
error_cpld:
    platform_device_unregister(&s6000_mux);
error_mux:
    platform_driver_unregister(&i2c_device_driver);
error_i2c_device_driver:
    platform_driver_unregister(&qsfp_mux_driver);
error_qsfp_mux_driver:
    platform_driver_unregister(&cpld_driver);
error_cpld_driver:
    return ret;
}

static void __exit dell_s6000_platform_exit(void)
{
    int i;

    for (i = 0; i < ARRAY_SIZE(s6000_i2c_device_platform_data); i++)
        platform_device_unregister(&s6000_i2c_device[i]);
    for (i = 0; i < MUX_CHANNEL_NUM; i++)
        platform_device_unregister(&s6000_qsfp_mux[i]);
    platform_device_unregister(&s6000_cpld);
    platform_device_unregister(&s6000_mux);

    platform_driver_unregister(&i2c_device_driver);
    platform_driver_unregister(&cpld_driver);
    platform_driver_unregister(&qsfp_mux_driver);
}

module_init(dell_s6000_platform_init);
module_exit(dell_s6000_platform_exit);

MODULE_DESCRIPTION("DELL S6000 Platform Support");
MODULE_AUTHOR("Guohan Lu <gulv@microsoft.com>");
MODULE_LICENSE("GPL");
