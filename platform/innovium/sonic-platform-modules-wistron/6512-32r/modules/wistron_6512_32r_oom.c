#include <linux/module.h>
#include <linux/jiffies.h>
#include <linux/i2c.h>
#include <linux/hwmon.h>
#include <linux/hwmon-sysfs.h>
#include <linux/err.h>
#include <linux/mutex.h>
#include <linux/sysfs.h>
#include <linux/slab.h>
#include <linux/delay.h>
#include <linux/dmi.h>

/* QSFP-DD: page0 (low page + high page (128+128 byte)), page 2 (high page (128 byte)), page11 (high page (128 byte))*/
#define EEPROM_DATA_SIZE        256

/* Addresses scanned */
static const unsigned short normal_i2c[] = { I2C_CLIENT_END };
#define MAX_PORT_NAME_LEN       20

enum sysfs_fan_attributes {
	OOM_LP_MODE,
	OOM_TEMP,
	OOM_EEPROM1,
	OOM_EEPROM2,
	OOM_PORT_NAME,
	OOM_ATTR_MAX
};

/* Each client has this additional data */
struct wistron_oom_data {
	struct device   *hwmon_dev;
	struct mutex    lock;
	u8              index;
	int             lp_mode;
	int             temp;
	unsigned char   eeprom1[EEPROM_DATA_SIZE];
	unsigned char   eeprom2[EEPROM_DATA_SIZE];
	char            port_name[MAX_PORT_NAME_LEN];
};

/* sysfs attributes for hwmon */
static ssize_t get_oom_value(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t set_oom_value(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t get_oom_info1(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t set_oom_info1(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t get_oom_info2(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t set_oom_info2(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static ssize_t get_port_name(struct device *dev, struct device_attribute *da, char *buf);
static ssize_t set_port_name(struct device *dev, struct device_attribute *da, const char *buf, size_t count);
static SENSOR_DEVICE_ATTR(lp_mode, S_IWUSR | S_IRUGO, get_oom_value, set_oom_value, OOM_LP_MODE);
static SENSOR_DEVICE_ATTR(temp, S_IWUSR | S_IRUGO, get_oom_value, set_oom_value, OOM_TEMP);
static SENSOR_DEVICE_ATTR(eeprom1, S_IWUSR | S_IRUGO, get_oom_info1, set_oom_info1, OOM_EEPROM1);
static SENSOR_DEVICE_ATTR(eeprom2, S_IWUSR | S_IRUGO, get_oom_info2, set_oom_info2, OOM_EEPROM2);
static SENSOR_DEVICE_ATTR(port_name, S_IRUGO | S_IWUSR, get_port_name, set_port_name, OOM_PORT_NAME);

static struct attribute *wistron_oom_attributes[] = {
	&sensor_dev_attr_lp_mode.dev_attr.attr,
	&sensor_dev_attr_temp.dev_attr.attr,
	&sensor_dev_attr_eeprom1.dev_attr.attr,
	&sensor_dev_attr_eeprom2.dev_attr.attr,
	&sensor_dev_attr_port_name.dev_attr.attr,
	NULL
};

static ssize_t get_oom_value(struct device *dev, struct device_attribute *da, char *buf)
{
	struct sensor_device_attribute  *attr = to_sensor_dev_attr(da);
	struct i2c_client               *client = to_i2c_client(dev);
	struct wistron_oom_data      	*data = i2c_get_clientdata(client);
	int                             value = 0;

	mutex_lock(&data->lock);
	if (attr->index == OOM_LP_MODE)
		value = data->lp_mode;
	else
		value = data->temp;

	mutex_unlock(&data->lock);
	return sprintf(buf, "%d", value);
}

static ssize_t set_oom_value(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
	struct sensor_device_attribute  *attr = to_sensor_dev_attr(da);
	struct i2c_client               *client = to_i2c_client(dev);
	struct wistron_oom_data      	*data = i2c_get_clientdata(client);
	int                             error, value;

	error = kstrtoint(buf, 10, &value);
	if (error) {
		printk("oom_set_value error=%d\n", error);
		return error;
	}

	mutex_lock(&data->lock);
	if (attr->index == OOM_LP_MODE)
		data->lp_mode = value;
	else
		data->temp = value;

	mutex_unlock(&data->lock);
	return count;
}

static ssize_t get_oom_info1(struct device *dev, struct device_attribute *da, char *buf)
{
	struct i2c_client           *client = to_i2c_client(dev);
	struct wistron_oom_data  	*data = i2c_get_clientdata(client);

	mutex_lock(&data->lock);
	memcpy(buf, data->eeprom1, EEPROM_DATA_SIZE);
	mutex_unlock(&data->lock);

	return EEPROM_DATA_SIZE;
}

static ssize_t set_oom_info1(struct device *dev, struct device_attribute *da, const char *buf, size_t size)
{
	struct i2c_client           *client = to_i2c_client(dev);
	struct wistron_oom_data  	*data = i2c_get_clientdata(client);
	int                         i = 0, j = 0, k = 0;
	unsigned char               str[3];
	unsigned int                val;

	mutex_lock(&data->lock);
	memset(data->eeprom1, 0xFF, EEPROM_DATA_SIZE);
	memset(str, 0x0, 3);

	if (strlen(buf) >= EEPROM_DATA_SIZE) {
		for (i=0; i < strlen(buf) ; i++) {
			for (j = 0; j < 2; j++) {
				str[j] = buf[i + j];
			}

			sscanf(str, "%x", &val);

			i = j + i - 1;

			if (k >= EEPROM_DATA_SIZE)
				break;

			data->eeprom1[k] = (unsigned char)val;
			k++;
		}
	}

	mutex_unlock(&data->lock);

	return size;
}

static ssize_t get_oom_info2(struct device *dev, struct device_attribute *da, char *buf)
{
	struct i2c_client           *client = to_i2c_client(dev);
	struct wistron_oom_data  	*data = i2c_get_clientdata(client);

	mutex_lock(&data->lock);
	memcpy(buf, data->eeprom2, EEPROM_DATA_SIZE);
	mutex_unlock(&data->lock);

	return EEPROM_DATA_SIZE;
}

static ssize_t set_oom_info2(struct device *dev, struct device_attribute *da, const char *buf, size_t size)
{
	struct i2c_client           *client = to_i2c_client(dev);
	struct wistron_oom_data  	*data = i2c_get_clientdata(client);
	int                         i = 0, j = 0, k = 0;
	unsigned char               str[3];
	unsigned int                val;

	mutex_lock(&data->lock);
	memset(data->eeprom2, 0xFF, EEPROM_DATA_SIZE);
	memset(str, 0x0, 3);

	if (strlen(buf) >= EEPROM_DATA_SIZE) {
		for (i = 0; i < strlen(buf) ; i++) {
			for (j = 0; j < 2; j++) {
				str[j] = buf[i + j];
			}

			sscanf(str, "%x", &val);

			i = j + i - 1;
			if (k >= EEPROM_DATA_SIZE)
				break;

			data->eeprom2[k]=(unsigned char)val;
			k++;
		}
	}

	mutex_unlock(&data->lock);

	return size;
}

static ssize_t get_port_name(struct device *dev, struct device_attribute *da, char *buf)
{
	struct i2c_client           *client = to_i2c_client(dev);
	struct wistron_oom_data  	*data = i2c_get_clientdata(client);
	ssize_t                     count;

	mutex_lock(&data->lock);
	count = sprintf(buf, "%s", data->port_name);
	mutex_unlock(&data->lock);

	return count;
}

static ssize_t set_port_name(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
	struct i2c_client           *client = to_i2c_client(dev);
	struct wistron_oom_data 	*data = i2c_get_clientdata(client);
	char                        port_name[MAX_PORT_NAME_LEN];

	if (sscanf(buf, "%19s", port_name) != 1)
		return -EINVAL;

	mutex_lock(&data->lock);
	strcpy(data->port_name, port_name);
	mutex_unlock(&data->lock);

	return count;
}

static const struct attribute_group wistron_oom_group = {
	.attrs = wistron_oom_attributes,
};

static int wistron_oom_probe(struct i2c_client *client, const struct i2c_device_id *dev_id)
{
	struct wistron_oom_data *data;
	int status;

	data = kzalloc(sizeof(struct wistron_oom_data), GFP_KERNEL);
	if (!data)
		return -ENOMEM;

	i2c_set_clientdata(client, data);
	data->index = dev_id->driver_data;
	mutex_init(&data->lock);

	dev_info(&client->dev, "device found\n");

	/* Register sysfs hooks */
	status = sysfs_create_group(&client->dev.kobj, &wistron_oom_group);
	if (status)
		goto exit_free;

	data->hwmon_dev = hwmon_device_register_with_info(&client->dev, "wistron_oom", NULL, NULL, NULL);
	if (IS_ERR(data->hwmon_dev)) {
		status = PTR_ERR(data->hwmon_dev);
		goto exit_remove;
	}

	dev_info(&client->dev, "%s: oom '%s'\n", dev_name(data->hwmon_dev), client->name);

	return 0;

exit_remove:
	sysfs_remove_group(&client->dev.kobj, &wistron_oom_group);
exit_free:
	kfree(data);

	return status;
}

static int wistron_oom_remove(struct i2c_client *client)
{
	struct wistron_oom_data *data = i2c_get_clientdata(client);

	hwmon_device_unregister(data->hwmon_dev);
	sysfs_remove_group(&client->dev.kobj, &wistron_oom_group);
	kfree(data);

	return 0;
}

static const struct i2c_device_id wistron_oom_id[] = {
	{ "wistron_oom", 0 },
	{}
};
MODULE_DEVICE_TABLE(i2c, wistron_oom_id);

static struct i2c_driver wistron_oom_driver = {
	.class        = I2C_CLASS_HWMON,
	.driver = {
		.name     = "wistron_oom",
	},
	.probe        = wistron_oom_probe,
	.remove       = wistron_oom_remove,
	.id_table     = wistron_oom_id,
	.address_list = normal_i2c,
};

static int __init wistron_oom_init(void)
{
	return i2c_add_driver(&wistron_oom_driver);
}

static void __exit wistron_oom_exit(void)
{
	i2c_del_driver(&wistron_oom_driver);
}

module_init(wistron_oom_init);
module_exit(wistron_oom_exit);

MODULE_AUTHOR("Wistron");
MODULE_DESCRIPTION("wistron_oom driver");
MODULE_LICENSE("GPL");
