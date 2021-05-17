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
#include <linux/delay.h>

#define DRIVER_VERSION  "2.5"

#define TURN_OFF            0
#define TURN_ON             1
#define LED_ON              0x1
#define LED_OFF             0xfe
#define ALERT_TH0           1
#define ALERT_TH1           2
#define ALERT_TH2           3
#define ALERT_TH3           4
#define ALERT_TH4           5
#define ALERT_TH5           6
#define ALERT_TH0_MASK      1
#define ALERT_TH1_MASK      2
#define ALERT_TH2_MASK      3
#define ALERT_TH3_MASK      4
#define ALERT_TH4_MASK      5
#define ALERT_TH5_MASK      6
#define SW_ALERT_TH0        1
#define SW_ALERT_TH1        2
#define SW_ALERT_TH2        3
#define SW_ALERT_TH3        4
#define SW_ALERT_TH0_MASK   1
#define SW_ALERT_TH1_MASK   2
#define SW_ALERT_TH2_MASK   3
#define SW_ALERT_TH3_MASK   4
#define SENSOR_INT_0        1
#define SENSOR_INT_1        2
#define SENSOR_INT_0_MASK   1
#define SENSOR_INT_1_MASK   2
#define FAN_CH1             1
#define FAN_CH2             2
#define FAN_CH3             3
#define USB_ON              0x1
#define USB_OFF             0xfe
#define MODULE_INS_INT      1
#define MODULE_INT          2
#define MODULE_POWER_INT    3
#define THER_SENSOR_INT     4
#define IO_BOARD_INT        5
#define FAN_ERROR_INT       6
#define MODULE_INS_INT_MASK 1
#define MODULE_INT_MASK     2
#define MODULE_POW_INT_MASK 3
#define THER_SEN_INT_MASK   4
#define IO_BOARD_INT_MASK   5
#define FAN_ERROR_INT_MASK  6
#define SFP_PORT_1          1
#define SFP_PORT_2          2
#define SFP_PORT_MGM        3
#define SFP_PORT_1_ON       1
#define SFP_PORT_1_OFF      2
#define SFP_PORT_2_ON       3
#define SFP_PORT_2_OFF      4
#define SFP_PORT_MGM_ON     5
#define SFP_PORT_MGM_OFF    6
#define SYS_LED_A           1
#define SYS_LED_G           2
#define SYS_LED_BLINK       3
#define SYS_LED_OFF         0
#define SYS_LED_A_N         1
#define SYS_LED_A_B         2
#define SYS_LED_G_N         3
#define SYS_LED_G_B         4
#define SWITCH_LED_OFF      0
#define SWITCH_LED_A_N      1
#define SWITCH_LED_A_B      2
#define SWITCH_LED_G_N      3
#define SWITCH_LED_G_B      4
#define SWITCH_LED_BLINK    1

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
#define ESC_600_BMC_WANTED
#define ESC_600_INT_WANTED
#define ESC_600_ALARM_WANTED
#define ESC_600_STAT_WANTED
#define ESC_600_JTAG_WANTED
#define WDT_CTRL_WANTED
#define EEPROM_WP_WANTED
//#define EEPROM_WANTED
//#define LED_L3_CTRL_WANTED
//#define LINEAR_CONVERT_FUNCTION

#define DEBUG_MSG
#ifdef DEBUG_MSG
    #define debug_print(s) printk s
#else
    #define debug_print(s)
#endif
/* end of compiler conditional */

/* i2c_client Declaration */
static struct i2c_client *ESC_600_128q_client;      //0x33 I/O Board CPLD ,XO2-640
static struct i2c_client *Cameo_Extpand_1_client;   //0x20 I/O Extpander ,PCA9534PW
static struct i2c_client *Cameo_Extpand_2_client;   //0x21 I/O Extpander ,PCA9534PW
static struct i2c_client *Cameo_CPLD_2_client;      //0x30 CPLD ,XO2-2000HC-4FTG256C
static struct i2c_client *Cameo_CPLD_3_client;      //0x31 CPLD ,XO2-7000HC-4TG144C
static struct i2c_client *Cameo_CPLD_4_client;      //0x35 CPLD ,XO2-2000HC-4FTG256C
#ifdef ESC_600_BMC_WANTED
static struct i2c_client *Cameo_BMC_client;         //0x14 BMC ,Aspeed
#endif /*ESC_600_BMC_WANTED*/
/* end of i2c_client Declaration */

/* Function Declaration */
/*0x33 I/O Board CPLD*/
static ssize_t sfp_select_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sfp_select_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t sfp_tx_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sfp_tx_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t sfp_insert_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sfp_rx_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t psu_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_button_get(struct device *dev, struct device_attribute *da, char *buf);
#ifdef LED_CTRL_WANTED
static ssize_t sys_led_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sys_led_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t switch_led_all_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_led_all_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#ifdef LED_L3_CTRL_WANTED
static ssize_t switch_led_3_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_led_3_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*LED_L3_CTRL_WANTED*/
static ssize_t switch_led_4_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_led_4_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t switch_led_5_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_led_5_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*LED_CTRL_WANTED*/
#ifdef ESC_600_INT_WANTED
static ssize_t sfp_int_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t psu_int_get(struct device *dev, struct device_attribute *da, char *buf);
#endif /*ESC_600_INT_WANTED*/
/*0x31 CPLD-1 700HC*/
#ifdef LED_CTRL_WANTED
static ssize_t led_ctrl_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t led_ctrl_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*LED_CTRL_WANTED*/
#ifdef ESC_600_JTAG_WANTED
static ssize_t jtag_select_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t jtag_select_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*ESC_600_JTAG_WANTED*/
#ifdef ESC_600_STAT_WANTED
static ssize_t sensor_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sersor_status_mask_all_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sersor_status_mask_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sersor_status_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*ESC_600_STAT_WANTED*/
#ifdef ESC_600_ALARM_WANTED
static ssize_t switch_alarm_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_alarm_mask_all_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_alarm_mask_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_alarm_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*ESC_600_ALARM_WANTED*/
#ifdef ESC_600_INT_WANTED
static ssize_t sensor_int_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sersor_int_mask_all_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sersor_int_mask_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t sersor_int_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t int_mask_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t int_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*ESC_600_INT_WANTED*/
/*0x30 CPLD-1 640UHC*/
static ssize_t fan_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t fan_insert_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t fan_power_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t fan_direct_get(struct device *dev, struct device_attribute *da, char *buf);
#ifdef USB_CTRL_WANTED
static ssize_t usb_power_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t usb_power_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*USB_CTRL_WANTED*/
static ssize_t shutdown_sys_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t shutdown_sys_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t reset_sys_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t module_reset_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t module_power_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t module_12v_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t module_enable_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t module_enable_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t module_insert_get(struct device *dev, struct device_attribute *da, char *buf);
#ifdef ESC_600_INT_WANTED
static ssize_t switch_int_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_int_mask_all_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_int_mask_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t switch_int_mask_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*ESC_600_INT_WANTED*/
static ssize_t cpld_version_get(struct device *dev, struct device_attribute *da, char *buf);
#ifdef WDT_CTRL_WANTED
static ssize_t wdt_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t wdt_status_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*WDT_CTRL_WANTED*/
#ifdef EEPROM_WP_WANTED
static ssize_t eeprom_wp_status_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t eeprom_wp_status_set(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
#endif /*EEPROM_WP_WANTED*/
/*0x14 BMC*/
#ifdef ESC_600_BMC_WANTED
static ssize_t bmc_module_detect(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t themal_temp_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t module_temp_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t mac_temp_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t psu_module_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t dc_chip_switch_get(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t dc_chip_slot_get(struct device *dev, struct device_attribute *da, char *buf);
#endif /*ESC_600_BMC_WANTED*/
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
/*end of struct i2c_data */

/* struct i2c_sysfs_attributes */
enum Cameo_i2c_sysfs_attributes
{
    /*0x31 CPLD-1 700HC*/
#ifdef LED_CTRL_WANTED
    LED_CTRL,
#endif /*LED_CTRL_WANTED*/
#ifdef ESC_600_JTAG_WANTED
    JTAG_SELECT,
#endif /*ESC_600_JTAG_WANTED*/
#ifdef ESC_600_STAT_WANTED
    SENSOR_STATUS,
    SENSOR_STATUS_MASK,
#endif /*ESC_600_STAT_WANTED*/
#ifdef ESC_600_ALARM_WANTED
    SWITCH_ALARM,
    SWITCH_ALARM_MASK,
#endif /*ESC_600_ALARM_WANTED*/
#ifdef ESC_600_INT_WANTED
    SENSOR_INT,
    SENSOR_INT_MASK,
#endif /*ESC_600_INT_WANTED*/
    /*0x30 CPLD-1 640UHC*/
    FAN_STATUS,
    FAN_INSERT,
    FAN_POWER,
    FAN_DIRECT,
    FAN_SPEED_RPM,
#ifdef USB_CTRL_WANTED
    USB_POWER,
#endif /*USB_CTRL_WANTED*/
    SYS_SHUTDOWN,
    SYS_RESET,
    MODULE_RESET,
    MODULE_INSERT,
    MODULE_POWER,
    MODULE_ENABLE,
    MODULE_12V_STAT,
    CPLD_VER,
#ifdef ESC_600_INT_WANTED
    SWITCH_INT,
    SWITCH_INT_MASK,
#endif /*ESC_600_INT_WANTED*/
#ifdef WDT_CTRL_WANTED
    WDT_CTRL,
#endif
#ifdef EEPROM_WP_WANTED
    EEPROM_WP_CTRL,
#endif
    /*0x33 I/O Board CPLD*/
    SFP_SELECT,
    SFP_INSERT,
    SFP_TX_DISABLE,
    SFP_RX_LOSS,
    PSU_PRESENT,
    PSU_STATUS,
    SWITCH_BUTTON,
#ifdef ESC_600_BMC_WANTED
    SENSOR_TEMP,
    MODULE_TEMP,
    MAC_TEMP,
    DC_CHIP_SWITCH,
    DC_CHIP_SLOT_1,
    DC_CHIP_SLOT_2,
    DC_CHIP_SLOT_3,
    DC_CHIP_SLOT_4,
    DC_CHIP_SLOT_5,
    DC_CHIP_SLOT_6,
    DC_CHIP_SLOT_7,
    DC_CHIP_SLOT_8,
    PSU_MODULE_1,
    PSU_MODULE_2,
    PSU_MODULE_3,
    PSU_MODULE_4,
    BMC_DETECT,
#endif /*ESC_600_BMC_WANTED*/
#ifdef LED_CTRL_WANTED
    SYS_LED,
    SWITCH_LED,
#endif /*LED_CTRL_WANTED*/
#ifdef ESC_600_INT_WANTED
    SFP_INT,
    SFP_INT_MASK,
    PSU_INT,
#endif /*ESC_600_INT_WANTED*/
};
/* end of struct i2c_sysfs_attributes */

/* sysfs attributes for SENSOR_DEVICE_ATTR */
/*ESC600_SYS_attributes*/
static SENSOR_DEVICE_ATTR(cpld_version              , S_IRUGO           , cpld_version_get              , NULL                      , CPLD_VER);
#ifdef WDT_CTRL_WANTED
static SENSOR_DEVICE_ATTR(wdt_ctrl                  , S_IRUGO | S_IWUSR , wdt_status_get                , wdt_status_set            , WDT_CTRL);
#endif /*WDT_CTRL_WANTED*/
#ifdef EEPROM_WP_WANTED
static SENSOR_DEVICE_ATTR(eeprom_wp_ctrl    , S_IRUGO | S_IWUSR , eeprom_wp_status_get   , eeprom_wp_status_set   , EEPROM_WP_CTRL);
#endif /*EEPROM_WP_WANTED*/
/*ESC600_PSU_attributes*/
static SENSOR_DEVICE_ATTR(psu_present               , S_IRUGO           , psu_status_get                , NULL                      , PSU_PRESENT);
static SENSOR_DEVICE_ATTR(psu_status                , S_IRUGO           , psu_status_get                , NULL                      , PSU_STATUS);
#ifdef ESC_600_BMC_WANTED
static SENSOR_DEVICE_ATTR(psu_module_1              , S_IRUGO           , psu_module_get                , NULL                      , PSU_MODULE_1);
static SENSOR_DEVICE_ATTR(psu_module_2              , S_IRUGO           , psu_module_get                , NULL                      , PSU_MODULE_2);
static SENSOR_DEVICE_ATTR(psu_module_3              , S_IRUGO           , psu_module_get                , NULL                      , PSU_MODULE_3);
static SENSOR_DEVICE_ATTR(psu_module_4              , S_IRUGO           , psu_module_get                , NULL                      , PSU_MODULE_4);
static SENSOR_DEVICE_ATTR(dc_chip_switch            , S_IRUGO           , dc_chip_switch_get            , NULL                      , DC_CHIP_SWITCH);
static SENSOR_DEVICE_ATTR(dc_chip_slot_1            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_1);
static SENSOR_DEVICE_ATTR(dc_chip_slot_2            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_2);
static SENSOR_DEVICE_ATTR(dc_chip_slot_3            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_3);
static SENSOR_DEVICE_ATTR(dc_chip_slot_4            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_4);
static SENSOR_DEVICE_ATTR(dc_chip_slot_5            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_5);
static SENSOR_DEVICE_ATTR(dc_chip_slot_6            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_6);
static SENSOR_DEVICE_ATTR(dc_chip_slot_7            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_7);
static SENSOR_DEVICE_ATTR(dc_chip_slot_8            , S_IRUGO           , dc_chip_slot_get              , NULL                      , DC_CHIP_SLOT_8);
#endif /*ESC_600_BMC_WANTED*/
/*ESC600_JTAG_attributes*/
#ifdef ESC_600_JTAG_WANTED
static SENSOR_DEVICE_ATTR(jtag_select               , S_IRUGO | S_IWUSR , jtag_select_get               , jtag_select_set           , JTAG_SELECT);
#endif /*ESC_600_JTAG_WANTED*/
/*ESC600_SFP_attributes*/
static SENSOR_DEVICE_ATTR(sfp_select                , S_IRUGO | S_IWUSR , sfp_select_get                , sfp_select_set            , SFP_SELECT);
static SENSOR_DEVICE_ATTR(sfp_insert                , S_IRUGO           , sfp_insert_get                , NULL                      , SFP_INSERT);
static SENSOR_DEVICE_ATTR(sfp_tx_disable            , S_IRUGO | S_IWUSR , sfp_tx_get                    , sfp_tx_set                , SFP_TX_DISABLE);
static SENSOR_DEVICE_ATTR(sfp_rx_loss               , S_IRUGO           , sfp_rx_get                    , NULL                      , SFP_RX_LOSS);
/*ESC600_Mask_attributes*/
#ifdef ESC_600_STAT_WANTED
static SENSOR_DEVICE_ATTR(sersor_status_mask_all    , S_IRUGO           , sersor_status_mask_all_get    , NULL                      , SENSOR_STATUS_MASK);
static SENSOR_DEVICE_ATTR(sersor_status_mask_1      , S_IRUGO | S_IWUSR , sersor_status_mask_get        , sersor_status_mask_set    , 1);
static SENSOR_DEVICE_ATTR(sersor_status_mask_2      , S_IRUGO | S_IWUSR , sersor_status_mask_get        , sersor_status_mask_set    , 2);
static SENSOR_DEVICE_ATTR(sersor_status_mask_3      , S_IRUGO | S_IWUSR , sersor_status_mask_get        , sersor_status_mask_set    , 3);
static SENSOR_DEVICE_ATTR(sersor_status_mask_4      , S_IRUGO | S_IWUSR , sersor_status_mask_get        , sersor_status_mask_set    , 4);
static SENSOR_DEVICE_ATTR(sersor_status_mask_5      , S_IRUGO | S_IWUSR , sersor_status_mask_get        , sersor_status_mask_set    , 5);
static SENSOR_DEVICE_ATTR(sersor_status_mask_6      , S_IRUGO | S_IWUSR , sersor_status_mask_get        , sersor_status_mask_set    , 6);
#endif /*ESC_600_STAT_WANTED*/
#ifdef ESC_600_ALARM_WANTED
static SENSOR_DEVICE_ATTR(switch_alarm_mask_all     , S_IRUGO           , switch_alarm_mask_all_get     , NULL                      , SWITCH_ALARM_MASK);
static SENSOR_DEVICE_ATTR(switch_alarm_mask_1       , S_IRUGO | S_IWUSR , switch_alarm_mask_get         , switch_alarm_mask_set     , 1);
static SENSOR_DEVICE_ATTR(switch_alarm_mask_2       , S_IRUGO | S_IWUSR , switch_alarm_mask_get         , switch_alarm_mask_set     , 2);
static SENSOR_DEVICE_ATTR(switch_alarm_mask_3       , S_IRUGO | S_IWUSR , switch_alarm_mask_get         , switch_alarm_mask_set     , 3);
static SENSOR_DEVICE_ATTR(switch_alarm_mask_4       , S_IRUGO | S_IWUSR , switch_alarm_mask_get         , switch_alarm_mask_set     , 4);
#endif /*ESC_600_ALARM_WANTED*/
#ifdef ESC_600_INT_WANTED
static SENSOR_DEVICE_ATTR(sersor_int_mask_all       , S_IRUGO           , sersor_int_mask_all_get       , NULL                      , SENSOR_INT_MASK);
static SENSOR_DEVICE_ATTR(sersor_int_mask_1         , S_IRUGO | S_IWUSR , sersor_int_mask_get           , sersor_int_mask_set       , 1);
static SENSOR_DEVICE_ATTR(sersor_int_mask_2         , S_IRUGO | S_IWUSR , sersor_int_mask_get           , sersor_int_mask_set       , 2);
static SENSOR_DEVICE_ATTR(switch_int_mask_all       , S_IRUGO           , switch_int_mask_all_get       , NULL                      , SWITCH_INT_MASK);
static SENSOR_DEVICE_ATTR(phy_module_ins_mask       , S_IRUGO | S_IWUSR , switch_int_mask_get           , switch_int_mask_set       , 1);
static SENSOR_DEVICE_ATTR(phy_module_int_mask       , S_IRUGO | S_IWUSR , switch_int_mask_get           , switch_int_mask_set       , 2);
static SENSOR_DEVICE_ATTR(phy_module_power_mask     , S_IRUGO | S_IWUSR , switch_int_mask_get           , switch_int_mask_set       , 3);
static SENSOR_DEVICE_ATTR(cpld2_int_mask            , S_IRUGO | S_IWUSR , switch_int_mask_get           , switch_int_mask_set       , 4);
static SENSOR_DEVICE_ATTR(io_board_int_mask         , S_IRUGO | S_IWUSR , switch_int_mask_get           , switch_int_mask_set       , 5);
static SENSOR_DEVICE_ATTR(fan_error_mask            , S_IRUGO | S_IWUSR , switch_int_mask_get           , switch_int_mask_set       , 6);
static SENSOR_DEVICE_ATTR(psu_int_mask              , S_IRUGO | S_IWUSR , int_mask_get                  , int_mask_set              , 1);
static SENSOR_DEVICE_ATTR(sfp_loss_int_mask         , S_IRUGO | S_IWUSR , int_mask_get                  , int_mask_set              , 2);
static SENSOR_DEVICE_ATTR(sfp_abs_int_mask          , S_IRUGO | S_IWUSR , int_mask_get                  , int_mask_set              , 3);
#endif /*ESC_600_INT_WANTED*/
/*ESC600_Fan_attributes*/
static SENSOR_DEVICE_ATTR(fan_status                , S_IRUGO           , fan_status_get                , NULL                      , FAN_STATUS);
static SENSOR_DEVICE_ATTR(fan_insert                , S_IRUGO           , fan_insert_get                , NULL                      , FAN_INSERT);
static SENSOR_DEVICE_ATTR(fan_power                 , S_IRUGO           , fan_power_get                 , NULL                      , FAN_POWER);
static SENSOR_DEVICE_ATTR(fan_direct                , S_IRUGO           , fan_direct_get                , NULL                      , FAN_DIRECT);
static SENSOR_DEVICE_ATTR(fan_speed_rpm             , S_IRUGO           , fan_status_get                , NULL                      , FAN_SPEED_RPM);
/*ESC600_USB_attributes*/
#ifdef USB_CTRL_WANTED
static SENSOR_DEVICE_ATTR(usb_power                 , S_IRUGO | S_IWUSR , usb_power_get                 , usb_power_set             , USB_POWER);
#endif /*USB_CTRL_WANTED*/
/*ESC600_LED_attributes*/
#ifdef LED_CTRL_WANTED
static SENSOR_DEVICE_ATTR(led_ctrl                  , S_IRUGO | S_IWUSR , led_ctrl_get                  , led_ctrl_set              , LED_CTRL);
static SENSOR_DEVICE_ATTR(sys_led                   , S_IRUGO | S_IWUSR , sys_led_get                   , sys_led_set               , SYS_LED);
static SENSOR_DEVICE_ATTR(switch_led_all            , S_IRUGO | S_IWUSR , switch_led_all_get            , switch_led_all_set        , SWITCH_LED);
#ifdef LED_L3_CTRL_WANTED
static SENSOR_DEVICE_ATTR(switch_led_3_1            , S_IRUGO | S_IWUSR , switch_led_3_get              , switch_led_3_set          , 1);
static SENSOR_DEVICE_ATTR(switch_led_3_2            , S_IRUGO | S_IWUSR , switch_led_3_get              , switch_led_3_set          , 2);
static SENSOR_DEVICE_ATTR(switch_led_3_3            , S_IRUGO | S_IWUSR , switch_led_3_get              , switch_led_3_set          , 3);
static SENSOR_DEVICE_ATTR(switch_led_3_4            , S_IRUGO | S_IWUSR , switch_led_3_get              , switch_led_3_set          , 4);
#endif /*LED_L3_CTRL_WANTED*/
static SENSOR_DEVICE_ATTR(switch_led_4_1            , S_IRUGO | S_IWUSR , switch_led_4_get              , switch_led_4_set          , 1);
static SENSOR_DEVICE_ATTR(switch_led_4_2            , S_IRUGO | S_IWUSR , switch_led_4_get              , switch_led_4_set          , 2);
static SENSOR_DEVICE_ATTR(switch_led_4_3            , S_IRUGO | S_IWUSR , switch_led_4_get              , switch_led_4_set          , 3);
static SENSOR_DEVICE_ATTR(switch_led_4_4            , S_IRUGO | S_IWUSR , switch_led_4_get              , switch_led_4_set          , 4);
static SENSOR_DEVICE_ATTR(switch_led_5_1            , S_IRUGO | S_IWUSR , switch_led_5_get              , switch_led_5_set          , 1);
static SENSOR_DEVICE_ATTR(switch_led_5_2            , S_IRUGO | S_IWUSR , switch_led_5_get              , switch_led_5_set          , 2);
static SENSOR_DEVICE_ATTR(switch_led_5_3            , S_IRUGO | S_IWUSR , switch_led_5_get              , switch_led_5_set          , 3);
static SENSOR_DEVICE_ATTR(switch_led_5_4            , S_IRUGO | S_IWUSR , switch_led_5_get              , switch_led_5_set          , 4);
#endif /*LED_CTRL_WANTED*/
/*ESC600_Reset_attributes*/
static SENSOR_DEVICE_ATTR(shutdown_sys              , S_IRUGO | S_IWUSR , shutdown_sys_get              , shutdown_sys_set          , SYS_SHUTDOWN);
static SENSOR_DEVICE_ATTR(reset_sys                 , S_IRUGO | S_IWUSR , NULL                          , reset_sys_set             , SYS_RESET);
/*ESC600_Sensor_attributes*/
#ifdef ESC_600_STAT_WANTED
static SENSOR_DEVICE_ATTR(sensor_status             , S_IRUGO           , sensor_status_get             , NULL                      , SENSOR_STATUS);
#endif /*ESC_600_STAT_WANTED*/
#ifdef ESC_600_ALARM_WANTED
static SENSOR_DEVICE_ATTR(switch_alarm              , S_IRUGO           , switch_alarm_get              , NULL                      , SWITCH_ALARM);
#endif /*ESC_600_ALARM_WANTED*/
static SENSOR_DEVICE_ATTR(switch_button             , S_IRUGO           , switch_button_get             , NULL                      , SWITCH_BUTTON);
#ifdef ESC_600_BMC_WANTED
static SENSOR_DEVICE_ATTR(sensor_temp               , S_IRUGO           , themal_temp_get               , NULL                      , SENSOR_TEMP);
static SENSOR_DEVICE_ATTR(module_temp               , S_IRUGO           , module_temp_get               , NULL                      , MODULE_TEMP);
static SENSOR_DEVICE_ATTR(mac_temp                  , S_IRUGO           , mac_temp_get                  , NULL                      , MAC_TEMP);
static SENSOR_DEVICE_ATTR(bmc_present               , S_IRUGO           , bmc_module_detect             , NULL                      , BMC_DETECT);
#endif /*ESC_600_BMC_WANTED*/
/*ESC600_INT_attributes*/
#ifdef ESC_600_INT_WANTED
static SENSOR_DEVICE_ATTR(sensor_int                , S_IRUGO           , sensor_int_get                , NULL                      , SENSOR_INT);
static SENSOR_DEVICE_ATTR(switch_int                , S_IRUGO           , switch_int_get                , NULL                      , SWITCH_INT);
static SENSOR_DEVICE_ATTR(sfp_int                   , S_IRUGO           , sfp_int_get                   , NULL                      , SFP_INT);
static SENSOR_DEVICE_ATTR(psu_int                   , S_IRUGO           , psu_int_get                   , NULL                      , PSU_INT);
#endif /*ESC_600_INT_WANTED*/
/*ESC600_Module_attributes*/
static SENSOR_DEVICE_ATTR(module_reset              , S_IRUGO | S_IWUSR , NULL                          , module_reset_set          , MODULE_RESET);
static SENSOR_DEVICE_ATTR(module_insert             , S_IRUGO           , module_insert_get             , NULL                      , MODULE_INSERT);
static SENSOR_DEVICE_ATTR(module_power              , S_IRUGO           , module_power_get              , NULL                      , MODULE_POWER);
static SENSOR_DEVICE_ATTR(module_enable             , S_IRUGO | S_IWUSR , module_enable_get             , module_enable_set         , MODULE_ENABLE);
static SENSOR_DEVICE_ATTR(module_12v_status         , S_IRUGO           , module_12v_status_get         , NULL                      , MODULE_12V_STAT);
/* end of sysfs attributes for SENSOR_DEVICE_ATTR */

/* sysfs attributes for hwmon */
static struct attribute *ESC600_SYS_attributes[] =
{
#ifdef ESC_600_BMC_WANTED
    &sensor_dev_attr_bmc_present.dev_attr.attr,
#endif /*ESC_600_BMC_WANTED*/
    &sensor_dev_attr_cpld_version.dev_attr.attr,
#ifdef WDT_CTRL_WANTED
    &sensor_dev_attr_wdt_ctrl.dev_attr.attr,
#endif
#ifdef EEPROM_WP_WANTED
    &sensor_dev_attr_eeprom_wp_ctrl.dev_attr.attr,
#endif
    NULL
};
static struct attribute *ESC600_PSU_attributes[] =
{
    &sensor_dev_attr_psu_present.dev_attr.attr,
    &sensor_dev_attr_psu_status.dev_attr.attr,
#ifdef ESC_600_BMC_WANTED
    &sensor_dev_attr_psu_module_1.dev_attr.attr,
    &sensor_dev_attr_psu_module_2.dev_attr.attr,
    &sensor_dev_attr_psu_module_3.dev_attr.attr,
    &sensor_dev_attr_psu_module_4.dev_attr.attr,
    &sensor_dev_attr_dc_chip_switch.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_1.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_2.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_3.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_4.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_5.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_6.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_7.dev_attr.attr,
    &sensor_dev_attr_dc_chip_slot_8.dev_attr.attr,
#endif /*ESC_600_BMC_WANTED*/
    NULL
};

#ifdef ESC_600_JTAG_WANTED
static struct attribute *ESC600_JTAG_attributes[] =
{
    &sensor_dev_attr_jtag_select.dev_attr.attr,
    NULL
};
#endif

static struct attribute *ESC600_SFP_attributes[] =
{
    &sensor_dev_attr_sfp_select.dev_attr.attr,
    &sensor_dev_attr_sfp_insert.dev_attr.attr,
    &sensor_dev_attr_sfp_tx_disable.dev_attr.attr,
    &sensor_dev_attr_sfp_rx_loss.dev_attr.attr,
    NULL
};

static struct attribute *ESC600_Mask_attributes[] =
{
#ifdef ESC_600_STAT_WANTED
    &sensor_dev_attr_sersor_status_mask_all.dev_attr.attr,
    &sensor_dev_attr_sersor_status_mask_1.dev_attr.attr,
    &sensor_dev_attr_sersor_status_mask_2.dev_attr.attr,
    &sensor_dev_attr_sersor_status_mask_3.dev_attr.attr,
    &sensor_dev_attr_sersor_status_mask_4.dev_attr.attr,
    &sensor_dev_attr_sersor_status_mask_5.dev_attr.attr,
    &sensor_dev_attr_sersor_status_mask_6.dev_attr.attr,
#endif /*ESC_600_STAT_WANTED*/
#ifdef ESC_600_ALARM_WANTED
    &sensor_dev_attr_switch_alarm_mask_all.dev_attr.attr,
    &sensor_dev_attr_switch_alarm_mask_1.dev_attr.attr,
    &sensor_dev_attr_switch_alarm_mask_2.dev_attr.attr,
    &sensor_dev_attr_switch_alarm_mask_3.dev_attr.attr,
    &sensor_dev_attr_switch_alarm_mask_4.dev_attr.attr,
#endif /*ESC_600_ALARM_WANTED*/
#ifdef ESC_600_INT_WANTED
    &sensor_dev_attr_sersor_int_mask_all.dev_attr.attr,
    &sensor_dev_attr_sersor_int_mask_1.dev_attr.attr,
    &sensor_dev_attr_sersor_int_mask_2.dev_attr.attr,
    &sensor_dev_attr_switch_int_mask_all.dev_attr.attr,
    &sensor_dev_attr_phy_module_ins_mask.dev_attr.attr,
    &sensor_dev_attr_phy_module_int_mask.dev_attr.attr,
    &sensor_dev_attr_phy_module_power_mask.dev_attr.attr,
    &sensor_dev_attr_cpld2_int_mask.dev_attr.attr,
    &sensor_dev_attr_io_board_int_mask.dev_attr.attr,
    &sensor_dev_attr_fan_error_mask.dev_attr.attr,
    &sensor_dev_attr_psu_int_mask.dev_attr.attr,
    &sensor_dev_attr_sfp_loss_int_mask.dev_attr.attr,
    &sensor_dev_attr_sfp_abs_int_mask.dev_attr.attr,
#endif /*ESC_600_INT_WANTED*/
    NULL
};

static struct attribute *ESC600_Fan_attributes[] =
{
    &sensor_dev_attr_fan_status.dev_attr.attr,
    &sensor_dev_attr_fan_insert.dev_attr.attr,
    &sensor_dev_attr_fan_power.dev_attr.attr,
    &sensor_dev_attr_fan_direct.dev_attr.attr,
    &sensor_dev_attr_fan_speed_rpm.dev_attr.attr,
    NULL
};

#ifdef USB_CTRL_WANTED
static struct attribute *ESC600_USB_attributes[] =
{
    &sensor_dev_attr_usb_power.dev_attr.attr,
    NULL
};
#endif /*USB_CTRL_WANTED*/

#ifdef LED_CTRL_WANTED
static struct attribute *ESC600_LED_attributes[] =
{

    &sensor_dev_attr_led_ctrl.dev_attr.attr,
    &sensor_dev_attr_sys_led.dev_attr.attr,
    &sensor_dev_attr_switch_led_all.dev_attr.attr,
#ifdef LED_L3_CTRL_WANTED
    &sensor_dev_attr_switch_led_3_1.dev_attr.attr,
    &sensor_dev_attr_switch_led_3_2.dev_attr.attr,
    &sensor_dev_attr_switch_led_3_3.dev_attr.attr,
    &sensor_dev_attr_switch_led_3_4.dev_attr.attr,
#endif /*LED_L3_CTRL_WANTED*/
    &sensor_dev_attr_switch_led_4_1.dev_attr.attr,
    &sensor_dev_attr_switch_led_4_2.dev_attr.attr,
    &sensor_dev_attr_switch_led_4_3.dev_attr.attr,
    &sensor_dev_attr_switch_led_4_4.dev_attr.attr,
    &sensor_dev_attr_switch_led_5_1.dev_attr.attr,
    &sensor_dev_attr_switch_led_5_2.dev_attr.attr,
    &sensor_dev_attr_switch_led_5_3.dev_attr.attr,
    &sensor_dev_attr_switch_led_5_4.dev_attr.attr,
    NULL
};
#endif

static struct attribute *ESC600_Reset_attributes[] =
{
    &sensor_dev_attr_shutdown_sys.dev_attr.attr,
    &sensor_dev_attr_reset_sys.dev_attr.attr,
    NULL
};

static struct attribute *ESC600_Sensor_attributes[] =
{
#ifdef ESC_600_STAT_WANTED
    &sensor_dev_attr_sensor_status.dev_attr.attr,
#endif /*ESC_600_STAT_WANTED*/
#ifdef ESC_600_ALARM_WANTED
    &sensor_dev_attr_switch_alarm.dev_attr.attr,
#endif /*ESC_600_ALARM_WANTED*/
    &sensor_dev_attr_switch_button.dev_attr.attr,
#ifdef ESC_600_BMC_WANTED
    &sensor_dev_attr_sensor_temp.dev_attr.attr,
    &sensor_dev_attr_module_temp.dev_attr.attr,
    &sensor_dev_attr_mac_temp.dev_attr.attr,
#endif /*ESC_600_BMC_WANTED*/
    NULL
}; 

#ifdef ESC_600_INT_WANTED
static struct attribute *ESC600_INT_attributes[] =
{
    &sensor_dev_attr_sensor_int.dev_attr.attr,
    &sensor_dev_attr_switch_int.dev_attr.attr,
    &sensor_dev_attr_sfp_int.dev_attr.attr,
    &sensor_dev_attr_psu_int.dev_attr.attr,
    NULL
};
#endif

static struct attribute *ESC600_Module_attributes[] =
{
    &sensor_dev_attr_module_reset.dev_attr.attr,
    &sensor_dev_attr_module_insert.dev_attr.attr,
    &sensor_dev_attr_module_power.dev_attr.attr,
    &sensor_dev_attr_module_enable.dev_attr.attr,
    &sensor_dev_attr_module_12v_status.dev_attr.attr,
    NULL
};
/* end of sysfs attributes for hwmon */

/* struct attribute_group */
static const struct attribute_group ESC600_SYS_group =
{
    .name  = "ESC600_SYS",
    .attrs = ESC600_SYS_attributes,
};

static const struct attribute_group ESC600_PSU_group =
{
    .name  = "ESC600_PSU",
    .attrs = ESC600_PSU_attributes,
};

#ifdef ESC_600_JTAG_WANTED
static const struct attribute_group ESC600_JTAG_group =
{
    .name  = "ESC600_JTAG",
    .attrs = ESC600_JTAG_attributes,
};
#endif

static const struct attribute_group ESC600_SFP_group =
{
    .name  = "ESC600_SFP",
    .attrs = ESC600_SFP_attributes,
};

static const struct attribute_group ESC600_MASK_group =
{
    .name  = "ESC600_MASK",
    .attrs = ESC600_Mask_attributes,
};

static const struct attribute_group ESC600_FAN_group =
{
    .name  = "ESC600_FAN",
    .attrs = ESC600_Fan_attributes,
};

#ifdef USB_CTRL_WANTED
static const struct attribute_group ESC600_USB_group =
{
    .name  = "ESC600_USB",
    .attrs = ESC600_USB_attributes,
};
#endif /*USB_CTRL_WANTED*/

#ifdef LED_CTRL_WANTED
static const struct attribute_group ESC600_LED_group =
{
    .name  = "ESC600_LED",
    .attrs = ESC600_LED_attributes,
};
#endif /*LED_CTRL_WANTED*/

static const struct attribute_group ESC600_Reset_group =
{
    .name  = "ESC600_Reset",
    .attrs = ESC600_Reset_attributes,
};

static const struct attribute_group ESC600_Sensor_group =
{
    .name  = "ESC600_Sensor",
    .attrs = ESC600_Sensor_attributes,
};

#ifdef ESC_600_INT_WANTED
static const struct attribute_group ESC600_INT_group =
{
    .name  = "ESC600_INT",
    .attrs = ESC600_INT_attributes,
};
#endif

static const struct attribute_group ESC600_Module_group =
{
    .name  = "ESC600_Module",
    .attrs = ESC600_Module_attributes,
};
/* end of struct attribute_group */