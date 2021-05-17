#include <linux/module.h>
#include <linux/jiffies.h>
#include <linux/i2c.h>
#include <linux/hwmon.h>
#include <linux/hwmon-sysfs.h>
#include <linux/err.h>
#include <linux/mutex.h>
#include <linux/sysfs.h>
#include <linux/slab.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/string.h>

#define DRIVER_VERSION  "1.4.1"

#define TURN_OFF        0
#define TURN_ON         1
#define GET_USB         2
#define GET_LOC         3
#define LOC_OFF         0
#define LOC_BLINK       1
#define ALARM_OFF       0
#define ALARM_AMBER     1
#define ALARM_GREEN     2
#define PSU_1_GOOD      3
#define PSU_2_GOOD      4
#define PCIE_INT        1
#define QSFP_1_INT      2
#define QSFP_2_INT      3
#define FAN_INT         4
#define PSU_INT         5
#define SENSOR_INT      6
#define USB_INT         7
#define USB_ON          0x2
#define USB_OFF         0xfd
#define DIAG_G_ON       0x2
#define DIAG_G_OFF      0xfd
#define LED_ON          0x1
#define LED_OFF         0xfe
#define DIAG_A_ON       0x1
#define DIAG_A_OFF      0xfe
#define LOC_LED_OFF     0x4
#define LOC_LED_BLINK   0xfb
#define SWITCH_LED_OFF  0
#define SWITCH_LED_A_N  1
#define SWITCH_LED_A_B  2
#define SWITCH_LED_G_N  3
#define SWITCH_LED_G_B  4

#define BMC_PRESENT_OFFSET 0xa4

#define SYSFAN_MAX_NUM  4

struct i2c_adap {
	int nr;
	char *name;
	const char *funcs;
	const char *algo;
};

struct i2c_adap *gather_i2c_busses(void);
void free_adapters(struct i2c_adap *adapters);

/* compiler conditional */
#define LED_CTRL_WANTED
#define USB_CTRL_WANTED
#define ASPEED_BMC_WANTED
#define PSU_STAT_WANTED
//#define WDT_CTRL_WANTED
//#define EEPROM_WP_WANTED
//#define I2C_SWITCH_WANTED
//#define THEMAL_WANTED
//#define FAN_CTRL_WANTED

//#define DEBUG_MSG
#ifdef DEBUG_MSG
    #define debug_print(s) printk s
#else
    #define debug_print(s)
#endif

/* end of compiler conditional */

/* i2c_client Declaration */
static struct i2c_client *ESQC_610_i2c_client; //0x30 for other device
static struct i2c_client *Cameo_CPLD_2_client; //0x31 for Port 01-32
static struct i2c_client *Cameo_CPLD_3_client; //0x32 for Port 33-48 QSFP 1-8
static struct i2c_client *Cameo_CPLD_4_client; //0x23 for Fan Status
static struct i2c_client *Cameo_CPLD_5_client; //0x35 for Power Status
#ifdef I2C_SWITCH_WANTED
static struct i2c_client *Cameo_Switch_1_client; //0x73
static struct i2c_client *Cameo_Switch_2_client; //0x77
#endif
#ifdef THEMAL_WANTED
static struct i2c_client *Cameo_Sensor_client; //0x4c themal sensor
static struct i2c_client *Cameo_Sensor_fan_client; //0x2e themal sensor
#endif
#ifdef ASPEED_BMC_WANTED
static struct i2c_client *Cameo_BMC_client; //0x14 ASPEED BMC
#endif
/* end of i2c_client Declaration */

/* Function Declaration */
/* i2c-0 */
static ssize_t psu_status_get(struct device *dev, struct device_attribute *da, char *buf);
#ifdef PSU_STAT_WANTED
static ssize_t psu_module_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t dc_chip_switch_get(struct device *dev, struct device_attribute *da, char *buf);
#endif
#ifdef USB_CTRL_WANTED
static ssize_t usb_power_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t usb_power_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif
#ifdef LED_CTRL_WANTED
static ssize_t led_ctrl_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t led_ctrl_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif
static ssize_t sys_led_ctrl_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sys_led_ctrl_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t reset_mac_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t shutdown_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t themal_status_get(struct device *dev, struct device_attribute *da, char *buf);
#ifdef THEMAL_WANTED
static ssize_t themal_temp_get(struct device *dev, struct device_attribute *da, char *buf);
#endif
static ssize_t themal_mask_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t themal_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t int_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sfp_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sfp_tx_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t low_power_all_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t low_power_all_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t low_power_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t low_power_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t qsfp_reset_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t qsfp_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t fan_status_get(struct device *dev, struct device_attribute *da, char *buf);
#ifdef FAN_CTRL_WANTED
static ssize_t fan_mode_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t fan_mode_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t fan_rpm_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t fan_rpm_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif
#ifdef ASPEED_BMC_WANTED
static ssize_t bmc_register_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t bmc_module_detect(struct device *dev, struct device_attribute *da, char *buf);
#endif
#ifdef WDT_CTRL_WANTED
static ssize_t wdt_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t wdt_status_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif
#ifdef EEPROM_WP_WANTED
static ssize_t eeprom_wp_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t eeprom_wp_status_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif
static ssize_t hw_version_get(struct device *dev, struct device_attribute *da, char *buf);
/* end of Function Declaration */

/* struct i2c_data */
struct Cameo_i2c_data
{
    struct device      *hwmon_dev;
    struct mutex        update_lock;
    char                valid;          /* !=0 if registers are valid */
    unsigned long       last_updated;   /* In jiffies */
    u8  status;                         /* Status register read from CPLD */
};

/* struct i2c_sysfs_attributes */
enum Cameo_i2c_sysfs_attributes
{
    /* i2c-0 */
    /*CPLD 0X30*/
    PSU_PRESENT,
    PSU_STATUS,
#ifdef PSU_STAT_WANTED
    PSU_MODULE_1,
    PSU_MODULE_2,
    DC_CHIP_SWITCH,
#endif
#ifdef USB_CTRL_WANTED
    USB_POWER,
#endif
#ifdef LED_CTRL_WANTED
    LED_CTRL,
#endif
    SYS_LED,
    FLOW_LED,
    SW_LED_1,
    SW_LED_2,
    RESET_MAC,
    SHUTDOWN_DUT,
    SENSOR_STATUS,
#ifdef THEMAL_WANTED
    SENSOR_TEMP,
#endif
    SENSOR_INT_MASK,
    INT_STATUS,
    /*CPLD 0X31 & 0X32*/
    SFP_PRESENT,
    SFP_RX_LOSS,
    SFP_TX_STAT,
    QSFP_LOW_POWER_ALL,
    QSFP_RESET,
    QSFP_PRESENT,
    QSFP_INT,
    FAN_STATUS,
    FAN_PRESENT,
    FAN_POWER,
    FAN_SPEED_RPM,
#ifdef FAN_CTRL_WANTED
    FAN_MODE,
    FAN_RPM,
#endif
#ifdef ASPEED_BMC_WANTED
    BMC_SERSOR_1,
    BMC_SERSOR_2,
    BMC_SERSOR_3,
    BMC_SERSOR_4,
    BMC_DETECT,
#endif
#ifdef WDT_CTRL_WANTED
    WDT_CTRL,
#endif
#ifdef EEPROM_WP_WANTED
    EEPROM_WP_CTRL,
#endif
    HW_VER,
};
/* end of struct i2c_sysfs_attributes */

/* sysfs attributes for SENSOR_DEVICE_ATTR */
/* i2c-0 */
/*CPLD 0X30*/
static SENSOR_DEVICE_ATTR(psu_present       , S_IRUGO           , psu_status_get    , NULL              , PSU_PRESENT);
static SENSOR_DEVICE_ATTR(psu_status        , S_IRUGO           , psu_status_get    , NULL              , PSU_STATUS);
#ifdef PSU_STAT_WANTED
static SENSOR_DEVICE_ATTR(psu_module_1      , S_IRUGO           , psu_module_get    , NULL              , PSU_MODULE_1);
static SENSOR_DEVICE_ATTR(psu_module_2      , S_IRUGO           , psu_module_get    , NULL              , PSU_MODULE_2);
static SENSOR_DEVICE_ATTR(dc_chip_switch    , S_IRUGO           , dc_chip_switch_get, NULL              , DC_CHIP_SWITCH);
#endif
#ifdef USB_CTRL_WANTED
static SENSOR_DEVICE_ATTR(usb_power         , S_IRUGO | S_IWUSR , usb_power_get     , usb_power_set     , USB_POWER);
#endif
#ifdef LED_CTRL_WANTED
static SENSOR_DEVICE_ATTR(led_ctrl          , S_IRUGO | S_IWUSR , led_ctrl_get      , led_ctrl_set      , LED_CTRL);
#endif
static SENSOR_DEVICE_ATTR(led_sys           , S_IRUGO | S_IWUSR , sys_led_ctrl_get  , sys_led_ctrl_set  , SYS_LED);
static SENSOR_DEVICE_ATTR(led_flow          , S_IRUGO | S_IWUSR , sys_led_ctrl_get  , sys_led_ctrl_set  , FLOW_LED);
static SENSOR_DEVICE_ATTR(led_sw1           , S_IRUGO | S_IWUSR , sys_led_ctrl_get  , sys_led_ctrl_set  , SW_LED_1);
static SENSOR_DEVICE_ATTR(led_sw2           , S_IRUGO | S_IWUSR , sys_led_ctrl_get  , sys_led_ctrl_set  , SW_LED_2);
static SENSOR_DEVICE_ATTR(reset_mac         , S_IRUGO | S_IWUSR , NULL              , reset_mac_set     , RESET_MAC);
static SENSOR_DEVICE_ATTR(shutdown_set      , S_IRUGO | S_IWUSR , NULL              , shutdown_set      , SHUTDOWN_DUT);
static SENSOR_DEVICE_ATTR(sensor_status     , S_IRUGO           , themal_status_get , NULL              , SENSOR_STATUS);
#ifdef THEMAL_WANTED
static SENSOR_DEVICE_ATTR(sensor_temp       , S_IRUGO           , themal_temp_get   , NULL              , SENSOR_TEMP);
#endif
static SENSOR_DEVICE_ATTR(sensor_int_mask   , S_IRUGO           , themal_mask_get   , NULL              , SENSOR_INT_MASK);
static SENSOR_DEVICE_ATTR(sensor_int_mask_1 , S_IRUGO | S_IWUSR , NULL              , themal_mask_set   , 1);
static SENSOR_DEVICE_ATTR(sensor_int_mask_2 , S_IRUGO | S_IWUSR , NULL              , themal_mask_set   , 2);
static SENSOR_DEVICE_ATTR(sensor_int_mask_3 , S_IRUGO | S_IWUSR , NULL              , themal_mask_set   , 3);
static SENSOR_DEVICE_ATTR(sensor_int_mask_4 , S_IRUGO | S_IWUSR , NULL              , themal_mask_set   , 4);
static SENSOR_DEVICE_ATTR(int_status        , S_IRUGO           , int_status_get    , NULL              , INT_STATUS);
/*CPLD 0X31 & 0X32*/
static SENSOR_DEVICE_ATTR(SFP_present       , S_IRUGO           , sfp_status_get    , NULL              , SFP_PRESENT);
static SENSOR_DEVICE_ATTR(SFP_rx_loss       , S_IRUGO           , sfp_status_get    , NULL              , SFP_RX_LOSS);
static SENSOR_DEVICE_ATTR(SFP_tx_stat       , S_IRUGO           , sfp_status_get    , NULL              , SFP_TX_STAT);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_1     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 1);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_2     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 2);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_3     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 3);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_4     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 4);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_5     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 5);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_6     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 6);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_7     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 7);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_8     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 8);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_9     , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 9);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_10    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 10);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_11    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 11);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_12    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 12);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_13    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 13);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_14    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 14);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_15    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 15);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_16    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 16);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_17    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 17);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_18    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 18);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_19    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 19);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_20    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 20);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_21    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 21);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_22    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 22);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_23    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 23);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_24    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 24);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_25    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 25);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_26    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 26);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_27    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 27);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_28    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 28);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_29    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 29);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_30    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 30);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_31    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 31);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_32    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 32);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_33    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 33);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_34    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 34);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_35    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 35);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_36    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 36);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_37    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 37);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_38    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 38);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_39    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 39);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_40    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 40);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_41    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 41);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_42    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 42);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_43    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 43);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_44    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 44);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_45    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 45);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_46    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 46);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_47    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 47);
static SENSOR_DEVICE_ATTR(SFP_tx_ctrl_48    , S_IRUGO | S_IWUSR , NULL              , sfp_tx_set        , 48);
static SENSOR_DEVICE_ATTR(QSFP_low_power_all, S_IRUGO | S_IWUSR , low_power_all_get , low_power_all_set , QSFP_LOW_POWER_ALL);
static SENSOR_DEVICE_ATTR(QSFP_low_power_1  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 1);
static SENSOR_DEVICE_ATTR(QSFP_low_power_2  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 2);
static SENSOR_DEVICE_ATTR(QSFP_low_power_3  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 3);
static SENSOR_DEVICE_ATTR(QSFP_low_power_4  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 4);
static SENSOR_DEVICE_ATTR(QSFP_low_power_5  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 5);
static SENSOR_DEVICE_ATTR(QSFP_low_power_6  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 6);
static SENSOR_DEVICE_ATTR(QSFP_low_power_7  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 7);
static SENSOR_DEVICE_ATTR(QSFP_low_power_8  , S_IRUGO | S_IWUSR , low_power_get     , low_power_set     , 8);
static SENSOR_DEVICE_ATTR(QSFP_reset        , S_IRUGO | S_IWUSR , NULL              , qsfp_reset_set    , QSFP_RESET);
static SENSOR_DEVICE_ATTR(QSFP_present      , S_IRUGO           , qsfp_status_get   , NULL              , QSFP_PRESENT);
static SENSOR_DEVICE_ATTR(QSFP_int          , S_IRUGO           , qsfp_status_get   , NULL              , QSFP_INT);
static SENSOR_DEVICE_ATTR(fan_status        , S_IRUGO           , fan_status_get    , NULL              , FAN_STATUS);
static SENSOR_DEVICE_ATTR(fan_present       , S_IRUGO           , fan_status_get    , NULL              , FAN_PRESENT);
static SENSOR_DEVICE_ATTR(fan_power         , S_IRUGO           , fan_status_get    , NULL              , FAN_POWER);
static SENSOR_DEVICE_ATTR(fan_speed_rpm     , S_IRUGO           , fan_status_get    , NULL              , FAN_SPEED_RPM);
#ifdef FAN_CTRL_WANTED
static SENSOR_DEVICE_ATTR(fan_mode          , S_IRUGO | S_IWUSR , fan_mode_get      , fan_mode_set      , FAN_MODE);
static SENSOR_DEVICE_ATTR(fan_rpm           , S_IRUGO | S_IWUSR , fan_rpm_get       , fan_rpm_set       , FAN_RPM);
#endif
#ifdef ASPEED_BMC_WANTED
static SENSOR_DEVICE_ATTR(bmc_sersor_1      , S_IRUGO           , bmc_register_get  , NULL              , BMC_SERSOR_1);
static SENSOR_DEVICE_ATTR(bmc_sersor_2      , S_IRUGO           , bmc_register_get  , NULL              , BMC_SERSOR_2);
static SENSOR_DEVICE_ATTR(bmc_sersor_3      , S_IRUGO           , bmc_register_get  , NULL              , BMC_SERSOR_3);
static SENSOR_DEVICE_ATTR(bmc_sersor_4      , S_IRUGO           , bmc_register_get  , NULL              , BMC_SERSOR_4);
static SENSOR_DEVICE_ATTR(bmc_present       , S_IRUGO           , bmc_module_detect , NULL              , BMC_DETECT);
#endif
#ifdef WDT_CTRL_WANTED
static SENSOR_DEVICE_ATTR(wdt_ctrl          , S_IRUGO | S_IWUSR , wdt_status_get    , wdt_status_set    , WDT_CTRL);
#endif
static SENSOR_DEVICE_ATTR(hw_version        , S_IRUGO           , hw_version_get    , NULL              , HW_VER);
#ifdef EEPROM_WP_WANTED
static SENSOR_DEVICE_ATTR(eeprom_wp_ctrl    , S_IRUGO | S_IWUSR , eeprom_wp_status_get  , eeprom_wp_status_set  , EEPROM_WP_CTRL);
#endif
/* end of sysfs attributes for SENSOR_DEVICE_ATTR */

/* sysfs attributes for hwmon */
/* i2c-0 */
static struct attribute *ESQC610_SYS_attributes[] =
{
    &sensor_dev_attr_hw_version.dev_attr.attr,
#ifdef WDT_CTRL_WANTED
    &sensor_dev_attr_wdt_ctrl.dev_attr.attr,
#endif
#ifdef EEPROM_WP_WANTED
    &sensor_dev_attr_eeprom_wp_ctrl.dev_attr.attr,
#endif
    NULL
};

static struct attribute *ESQC610_PSU_attributes[] =
{
    &sensor_dev_attr_psu_present.dev_attr.attr,
    &sensor_dev_attr_psu_status.dev_attr.attr,
#ifdef PSU_STAT_WANTED
    &sensor_dev_attr_psu_module_1.dev_attr.attr,
    &sensor_dev_attr_psu_module_2.dev_attr.attr,
    &sensor_dev_attr_dc_chip_switch.dev_attr.attr,
#endif
    NULL
};
#ifdef USB_CTRL_WANTED
static struct attribute *ESQC610_USB_attributes[] =
{
    &sensor_dev_attr_usb_power.dev_attr.attr,
    NULL
};
#endif
static struct attribute *ESQC610_LED_attributes[] =
{
#ifdef LED_CTRL_WANTED
    &sensor_dev_attr_led_ctrl.dev_attr.attr,
#endif
    &sensor_dev_attr_led_sys.dev_attr.attr,
    &sensor_dev_attr_led_flow.dev_attr.attr,
    &sensor_dev_attr_led_sw1.dev_attr.attr,
    &sensor_dev_attr_led_sw2.dev_attr.attr,
    NULL
};

static struct attribute *ESQC610_Reset_attributes[] =
{
    &sensor_dev_attr_reset_mac.dev_attr.attr,
    &sensor_dev_attr_shutdown_set.dev_attr.attr,
    NULL
};

static struct attribute *ESQC610_Sensor_attributes[] =
{
    &sensor_dev_attr_sensor_status.dev_attr.attr,
#ifdef THEMAL_WANTED
    &sensor_dev_attr_sensor_temp.dev_attr.attr,
#endif
    NULL
};

static struct attribute *ESQC610_INT_attributes[] =
{
    &sensor_dev_attr_int_status.dev_attr.attr,
    &sensor_dev_attr_QSFP_int.dev_attr.attr,
    &sensor_dev_attr_sensor_int_mask.dev_attr.attr,
    &sensor_dev_attr_sensor_int_mask_1.dev_attr.attr,
    &sensor_dev_attr_sensor_int_mask_2.dev_attr.attr,
    &sensor_dev_attr_sensor_int_mask_3.dev_attr.attr,
    &sensor_dev_attr_sensor_int_mask_4.dev_attr.attr,
    NULL
};

static struct attribute *ESQC610_SFP_attributes[] =
{
    &sensor_dev_attr_SFP_present.dev_attr.attr,
    &sensor_dev_attr_SFP_rx_loss.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_stat.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_1.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_2.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_3.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_4.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_5.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_6.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_7.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_8.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_9.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_10.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_11.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_12.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_13.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_14.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_15.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_16.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_17.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_18.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_19.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_20.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_21.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_22.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_23.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_24.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_25.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_26.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_27.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_28.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_29.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_30.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_31.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_32.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_33.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_34.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_35.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_36.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_37.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_38.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_39.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_40.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_41.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_42.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_43.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_44.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_45.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_46.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_47.dev_attr.attr,
    &sensor_dev_attr_SFP_tx_ctrl_48.dev_attr.attr,
    NULL
};

static struct attribute *ESQC610_QSFP_attributes[] =
{
    &sensor_dev_attr_QSFP_present.dev_attr.attr,
    &sensor_dev_attr_QSFP_reset.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_all.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_1.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_2.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_3.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_4.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_5.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_6.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_7.dev_attr.attr,
    &sensor_dev_attr_QSFP_low_power_8.dev_attr.attr,
    NULL
};

static struct attribute *ESQC610_FAN_attributes[] = {
    &sensor_dev_attr_fan_status.dev_attr.attr,
    &sensor_dev_attr_fan_present.dev_attr.attr,
    &sensor_dev_attr_fan_power.dev_attr.attr,
    &sensor_dev_attr_fan_speed_rpm.dev_attr.attr,
#ifdef FAN_CTRL_WANTED
    &sensor_dev_attr_fan_mode.dev_attr.attr,
    &sensor_dev_attr_fan_rpm.dev_attr.attr,
#endif
    NULL
};

#ifdef ASPEED_BMC_WANTED
static struct attribute *ESQC610_BMC_attributes[] = {
    &sensor_dev_attr_bmc_sersor_1.dev_attr.attr,
    &sensor_dev_attr_bmc_sersor_2.dev_attr.attr,
    &sensor_dev_attr_bmc_sersor_3.dev_attr.attr,
    &sensor_dev_attr_bmc_sersor_4.dev_attr.attr,
    &sensor_dev_attr_bmc_present.dev_attr.attr,
    NULL
};
#endif
/* end of sysfs attributes for hwmon */

/* struct attribute_group */
static const struct attribute_group ESQC610_SYS_group =
{
    .name  = "ESQC610_SYS",
    .attrs = ESQC610_SYS_attributes,
};

static const struct attribute_group ESQC610_PSU_group =
{
    .name  = "ESQC610_PSU",
    .attrs = ESQC610_PSU_attributes,
};

#ifdef USB_CTRL_WANTED
static const struct attribute_group ESQC610_USB_group =
{
    .name  = "ESQC610_USB",
    .attrs = ESQC610_USB_attributes,
};
#endif

static const struct attribute_group ESQC610_LED_group =
{
    .name  = "ESQC610_LED",
    .attrs = ESQC610_LED_attributes,
};

static const struct attribute_group ESQC610_Reset_group =
{
    .name  = "ESQC610_Reset",
    .attrs = ESQC610_Reset_attributes,
};

static const struct attribute_group ESQC610_Sensor_group =
{
    .name  = "ESQC610_Sensor",
    .attrs = ESQC610_Sensor_attributes,
};

static const struct attribute_group ESQC610_INT_group =
{
    .name  = "ESQC610_INT",
    .attrs = ESQC610_INT_attributes,
};

static const struct attribute_group ESQC610_SFP_group =
{
    .name  = "ESQC610_SFP",
    .attrs = ESQC610_SFP_attributes,
};

static const struct attribute_group ESQC610_QSFP_group =
{
    .name  = "ESQC610_QSFP",
    .attrs = ESQC610_QSFP_attributes,
};

static const struct attribute_group ESQC610_FAN_group =
{
    .name  = "ESQC610_FAN",
    .attrs = ESQC610_FAN_attributes,
};

#ifdef ASPEED_BMC_WANTED
static const struct attribute_group ESQC610_BMC_group =
{
    .name  = "ESQC610_BMC",
    .attrs = ESQC610_BMC_attributes,
};
#endif
/* end of struct attribute_group */
