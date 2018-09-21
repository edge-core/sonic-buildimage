/* Copyright (c) 2017 Arista Networks, Inc.
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
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/sysfs.h>
#include <linux/version.h>
#include <linux/hwmon.h>
#include <linux/hwmon-sysfs.h>
#include <linux/delay.h>
#include <linux/leds.h>
#include <linux/gpio.h>
#include <linux/i2c.h>
#include <linux/pci.h>
#include <linux/stat.h>

#include "scd.h"
#include "scd-hwmon.h"

#define SCD_MODULE_NAME "scd-hwmon"

#define SMBUS_REQUEST_OFFSET 0x10
#define SMBUS_CONTROL_STATUS_OFFSET 0x20
#define SMBUS_RESPONSE_OFFSET 0x30

#define RESET_SET_OFFSET 0x00
#define RESET_CLEAR_OFFSET 0x10

#define MASTER_DEFAULT_BUS_COUNT 8
#define MASTER_DEFAULT_MAX_RETRIES 3

#define MAX_CONFIG_LINE_SIZE 100

struct scd_context;

struct scd_master {
   struct scd_context *ctx;
   struct list_head list;

   u32 id;
   u32 req;
   u32 cs;
   u32 resp;
   struct mutex mutex;
   struct list_head bus_list;

   int max_retries;
};

struct bus_params {
   struct list_head list;
   u16 addr;
   u8 t;
   u8 datw;
   u8 datr;
};

const struct bus_params default_bus_params = {
   .t = 1,
   .datw = 3,
   .datr = 3,
};

struct scd_bus {
   struct scd_master *master;
   struct list_head list;

   u32 id;
   struct list_head params;

   struct i2c_adapter adap;
};

#define LED_NAME_MAX_SZ 40
struct scd_led {
   struct scd_context *ctx;
   struct list_head list;

   u32 addr;
   char name[LED_NAME_MAX_SZ];
   struct led_classdev cdev;
};

struct scd_gpio_attribute {
   struct device_attribute dev_attr;
   struct scd_context *ctx;

   u32 addr;
   u32 bit;
   u32 active_low;
};

#define GPIO_NAME_MAX_SZ 50
struct scd_gpio {
   char name[GPIO_NAME_MAX_SZ];
   struct scd_gpio_attribute attr;
   struct list_head list;
};

#define __ATTR_NAME_PTR(_name, _mode, _show, _store) {  \
   .attr = { .name = _name,                             \
             .mode = VERIFY_OCTAL_PERMISSIONS(_mode) }, \
   .show = _show,                                       \
   .store = _store,                                     \
}

#define to_scd_gpio_attr(_dev_attr) \
   container_of(_dev_attr, struct scd_gpio_attribute, dev_attr)

#define SCD_GPIO_ATTR(_name, _mode, _show, _store, _ctx, _addr, _bit, _active_low) \
   { .dev_attr = __ATTR_NAME_PTR(_name, _mode, _show, _store),                     \
     .ctx = _ctx,                                                                  \
     .addr = _addr,                                                                \
     .bit = _bit,                                                                  \
     .active_low = _active_low                                                     \
   }

#define SCD_RW_GPIO_ATTR(_name, _ctx, _addr, _bit, _active_low)                    \
   SCD_GPIO_ATTR(_name, S_IRUGO | S_IWUSR, attribute_gpio_get, attribute_gpio_set, \
                 _ctx, _addr, _bit, _active_low)

#define SCD_RO_GPIO_ATTR(_name, _ctx, _addr, _bit, _active_low) \
   SCD_GPIO_ATTR(_name, S_IRUGO, attribute_gpio_get, NULL,      \
                 _ctx, _addr, _bit, _active_low)

struct scd_reset_attribute {
   struct device_attribute dev_attr;
   struct scd_context *ctx;

   u32 addr;
   u32 bit;
};

#define RESET_NAME_MAX_SZ 50
struct scd_reset {
   char name[RESET_NAME_MAX_SZ];
   struct scd_reset_attribute attr;
   struct list_head list;
};

#define to_scd_reset_attr(_dev_attr) \
   container_of(_dev_attr, struct scd_reset_attribute, dev_attr)

#define SCD_RESET_ATTR(_name, _ctx, _addr, _bit)                                \
   { .dev_attr = __ATTR_NAME_PTR(_name, S_IRUGO | S_IWUSR, attribute_reset_get, \
                                 attribute_reset_set),                          \
     .ctx = _ctx,                                                               \
     .addr = _addr,                                                             \
     .bit = _bit,                                                               \
   }

struct scd_context {
   struct pci_dev *pdev;
   size_t res_size;

   struct list_head list;

   struct mutex mutex;
   bool initialized;

   struct list_head gpio_list;
   struct list_head reset_list;
   struct list_head led_list;
   struct list_head master_list;
};

union request_reg {
   u32 reg;
   struct {
      u32 d:8;
      u32 ss:6;
      u32 reserved1:2;
      u32 dat:2;
      u32 t:2;
      u32 sp:1;
      u32 da:1;
      u32 dod:1;
      u32 st:1;
      u32 bs:4;
      u32 ti:4;
   } __packed;
};

union ctrl_status_reg {
   u32 reg;
   struct {
      u32 reserved1:13;
      u32 foe:1;
      u32 reserved2:17;
      u32 reset:1;
   } __packed;
};

union response_reg {
   u32 reg;
   struct {
      u32 d:8;
      u32 bus_conflict_error:1;
      u32 timeout_error:1;
      u32 ack_error:1;
      u32 flushed:1;
      u32 ti:4;
      u32 ss:6;
      u32 reserved2:9;
      u32 fe:1;
   } __packed;
};

/* locking functions */
static struct mutex scd_hwmon_mutex;

static void module_lock(void)
{
   mutex_lock(&scd_hwmon_mutex);
}

static void module_unlock(void)
{
   mutex_unlock(&scd_hwmon_mutex);
}

static void master_lock(struct scd_master *master)
{
   mutex_lock(&master->mutex);
}

static void master_unlock(struct scd_master *master)
{
   mutex_unlock(&master->mutex);
}

static void scd_lock(struct scd_context *ctx)
{
   mutex_lock(&ctx->mutex);
}

static void scd_unlock(struct scd_context *ctx)
{
   mutex_unlock(&ctx->mutex);
}

/* SMBus functions */
static void smbus_master_write_req(struct scd_master *master,
                                   union request_reg req)
{
   u32 addr = (u32)master->req;
   scd_write_register(master->ctx->pdev, addr, req.reg);
}

static void smbus_master_write_cs(struct scd_master *master,
                                  union ctrl_status_reg cs)
{
   scd_write_register(master->ctx->pdev, master->cs, cs.reg);
}

static union ctrl_status_reg smbus_master_read_cs(struct scd_master *master)
{
   union ctrl_status_reg cs;
   cs.reg = scd_read_register(master->ctx->pdev, master->cs);
   return cs;
}

static union response_reg smbus_master_read_resp(struct scd_master *master)
{
   union response_reg resp;
   u32 retries = 10;

   resp.reg = scd_read_register(master->ctx->pdev, master->resp);

   while (resp.fe && --retries) {
      msleep(10);
      resp.reg = scd_read_register(master->ctx->pdev, master->resp);
   }

   if (resp.fe) {
      scd_dbg("smbus response: fifo still empty after retries");
      resp.reg = 0xffffffff;
   }

   return resp;
}

static s32 smbus_check_resp(union response_reg resp, u32 tid)
{
   const char *error;
   int error_ret = -EIO;

   if (resp.reg == 0xffffffff) {
      error = "fe";
      goto fail;
   }
   if (resp.ack_error) {
      error = "ack";
      goto fail;
   }
   if (resp.timeout_error) {
      error = "timeout";
      goto fail;
   }
   if (resp.bus_conflict_error) {
      error = "conflict";
      goto fail;
   }
   if (resp.flushed) {
      error = "flush";
      goto fail;
   }
   if (resp.ti != tid) {
      error = "tid";
      goto fail;
   }

   return 0;

fail:
   scd_dbg("smbus response: %s error. reg=0x%08x", error, resp.reg);
   return error_ret;
}

static u32 scd_smbus_func(struct i2c_adapter *adapter)
{
   return I2C_FUNC_SMBUS_QUICK | I2C_FUNC_SMBUS_BYTE |
      I2C_FUNC_SMBUS_BYTE_DATA | I2C_FUNC_SMBUS_WORD_DATA |
      I2C_FUNC_SMBUS_I2C_BLOCK | I2C_FUNC_SMBUS_BLOCK_DATA;
}

static void smbus_master_reset(struct scd_master *master)
{
   union ctrl_status_reg cs;
   cs = smbus_master_read_cs(master);
   cs.reset = 1;
   cs.foe = 1;
   smbus_master_write_cs(master, cs);
   mdelay(10);
   cs.reset = 0;
   smbus_master_write_cs(master, cs);
}

static const struct bus_params *get_bus_params(struct scd_bus *bus, u16 addr) {
   const struct bus_params *params = &default_bus_params;
   struct bus_params *params_tmp;

   list_for_each_entry(params_tmp, &bus->params, list) {
      if (params_tmp->addr == addr) {
         params = params_tmp;
         break;
      }
   }

   return params;
}

static s32 scd_smbus_do(struct scd_bus *bus, u16 addr, unsigned short flags,
                        char read_write, u8 command, int size,
                        union i2c_smbus_data *data)
{
   struct scd_master *master = bus->master;
   const struct bus_params *params;
   int i;
   union request_reg req;
   union response_reg resp;
   int ret = 0;
   u32 ss = 0;
   u32 data_offset = 0;

   master_lock(master);

   params = get_bus_params(bus, addr);

   req.reg = 0;
   req.bs = bus->id;
   req.t = params->t;

   switch (size) {
   case I2C_SMBUS_QUICK:
      ss = 1;
      break;
   case I2C_SMBUS_BYTE:
      ss = 2;
      break;
   case I2C_SMBUS_BYTE_DATA:
      if (read_write == I2C_SMBUS_WRITE) {
         ss = 3;
      } else {
         ss = 4;
      }
      break;
   case I2C_SMBUS_WORD_DATA:
      if (read_write == I2C_SMBUS_WRITE) {
         ss = 4;
      } else {
         ss = 5;
      }
      break;
   case I2C_SMBUS_I2C_BLOCK_DATA:
      data_offset = 1;
      if (read_write == I2C_SMBUS_WRITE) {
         ss = 2 + data->block[0];
      } else {
         ss = 3 + data->block[0];
      }
      break;
   case I2C_SMBUS_BLOCK_DATA:
      if (read_write == I2C_SMBUS_WRITE) {
         ss = 3 + data->block[0];
      } else {
         master_unlock(master);
         ret = scd_smbus_do(bus, addr, flags, I2C_SMBUS_READ, command,
                            I2C_SMBUS_BYTE_DATA, data);
         master_lock(master);
         if (ret) {
            goto fail;
         }
         ss = 4 + data->block[0];
      }
      break;
   }

   req.st = 1;
   req.ss = ss;
   req.d = (((addr & 0xff) << 1) | ((ss <= 2) ? read_write : 0));
   req.dod = 1;
   for (i = 0; i < ss; i++) {
      if (i == ss - 1) {
         req.sp = 1;
         if (read_write == I2C_SMBUS_WRITE) {
            req.dat = params->datw;
         } else {
            req.dat = params->datr;
         }
      }
      if (i == 1) {
         req.st = 0;
         req.ss = 0;
         req.d = command;
         if (ss == 2)
            req.dod = ((read_write == I2C_SMBUS_WRITE) ? 1 : 0);
         else
            req.dod = 1;
      }
      if ((i == 2 && read_write == I2C_SMBUS_READ)) {
         req.st = 1;
         req.d = (((addr & 0xff) << 1) | 1);
      }
      if (i >= 2 && (read_write == I2C_SMBUS_WRITE)) {
         req.d = data->block[data_offset + i - 2];
      }
      if ((i == 3 && read_write == I2C_SMBUS_READ)) {
         req.dod = 0;
      }
      req.da = ((!(req.dod || req.sp)) ? 1 : 0);
      smbus_master_write_req(master, req);
      req.ti++;
      req.st = 0;
   }

   req.ti = 0;
   for (i = 0; i < ss; i++) {
      resp = smbus_master_read_resp(master);
      ret = smbus_check_resp(resp, req.ti);
      if (ret) {
         goto fail;
      }
      req.ti++;
      if (read_write == I2C_SMBUS_READ) {
         if (size == I2C_SMBUS_BYTE || size == I2C_SMBUS_BYTE_DATA) {
            if (i == ss - 1) {
               data->byte = resp.d;
            }
         } else if (size == I2C_SMBUS_WORD_DATA) {
            if (i == ss - 2) {
               data->word = resp.d;
            } else if (i == ss - 1) {
               data->word |= (resp.d << 8);
            }
         } else {
            if (i >= 3) {
               if (size == I2C_SMBUS_BLOCK_DATA) {
                  data->block[i - 3] = resp.d;
               } else {
                  data->block[i - 2] = resp.d;
               }
            }
         }
      }
   }

   master_unlock(master);
   return 0;

fail:
   scd_dbg("smbus %s failed addr=0x%02x reg=0x%02x size=0x%02x adapter=\"%s\"\n",
           (read_write) ? "read" : "write", addr, command, size, bus->adap.name);
   smbus_master_reset(master);
   master_unlock(master);
   return ret;
}

static s32 scd_smbus_access(struct i2c_adapter *adap, u16 addr,
                            unsigned short flags, char read_write,
                            u8 command, int size, union i2c_smbus_data *data)
{
   struct scd_bus *bus = i2c_get_adapdata(adap);
   struct scd_master *master = bus->master;
   int retry = 0;
   int ret;

   scd_dbg("smbus %s do addr=0x%02x reg=0x%02x size=0x%02x adapter=\"%s\"\n",
         (read_write) ? "read" : "write", addr, command, size, bus->adap.name);
   do {
      ret = scd_smbus_do(bus, addr, flags, read_write, command, size, data);
      if (ret != -EIO)
         return ret;
      retry++;
      scd_dbg("smbus retrying... %d/%d", retry, master->max_retries);
   } while (retry < master->max_retries);

   scd_warn("smbus %s failed addr=0x%02x reg=0x%02x size=0x%02x "
            "adapter=\"%s\"\n", (read_write) ? "read" : "write",
            addr, command, size, bus->adap.name);

   return -EIO;
}

static struct i2c_algorithm scd_smbus_algorithm = {
   .smbus_xfer    = scd_smbus_access,
   .functionality = scd_smbus_func,
};

static struct list_head scd_list;

static struct scd_context *get_context_for_pdev(struct pci_dev *pdev)
{
   struct scd_context *ctx;

   module_lock();
   list_for_each_entry(ctx, &scd_list, list) {
      if (ctx->pdev == pdev) {
         module_unlock();
         return ctx;
      }
   }
   module_unlock();

   return NULL;
}

static struct scd_context *get_context_for_dev(struct device *dev)
{
   struct scd_context *ctx;

   module_lock();
   list_for_each_entry(ctx, &scd_list, list) {
      if (&ctx->pdev->dev == dev) {
         module_unlock();
         return ctx;
      }
   }
   module_unlock();

   return NULL;
}

static int scd_smbus_bus_add(struct scd_master *master, int id)
{
   struct scd_bus *bus;
   int err;

   bus = kzalloc(sizeof(*bus), GFP_KERNEL);
   if (!bus) {
      return -ENOMEM;
   }

   bus->master = master;
   bus->id = id;
   INIT_LIST_HEAD(&bus->params);
   bus->adap.owner = THIS_MODULE;
   bus->adap.class = 0;
   bus->adap.algo = &scd_smbus_algorithm;
   bus->adap.dev.parent = &master->ctx->pdev->dev;
   scnprintf(bus->adap.name,
             sizeof(bus->adap.name),
             "SCD %s SMBus master %d bus %d", pci_name(master->ctx->pdev),
             master->id, bus->id);
   i2c_set_adapdata(&bus->adap, bus);
   err = i2c_add_adapter(&bus->adap);
   if (err) {
      kfree(bus);
      return err;
   }

   master_lock(master);
   list_add_tail(&bus->list, &master->bus_list);
   master_unlock(master);

   return 0;
}

static void scd_smbus_master_remove(struct scd_master *master)
{
   struct scd_bus *bus;
   struct scd_bus *tmp_bus;
   struct bus_params *params;
   struct bus_params *tmp_params;

   list_for_each_entry_safe(bus, tmp_bus, &master->bus_list, list) {
      i2c_del_adapter(&bus->adap);

      list_for_each_entry_safe(params, tmp_params, &bus->params, list) {
         list_del(&params->list);
         kfree(params);
      }

      list_del(&bus->list);
      kfree(bus);
   }

   smbus_master_reset(master);

   list_del(&master->list);
   kfree(master);
}

static void scd_smbus_remove_all(struct scd_context *ctx)
{
   struct scd_master *master;
   struct scd_master *tmp_master;

   list_for_each_entry_safe(master, tmp_master, &ctx->master_list, list) {
      scd_smbus_master_remove(master);
   }
}

static int scd_smbus_master_add(struct scd_context *ctx, u32 addr, u32 id,
                                u32 bus_count)
{
   struct scd_master *master;
   int err = 0;
   int i;

   list_for_each_entry(master, &ctx->master_list, list) {
      if (master->id == id) {
         return -EEXIST;
      }
   }

   master = kzalloc(sizeof(*master), GFP_KERNEL);
   if (!master) {
      return -ENOMEM;
   }

   master->ctx = ctx;
   mutex_init(&master->mutex);
   master->id = id;
   master->req = addr + SMBUS_REQUEST_OFFSET;
   master->cs = addr + SMBUS_CONTROL_STATUS_OFFSET;
   master->resp = addr + SMBUS_RESPONSE_OFFSET;
   master->max_retries = MASTER_DEFAULT_MAX_RETRIES;
   INIT_LIST_HEAD(&master->bus_list);

   for (i = 0; i < bus_count; ++i) {
      err = scd_smbus_bus_add(master, i);
      if (err) {
         goto fail_bus;
      }
   }

   smbus_master_reset(master);

   list_add_tail(&master->list, &ctx->master_list);

   return 0;

fail_bus:
   scd_smbus_master_remove(master);
   return err;
}

static void led_brightness_set(struct led_classdev *led_cdev,
                               enum led_brightness value)
{
   struct scd_led *led = container_of(led_cdev, struct scd_led, cdev);
   u32 reg;

   switch ((int)value) {
   case 0:
      reg = 0x0006ff00;
      break;
   case 1:
      reg = 0x1006ff00;
      break;
   case 2:
      reg = 0x0806ff00;
      break;
   case 3:
      reg = 0x1806ff00;
      break;
   case 4:
      reg = 0x1406ff00;
      break;
   case 5:
      reg = 0x0C06ff00;
      break;
   case 6:
      reg = 0x1C06ff00;
      break;
   default:
      reg = 0x1806ff00;
      break;
   }
   scd_write_register(led->ctx->pdev, led->addr, reg);
}

static void scd_led_remove_all(struct scd_context *ctx)
{
   struct scd_led *led;
   struct scd_led *led_tmp;

   list_for_each_entry_safe(led, led_tmp, &ctx->led_list, list) {
      led_classdev_unregister(&led->cdev);
      list_del(&led->list);
      kfree(led);
   }
}

static struct scd_led *scd_led_find(struct scd_context *ctx, u32 addr)
{
   struct scd_led *led;

   list_for_each_entry(led, &ctx->led_list, list) {
      if (led->addr == addr)
         return led;
   }
   return NULL;
}

static int scd_led_add(struct scd_context *ctx, const char *name, u32 addr)
{
   struct scd_led *led;
   int ret;

   if (scd_led_find(ctx, addr))
      return -EEXIST;

   led = kzalloc(sizeof(*led), GFP_KERNEL);
   if (!led)
      return -ENOMEM;

   led->ctx = ctx;
   led->addr = addr;
   strncpy(led->name, name, FIELD_SIZEOF(typeof(*led), name));
   INIT_LIST_HEAD(&led->list);

   led->cdev.name = led->name;
   led->cdev.brightness_set = led_brightness_set;

   ret = led_classdev_register(&ctx->pdev->dev, &led->cdev);
   if (ret) {
      kfree(led);
      return ret;
   }

   list_add_tail(&led->list, &ctx->led_list);

   return 0;
}

static ssize_t attribute_gpio_get(struct device *dev,
                                  struct device_attribute *devattr, char *buf)
{
   const struct scd_gpio_attribute *gpio = to_scd_gpio_attr(devattr);
   u32 reg = scd_read_register(gpio->ctx->pdev, gpio->addr);
   u32 res = !!(reg & (1 << gpio->bit));
   res = (gpio->active_low) ? !res : res;
   return sprintf(buf, "%u\n", res);
}

static ssize_t attribute_gpio_set(struct device *dev,
                                  struct device_attribute *devattr,
                                  const char *buf, size_t count)
{
   const struct scd_gpio_attribute *gpio = to_scd_gpio_attr(devattr);
   long value;
   int res;
   u32 reg;

   res = kstrtol(buf, 10, &value);
   if (res < 0)
      return res;

   if (value != 0 && value != 1)
      return -EINVAL;

   reg = scd_read_register(gpio->ctx->pdev, gpio->addr);
   if (gpio->active_low) {
      if (value)
         reg &= ~(1 << gpio->bit);
      else
         reg |= ~(1 << gpio->bit);
   } else {
      if (value)
         reg |= 1 << gpio->bit;
      else
         reg &= ~(1 << gpio->bit);
   }
   scd_write_register(gpio->ctx->pdev, gpio->addr, reg);

   return count;
}

static void scd_gpio_unregister(struct scd_context *ctx, struct scd_gpio *gpio)
{
   sysfs_remove_file(&ctx->pdev->dev.kobj, &gpio->attr.dev_attr.attr);
}

static int scd_gpio_register(struct scd_context *ctx, struct scd_gpio *gpio)
{
   int res;

   res = sysfs_create_file(&ctx->pdev->dev.kobj, &gpio->attr.dev_attr.attr);
   if (res < 0)
      return res;

   list_add_tail(&gpio->list, &ctx->gpio_list);
   return 0;
}

static void scd_gpio_remove_all(struct scd_context *ctx)
{
   struct scd_gpio *tmp_gpio;
   struct scd_gpio *gpio;

   list_for_each_entry_safe(gpio, tmp_gpio, &ctx->gpio_list, list) {
      scd_gpio_unregister(ctx, gpio);
      list_del(&gpio->list);
      kfree(gpio);
   }
}

static ssize_t attribute_reset_get(struct device *dev,
                                   struct device_attribute *devattr, char *buf)
{
   const struct scd_reset_attribute *reset = to_scd_reset_attr(devattr);
   u32 reg = scd_read_register(reset->ctx->pdev, reset->addr);
   u32 res = !!(reg & (1 << reset->bit));
   return sprintf(buf, "%u\n", res);
}

// write 1 -> set, 0 -> clear
static ssize_t attribute_reset_set(struct device *dev,
                                   struct device_attribute *devattr,
                                   const char *buf, size_t count)
{
   const struct scd_reset_attribute *reset = to_scd_reset_attr(devattr);
   u32 offset = RESET_SET_OFFSET;
   long value;
   int res;
   u32 reg;

   res = kstrtol(buf, 10, &value);
   if (res < 0)
      return res;

   if (value != 0 && value != 1)
      return -EINVAL;

   if (!value)
      offset = RESET_CLEAR_OFFSET;

   reg = 1 << reset->bit;
   scd_write_register(reset->ctx->pdev, reset->addr + offset, reg);

   return count;
}

static void scd_reset_unregister(struct scd_context *ctx, struct scd_reset *reset)
{
   sysfs_remove_file(&ctx->pdev->dev.kobj, &reset->attr.dev_attr.attr);
}

static int scd_reset_register(struct scd_context *ctx, struct scd_reset *reset)
{
   int res;

   res = sysfs_create_file(&ctx->pdev->dev.kobj, &reset->attr.dev_attr.attr);
   if (res < 0)
      return res;

   list_add_tail(&reset->list, &ctx->reset_list);
   return 0;
}

static void scd_reset_remove_all(struct scd_context *ctx)
{
   struct scd_reset *tmp_reset;
   struct scd_reset *reset;

   list_for_each_entry_safe(reset, tmp_reset, &ctx->reset_list, list) {
      scd_reset_unregister(ctx, reset);
      list_del(&reset->list);
      kfree(reset);
   }
}

struct gpio_cfg {
   u32 bitpos;
   bool readonly;
   bool active_low;
   const char *name;
};

static int scd_xcvr_add(struct scd_context *ctx, const char *prefix,
                        const struct gpio_cfg *cfgs, size_t gpio_count,
                        u32 addr, u32 id)
{
   int i;
   int err;
   const struct gpio_cfg *cfg;
   struct scd_gpio *gpio;

   for (i = 0; i < gpio_count; ++i) {
      cfg = &cfgs[i];

      gpio = kzalloc(sizeof(*gpio), GFP_KERNEL);
      if (!gpio) {
         err = -ENOMEM;
         goto fail;
      }

      snprintf(gpio->name, FIELD_SIZEOF(typeof(*gpio), name),
               "%s%u_%s", prefix, id, cfg->name);

      if (cfg->readonly)
         gpio->attr = (struct scd_gpio_attribute)SCD_RO_GPIO_ATTR(
                              gpio->name, ctx, addr, cfg->bitpos, cfg->active_low);
      else
         gpio->attr = (struct scd_gpio_attribute)SCD_RW_GPIO_ATTR(
                              gpio->name, ctx, addr, cfg->bitpos, cfg->active_low);

      err = scd_gpio_register(ctx, gpio);
      if (err) {
         kfree(gpio);
         goto fail;
      }
   }

   return 0;

fail:
   if (gpio)
      kfree(gpio);

   while (i--) {
      gpio = list_last_entry(&ctx->gpio_list, struct scd_gpio, list);
      if (gpio)
         list_del(&gpio->list);
   }

   return err;
}

static int scd_xcvr_sfp_add(struct scd_context *ctx, u32 addr, u32 id)
{
   static const struct gpio_cfg sfp_gpios[] = {
      {0, true,  false, "rxlos"},
      {1, true,  false, "txfault"},
      {2, true,  true,  "present"},
      {3, true,  false, "rxlos_changed"},
      {4, true,  false, "txfault_changed"},
      {5, true,  false, "present_changed"},
      {6, false, false, "txdisable"},
      {7, false, false, "rate_select0"},
      {8, false, false, "rate_select1"},
   };

   scd_dbg("sfp %u @ 0x%04x\n", id, addr);
   return scd_xcvr_add(ctx, "sfp", sfp_gpios, ARRAY_SIZE(sfp_gpios), addr, id);
}

static int scd_xcvr_qsfp_add(struct scd_context *ctx, u32 addr, u32 id)
{
   static const struct gpio_cfg qsfp_gpios[] = {
      {0, true,  true,  "interrupt"},
      {2, true,  true,  "present"},
      {3, true,  false, "interrupt_changed"},
      {5, true,  false, "present_changed"},
      {6, false, false, "lp_mode"},
      {7, false, false, "reset"},
      {8, false, true,  "modsel"},
   };

   scd_dbg("qsfp %u @ 0x%04x\n", id, addr);
   return scd_xcvr_add(ctx, "qsfp", qsfp_gpios, ARRAY_SIZE(qsfp_gpios), addr, id);
}

static int scd_gpio_add(struct scd_context *ctx, const char *name,
                        u32 addr, u32 bitpos, bool read_only, bool active_low)
{
   int err;
   struct scd_gpio *gpio;

   gpio = kzalloc(sizeof(*gpio), GFP_KERNEL);
   if (!gpio) {
      return -ENOMEM;
   }

   snprintf(gpio->name, FIELD_SIZEOF(typeof(*gpio), name), name);
   if (read_only)
      gpio->attr = (struct scd_gpio_attribute)SCD_RO_GPIO_ATTR(
                           gpio->name, ctx, addr, bitpos, active_low);
   else
      gpio->attr = (struct scd_gpio_attribute)SCD_RW_GPIO_ATTR(
                           gpio->name, ctx, addr, bitpos, active_low);

   err = scd_gpio_register(ctx, gpio);
   if (err) {
      kfree(gpio);
      return err;
   }

   return 0;
}

static int scd_reset_add(struct scd_context *ctx, const char *name,
                         u32 addr, u32 bitpos)
{
   int err;
   struct scd_reset *reset;

   reset = kzalloc(sizeof(*reset), GFP_KERNEL);
   if (!reset) {
      return -ENOMEM;
   }

   snprintf(reset->name, FIELD_SIZEOF(typeof(*reset), name), name);
   reset->attr = (struct scd_reset_attribute)SCD_RESET_ATTR(
                                                reset->name, ctx, addr, bitpos);

   err = scd_reset_register(ctx, reset);
   if (err) {
      kfree(reset);
      return err;
   }

   return 0;
}

#define PARSE_INT_OR_RETURN(Buf, Tmp, Type, Ptr)        \
   do {                                                 \
      int ___ret = 0;                                   \
      Tmp = strsep(Buf, " ");                           \
      if (!Tmp || !*Tmp) {                              \
         return -EINVAL;                                \
      }                                                 \
      ___ret = kstrto##Type(Tmp, 0, Ptr);               \
      if (___ret) {                                     \
         return ___ret;                                 \
      }                                                 \
   } while(0)

#define PARSE_ADDR_OR_RETURN(Buf, Tmp, Type, Ptr, Size) \
   do {                                                 \
      PARSE_INT_OR_RETURN(Buf, Tmp, Type, Ptr);         \
      if (*(Ptr) > (Size)) {                            \
         return -EINVAL;                                \
      }                                                 \
   } while(0)

#define PARSE_STR_OR_RETURN(Buf, Tmp, Ptr)              \
   do {                                                 \
      Tmp = strsep(Buf, " ");                           \
      if (!Tmp || !*Tmp) {                              \
         return -EINVAL;                                \
      }                                                 \
      Ptr = Tmp;                                        \
   } while(0)

#define PARSE_END_OR_RETURN(Buf, Tmp)                   \
   do {                                                 \
      Tmp = strsep(Buf, " ");                           \
      if (Tmp) {                                        \
         return -EINVAL;                                \
      }                                                 \
   } while(0)


// new_master <addr> <accel_id> <bus_count:8>
static ssize_t parse_new_object_master(struct scd_context *ctx,
                                       char *buf, size_t count)
{
   u32 id;
   u32 addr;
   u32 bus_count = MASTER_DEFAULT_BUS_COUNT;

   const char *tmp;
   int res;

   if (!buf)
      return -EINVAL;

   PARSE_ADDR_OR_RETURN(&buf, tmp, u32, &addr, ctx->res_size);
   PARSE_INT_OR_RETURN(&buf, tmp, u32, &id);

   tmp = strsep(&buf, " ");
   if (tmp && *tmp) {
      res = kstrtou32(tmp, 0, &bus_count);
      if (res)
         return res;
      PARSE_END_OR_RETURN(&buf, tmp);
   }

   res = scd_smbus_master_add(ctx, addr, id, bus_count);
   if (res)
      return res;

   return count;
}

// new_led <addr> <name>
static ssize_t parse_new_object_led(struct scd_context *ctx,
                                    char *buf, size_t count)
{
   u32 addr;
   const char *name;

   const char *tmp;
   int res;

   if (!buf)
      return -EINVAL;

   PARSE_ADDR_OR_RETURN(&buf, tmp, u32, &addr, ctx->res_size);
   PARSE_STR_OR_RETURN(&buf, tmp, name);
   PARSE_END_OR_RETURN(&buf, tmp);

   res = scd_led_add(ctx, name, addr);
   if (res)
      return res;

   return count;
}

enum xcvr_type {
   XCVR_TYPE_SFP,
   XCVR_TYPE_QSFP
};

static ssize_t parse_new_object_xcvr(struct scd_context *ctx, enum xcvr_type type,
                                     char *buf, size_t count)
{
   u32 addr;
   u32 id;

   const char *tmp;
   int res;

   if (!buf)
      return -EINVAL;

   PARSE_ADDR_OR_RETURN(&buf, tmp, u32, &addr, ctx->res_size);
   PARSE_INT_OR_RETURN(&buf, tmp, u32, &id);
   PARSE_END_OR_RETURN(&buf, tmp);

   if (type == XCVR_TYPE_SFP)
      res = scd_xcvr_sfp_add(ctx, addr, id);
   else if (type == XCVR_TYPE_QSFP)
      res = scd_xcvr_qsfp_add(ctx, addr, id);
   else
      res = -EINVAL;

   if (res)
      return res;

   return count;
}

// new_qsfp <addr> <id>
static ssize_t parse_new_object_qsfp(struct scd_context *ctx,
                                     char *buf, size_t count)
{
   return parse_new_object_xcvr(ctx, XCVR_TYPE_QSFP, buf, count);
}

// new_sfp <addr> <id>
static ssize_t parse_new_object_sfp(struct scd_context *ctx,
                                     char *buf, size_t count)
{
   return parse_new_object_xcvr(ctx, XCVR_TYPE_SFP, buf, count);
}

// new_reset <addr> <name> <bitpos>
static ssize_t parse_new_object_reset(struct scd_context *ctx,
                                      char *buf, size_t count)
{
   u32 addr;
   const char *name;
   u32 bitpos;

   const char *tmp;
   int res;

   if (!buf)
      return -EINVAL;

   PARSE_ADDR_OR_RETURN(&buf, tmp, u32, &addr, ctx->res_size);
   PARSE_STR_OR_RETURN(&buf, tmp, name);
   PARSE_INT_OR_RETURN(&buf, tmp, u32, &bitpos);
   PARSE_END_OR_RETURN(&buf, tmp);

   res = scd_reset_add(ctx, name, addr, bitpos);
   if (res)
      return res;

   return count;
}

// new_gpio <addr> <name> <bitpos> <ro> <activeLow>
static ssize_t parse_new_object_gpio(struct scd_context *ctx,
                                     char *buf, size_t count)
{
   u32 addr;
   const char *name;
   u32 bitpos;
   u32 read_only;
   u32 active_low;

   const char *tmp;
   int res;

   if (!buf)
      return -EINVAL;

   PARSE_ADDR_OR_RETURN(&buf, tmp, u32, &addr, ctx->res_size);
   PARSE_STR_OR_RETURN(&buf, tmp, name);
   PARSE_INT_OR_RETURN(&buf, tmp, u32, &bitpos);
   PARSE_INT_OR_RETURN(&buf, tmp, u32, &read_only);
   PARSE_INT_OR_RETURN(&buf, tmp, u32, &active_low);
   PARSE_END_OR_RETURN(&buf, tmp);

   res = scd_gpio_add(ctx, name, addr, bitpos, read_only, active_low);
   if (res)
      return res;

   return count;
}

typedef ssize_t (*new_object_parse_func)(struct scd_context*, char*, size_t);
static struct {
   const char *name;
   new_object_parse_func func;
} funcs[] = {
   { "master", parse_new_object_master },
   { "led",    parse_new_object_led },
   { "qsfp",   parse_new_object_qsfp },
   { "sfp",    parse_new_object_sfp },
   { "reset",  parse_new_object_reset },
   { "gpio",   parse_new_object_gpio },
   { NULL, NULL }
};

static ssize_t parse_new_object(struct scd_context *ctx, const char *buf,
                                size_t count)
{
   char tmp[MAX_CONFIG_LINE_SIZE];
   char *ptr = tmp;
   char *tok;
   int i = 0;
   ssize_t err;

   if (count >= MAX_CONFIG_LINE_SIZE) {
      scd_warn("new_object line is too long\n");
      return -EINVAL;
   }

   strncpy(tmp, buf, count);
   tmp[count] = 0;
   tok = strsep(&ptr, " ");
   if (!tok)
      return -EINVAL;

   while (funcs[i].name) {
      if (!strcmp(tok, funcs[i].name))
         break;
      i++;
   }

   if (!funcs[i].name)
      return -EINVAL;

   err = funcs[i].func(ctx, ptr, count - (ptr - tmp));
   if (err < 0)
      return err;

   return count;
}

typedef ssize_t (*line_parser_func)(struct scd_context *ctx, const char *buf,
   size_t count);

static ssize_t parse_lines(struct scd_context *ctx, const char *buf,
                           size_t count, line_parser_func parser)
{
   ssize_t res;
   size_t left = count;
   const char *nl;

   if (count == 0)
      return 0;

   while (true) {
      nl = strnchr(buf, left, '\n');
      if (!nl)
         nl = buf + left; // points on the \0

      res = parser(ctx, buf, nl - buf);
      if (res < 0)
         return res;
      left -= res;

      buf = nl;
      while (left && *buf == '\n') {
         buf++;
         left--;
      }
      if (!left)
         break;
   }

   return count;
}

static ssize_t new_object(struct device *dev, struct device_attribute *attr,
                          const char *buf, size_t count)
{
   ssize_t res;
   struct scd_context *ctx = get_context_for_dev(dev);

   if (!ctx) {
      return -ENODEV;
   }

   scd_lock(ctx);
   if (ctx->initialized) {
      scd_unlock(ctx);
      return -EBUSY;
   }
   res = parse_lines(ctx, buf, count, parse_new_object);
   scd_unlock(ctx);
   return res;
}

static DEVICE_ATTR(new_object, S_IRUGO|S_IWUSR|S_IWGRP, 0, new_object);

static struct scd_bus *find_scd_bus(struct scd_context *ctx, u16 bus) {
   struct scd_master *master;
   struct scd_bus *scd_bus;

   list_for_each_entry(master, &ctx->master_list, list) {
      list_for_each_entry(scd_bus, &master->bus_list, list) {
         if (scd_bus->adap.nr != bus)
            continue;
         return scd_bus;
      }
   }
   return NULL;
}

static ssize_t set_bus_params(struct scd_context *ctx, u16 bus,
                              struct bus_params *params) {
   struct bus_params *p;
   struct scd_bus *scd_bus = find_scd_bus(ctx, bus);

   if (!scd_bus) {
      scd_err("Cannot find bus %d to add tweak\n", bus);
      return -EINVAL;
   }

   list_for_each_entry(p, &scd_bus->params, list) {
      if (p->addr == params->addr) {
         p->t = params->t;
         p->datw = params->datw;
         p->datr = params->datr;
         return 0;
      }
   }

   p = kzalloc(sizeof(*p), GFP_KERNEL);
   if (!p) {
      return -ENOMEM;
   }

   p->addr = params->addr;
   p->t = params->t;
   p->datw = params->datw;
   p->datr = params->datr;
   list_add_tail(&p->list, &scd_bus->params);
   return 0;
}

static ssize_t parse_smbus_tweak(struct scd_context *ctx, const char *buf,
                                 size_t count)
{
   char buf_copy[MAX_CONFIG_LINE_SIZE];
   struct bus_params params;
   ssize_t err;
   char *ptr = buf_copy;
   const char *tmp;
   u16 bus;

   if (count >= MAX_CONFIG_LINE_SIZE) {
      scd_warn("smbus_tweak line is too long\n");
      return -EINVAL;
   }

   strncpy(buf_copy, buf, count);
   buf_copy[count] = 0;

   PARSE_INT_OR_RETURN(&ptr, tmp, u16, &bus);
   PARSE_INT_OR_RETURN(&ptr, tmp, u16, &params.addr);
   PARSE_INT_OR_RETURN(&ptr, tmp, u8, &params.t);
   PARSE_INT_OR_RETURN(&ptr, tmp, u8, &params.datr);
   PARSE_INT_OR_RETURN(&ptr, tmp, u8, &params.datw);

   err = set_bus_params(ctx, bus, &params);
   if (err == 0)
      return count;
   return err;
}

static ssize_t smbus_tweaks(struct device *dev, struct device_attribute *attr,
                            const char *buf, size_t count)
{
   ssize_t res;
   struct scd_context *ctx = get_context_for_dev(dev);

   if (!ctx) {
      return -ENODEV;
   }

   scd_lock(ctx);
   res = parse_lines(ctx, buf, count, parse_smbus_tweak);
   scd_unlock(ctx);
   return res;
}

static DEVICE_ATTR(smbus_tweaks, S_IRUGO|S_IWUSR|S_IWGRP, 0, smbus_tweaks);

static int scd_ext_hwmon_probe(struct pci_dev *pdev)
{
   struct scd_context *ctx = get_context_for_pdev(pdev);
   int err;

   if (ctx) {
      scd_warn("this pci device has already been probed\n");
      return -EEXIST;
   }

   ctx = kzalloc(sizeof(*ctx), GFP_KERNEL);
   if (!ctx) {
      return -ENOMEM;
   }

   ctx->pdev = pdev;
   get_device(&pdev->dev);
   INIT_LIST_HEAD(&ctx->list);

   ctx->initialized = false;
   mutex_init(&ctx->mutex);

   ctx->res_size = scd_resource_len(pdev);

   INIT_LIST_HEAD(&ctx->led_list);
   INIT_LIST_HEAD(&ctx->master_list);
   INIT_LIST_HEAD(&ctx->gpio_list);
   INIT_LIST_HEAD(&ctx->reset_list);

   kobject_get(&pdev->dev.kobj);
   err = sysfs_create_file(&pdev->dev.kobj, &dev_attr_new_object.attr);
   if (err) {
      goto fail_sysfs;
   }

   err = sysfs_create_file(&pdev->dev.kobj, &dev_attr_smbus_tweaks.attr);
   if (err) {
      sysfs_remove_file(&pdev->dev.kobj, &dev_attr_new_object.attr);
      goto fail_sysfs;
   }

   module_lock();
   list_add_tail(&ctx->list, &scd_list);
   module_unlock();

   return 0;

fail_sysfs:
   kobject_put(&pdev->dev.kobj);
   kfree(ctx);
   put_device(&pdev->dev);

   return err;
}

static void scd_ext_hwmon_remove(struct pci_dev *pdev)
{
   struct scd_context *ctx = get_context_for_pdev(pdev);

   if (!ctx) {
      return;
   }

   scd_info("removing scd components\n");

   scd_lock(ctx);
   scd_smbus_remove_all(ctx);
   scd_led_remove_all(ctx);
   scd_gpio_remove_all(ctx);
   scd_reset_remove_all(ctx);
   scd_unlock(ctx);

   module_lock();
   list_del(&ctx->list);
   module_unlock();

   sysfs_remove_file(&pdev->dev.kobj, &dev_attr_new_object.attr);
   sysfs_remove_file(&pdev->dev.kobj, &dev_attr_smbus_tweaks.attr);

   kfree(ctx);

   kobject_put(&pdev->dev.kobj);
   put_device(&pdev->dev);
}

static int scd_ext_hwmon_init_trigger(struct pci_dev *pdev)
{
   struct scd_context *ctx = get_context_for_pdev(pdev);

   if (!ctx) {
      return -ENODEV;
   }

   scd_lock(ctx);
   ctx->initialized = true;
   scd_unlock(ctx);
   return 0;
}

static struct scd_ext_ops scd_hwmon_ops = {
   .probe  = scd_ext_hwmon_probe,
   .remove = scd_ext_hwmon_remove,
   .init_trigger = scd_ext_hwmon_init_trigger,
};

static int __init scd_hwmon_init(void)
{
   int err = 0;

   scd_info("loading scd hwmon driver\n");
   mutex_init(&scd_hwmon_mutex);
   INIT_LIST_HEAD(&scd_list);

   err = scd_register_ext_ops(&scd_hwmon_ops);
   if (err) {
      scd_warn("scd_register_ext_ops failed\n");
      return err;
   }

   return err;
}

static void __exit scd_hwmon_exit(void)
{
   scd_info("unloading scd hwmon driver\n");
   scd_unregister_ext_ops();
}

module_init(scd_hwmon_init);
module_exit(scd_hwmon_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Arista Networks");
MODULE_DESCRIPTION("SCD component driver");
