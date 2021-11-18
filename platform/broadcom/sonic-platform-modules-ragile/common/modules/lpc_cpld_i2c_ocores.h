#ifndef _LPC_CPLD_I2C_OCORES_H
#define _LPC_CPLD_I2C_OCORES_H

struct rg_ocores_cpld_i2c_platform_data {
    u32 reg_shift; /* register offset shift value */
    u32 reg_io_width; /* register io read/write width */
    u32 clock_khz; /* input clock in kHz */
    u8 num_devices; /* number of devices in the devices list */
    u8 i2c_irq_flag;
    struct i2c_board_info const *devices; /* devices connected to the bus */
};

#endif /* _LPC_CPLD_I2C_OCORES_H */
