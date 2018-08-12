#include <linux/init.h>
#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/i2c/pca954x.h>

#define PCA9548_CHANNEL_NUM     8
#define PCA9548_ADAPT_ID_START  10

static struct pca954x_platform_mode i2c_dev_pca9548_platform_mode[PCA9548_CHANNEL_NUM] = {
    [0] = {
        .adap_id = PCA9548_ADAPT_ID_START,
        .deselect_on_exit = 1,
        .class   = 0,
    },
    [1] = {
        .adap_id = PCA9548_ADAPT_ID_START + 1,
        .deselect_on_exit = 1,
        .class   = 0,
    },
    [2] = {
        .adap_id = PCA9548_ADAPT_ID_START + 2,
        .deselect_on_exit = 1,
        .class   = 0,
    },
    [3] = {
        .adap_id = PCA9548_ADAPT_ID_START + 3,
        .deselect_on_exit = 1,
        .class   = 0,
    },
    [4] = {
        .adap_id = PCA9548_ADAPT_ID_START + 4,
        .deselect_on_exit = 1,
        .class   = 0,
    },
    [5] = {
        .adap_id = PCA9548_ADAPT_ID_START + 5,
        .deselect_on_exit = 1,
        .class   = 0,
    },
    [6] = {
        .adap_id = PCA9548_ADAPT_ID_START + 6,
        .deselect_on_exit = 1,
        .class   = 0,
    },
    [7] = {
        .adap_id = PCA9548_ADAPT_ID_START + 7,
        .deselect_on_exit = 1,
        .class   = 0,
    }
};

static struct pca954x_platform_data i2c_dev_pca9548_platform_data = {
    .modes = i2c_dev_pca9548_platform_mode,
    .num_modes = PCA9548_CHANNEL_NUM,
};

static struct i2c_board_info i2c_dev_pca9548 = {
    I2C_BOARD_INFO("pca9548", 0x70),
    .platform_data = &i2c_dev_pca9548_platform_data,
};

static struct i2c_board_info i2c_dev_adt7475 = {
    I2C_BOARD_INFO("adt7470", 0x2F),
};

struct i2c_adapter *i2c_core_master         = NULL; /* i2c-0-cpu */
struct i2c_adapter *i2c_mux_channel_4       = NULL; /* pca9548x-channel 5 */
struct i2c_client  *i2c_client_pca9548x     = NULL;
struct i2c_client  *i2c_client_adt7475      = NULL;

static int e582_48x6q_init(void)
{
    printk(KERN_INFO "install e582_48x6q board dirver...\n");
        
    /* find i2c-core master */
    i2c_core_master = i2c_get_adapter(0);
    if(i2c_core_master == NULL)
    {
        printk(KERN_CRIT "can't find i2c-core bus\n");
        goto err_i2c_core_master;
    }
 
    /* install i2c-mux */
    i2c_client_pca9548x = i2c_new_device(i2c_core_master, &i2c_dev_pca9548);
    if(i2c_client_pca9548x == NULL)
    {
        printk(KERN_INFO "install e582_48x6q board pca9548 failed\n");
        goto install_at24c64;
    }
    
    /* install adt7475 */
    /* find i2c-mux-channel 15 */
    i2c_mux_channel_4 = i2c_get_adapter(PCA9548_ADAPT_ID_START + 4);
    if(i2c_mux_channel_4 == NULL)
    {
        printk(KERN_INFO "install e582_48x6q board adt7470 failed\n");
        goto install_at24c64;
    }
    
    i2c_client_adt7475 = i2c_new_device(i2c_mux_channel_4, &i2c_dev_adt7475);
    if(i2c_client_adt7475 == NULL){
        printk(KERN_INFO "install e582_48x6q board adt7470 failed\n");
        goto install_at24c64;
    }
    
install_at24c64:
    
    printk(KERN_INFO "install e582_48x6q board dirver...ok\n");
    return 0;
    
err_i2c_core_master:
    return -1;
}

static void e582_48x6q_exit(void)
{
    printk(KERN_INFO "uninstall e582_48x6q board dirver...\n");
    
    /* uninstall adt7475 master */
    if(i2c_client_adt7475) {
        i2c_unregister_device(i2c_client_adt7475);
    }
    if(i2c_mux_channel_4) {
        i2c_put_adapter(i2c_mux_channel_4);
    }
    
    /* uninstall i2c-core master */
    if(i2c_client_pca9548x) {
        i2c_unregister_device(i2c_client_pca9548x);
    }
    
    /* uninstall i2c-core master */
    if(i2c_core_master) {
        i2c_put_adapter(i2c_core_master);
    }
}

MODULE_LICENSE("Dual BSD/GPL");
MODULE_AUTHOR("xuwj centecNetworks, Inc");
MODULE_DESCRIPTION("e582-48x6q board driver");
module_init(e582_48x6q_init);
module_exit(e582_48x6q_exit);
