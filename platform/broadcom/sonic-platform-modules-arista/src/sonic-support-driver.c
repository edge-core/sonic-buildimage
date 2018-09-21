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

#include <linux/module.h>
#include <linux/sysfs.h>
#include <linux/version.h>
#include <linux/hwmon.h>
#include <linux/delay.h>
#include <linux/leds.h>
#include <linux/gpio.h>
#include <linux/hwmon.h>
#include <linux/i2c.h>
#include <linux/pci.h>

#include "scd.h"
#include "sonic-support-driver.h"
#include "gpio-kversfix.h"

#define SCD_MODULE_NAME "scd"

#define NUM_SMBUS_MASTERS 8
#define NUM_SMBUS_BUSES 8
#define SMBUS_RETRY_COUNT 3
#define SMBUS_REQUEST_OFFSET 0x10
#define SMBUS_CONTROL_STATUS_OFFSET 0x20
#define SMBUS_RESPONSE_OFFSET 0x30

#define NUM_LEDS 200
#define NUM_GPIO_ADDRS 200
#define NUM_GPIOS 500
#define NUM_RESET_ADDRS 10
#define NUM_RESETS 100
#define RESET_SET_OFFSET 0x00
#define RESET_CLEAR_OFFSET 0x10
#define NAME_LENGTH 50

/* String constants for SFP/QSFP gpio names */
static const char *qsfpGpioSuffixes[] = {
   "_interrupt",
   "_present",
   "_interrupt_changed",
   "_present_changed",
   "_lp_mode",
   "_reset",
   "_modsel"
};

static const char *sfpGpioSuffixes[] = {
   "_rxlos",
   "_txfault",
   "_present",
   "_rxlos_changed",
   "_txfault_changed",
   "_present_changed",
   "_txdisable",
   "_rate_select0",
   "_rate_select1"
};

static const char *psuGpioSuffixes[] = {
   "1_present",
   "2_present"
};

static const char *muxGpioSuffixes[] = {
   "_sfp_qsfp"
};

#define QSFPTYPE 0
#define SFPTYPE 1
#define PSUTYPE 2
#define MUXTYPE 3

static int numQsfpBits = ARRAY_SIZE(qsfpGpioSuffixes);
static int numSfpBits = ARRAY_SIZE(sfpGpioSuffixes);
static int numPsuBits = ARRAY_SIZE(psuGpioSuffixes);
static int numMuxBits = ARRAY_SIZE(muxGpioSuffixes);

struct sonic_master;

struct sonic_bus {
   struct sonic_master *master;
   u32 id;
   struct i2c_adapter adap;
};

struct sonic_master {
   u32 id;
   u32 req;
   u32 cs;
   u32 resp;
   struct mutex mutex;
   struct sonic_bus bus[NUM_SMBUS_BUSES];
};

struct sonic_led {
   u32 addr;
   struct led_classdev cdev;
};


struct sonic_gpio {
   char name[40];
   u32 addr;
   u32 mask;
   u32 ro;
   u32 active_low;
   u32 gpio_type;
   struct gpio_chip chip;
};

struct sonic_reset {
   char name[40];
   u32 addr;
   u32 mask;
   struct gpio_chip chip;
};


struct sonic_master master[NUM_SMBUS_MASTERS];
u32 master_addrs[NUM_SMBUS_MASTERS + 1];

struct sonic_led led[NUM_LEDS];
u32 led_addrs[NUM_LEDS + 1];
char led_names[NUM_LEDS + 1][NAME_LENGTH];
u32 num_led_names;

struct sonic_gpio gpio[NUM_GPIO_ADDRS];
u32 gpio_addrs[NUM_GPIO_ADDRS + 1];
u32 gpio_masks[NUM_GPIO_ADDRS + 1];
u32 gpio_ro[NUM_GPIO_ADDRS + 1];
u32 gpio_type[NUM_GPIO_ADDRS + 1];
u32 gpio_active_low[NUM_GPIO_ADDRS + 1];
char gpio_names[NUM_GPIOS + 1][NAME_LENGTH];
u32 num_gpio_names;

struct sonic_reset reset[NUM_RESET_ADDRS];
u32 reset_addrs[NUM_RESET_ADDRS + 1];
u32 reset_masks[NUM_RESET_ADDRS + 1];
char reset_names[NUM_RESETS + 1][NAME_LENGTH];
u32 num_reset_names;

union Request {
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

union ControlStatus {
   u32 reg;
   struct {
      u32 reserved1:13;
      u32 foe:1;
      u32 reserved2:17;
      u32 reset:1;
   } __packed;
};

union Response {
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

/* Reference to the pci device */
static struct pci_dev *pdev_ref;
/* Flag to indicate initialization */
static int initialized;
/* kobj for the sonic driver */
static struct kobject *sonic_kobject;

/* i2c client */
struct sonic_i2c_client {
   int master;
   int bus;
   int addr;
   struct i2c_client *client;
   struct list_head next;
};

static struct list_head client_list;

static void master_lock(struct sonic_master *pmaster)
{
   mutex_lock(&pmaster->mutex);
}

static void master_unlock(struct sonic_master *pmaster)
{
   mutex_unlock(&pmaster->mutex);
}

static struct mutex sonic_mutex;

static void sonic_lock(void)
{
   mutex_lock(&sonic_mutex);
}

static void sonic_unlock(void)
{
   mutex_unlock(&sonic_mutex);
}

/* SMBus functions */
static void write_req(struct sonic_master *pmaster,
                      union Request req)
{
   u32 addr = (u32)pmaster->req;
   scd_write_register(pdev_ref, addr, req.reg);
}

static void write_cs(struct sonic_master *pmaster,
                     union ControlStatus cs)
{
   scd_write_register(pdev_ref, pmaster->cs, cs.reg);
}

static union ControlStatus read_cs(struct sonic_master *pmaster)
{
   union ControlStatus cs;
   cs.reg = scd_read_register(pdev_ref, pmaster->cs);
   return cs;
}

static union Response read_resp(struct sonic_master *pmaster)
{
   union Response resp;
   u32 retry = 10;

   resp.reg = scd_read_register(pdev_ref, pmaster->resp);
   while (resp.fe && --retry) {
      msleep(10);
      resp.reg = scd_read_register(pdev_ref, pmaster->resp);
   }

   if (resp.fe) {
      sonic_dbg("smbus response: fifo still empty after retries");
      resp.reg = 0xffffffff;
   }

   return resp;
}

static s32 check_resp(struct sonic_master *pmaster,
                      union Response resp, u32 tid)
{
   const char *error;
   int error_ret = -EIO;

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
   sonic_dbg("smbus response: %s error. reg = 0x%08x", error, resp.reg);
   return error_ret;
}

static u32 sonic_smbus_func(struct i2c_adapter *adapter)
{
   return I2C_FUNC_SMBUS_QUICK | I2C_FUNC_SMBUS_BYTE |
      I2C_FUNC_SMBUS_BYTE_DATA | I2C_FUNC_SMBUS_WORD_DATA |
      I2C_FUNC_SMBUS_I2C_BLOCK | I2C_FUNC_SMBUS_BLOCK_DATA;
}

static void smbus_reset(struct sonic_master *pmaster)
{
   union ControlStatus cs;
   cs = read_cs(pmaster);
   cs.reset = 1;
   cs.foe = 1;
   write_cs(pmaster, cs);
   mdelay(10);
   cs.reset = 0;
   write_cs(pmaster, cs);
}

static s32 sonic_smbus_access(struct i2c_adapter *adap, u16 addr,
                            unsigned short flags, char read_write,
                            u8 command, int size, union i2c_smbus_data *data)
{
   int i;
   union Request req;
   union Response resp;
   int ret = 0;
   u32 ss = 0;
   u32 data_offset = 0;
   struct sonic_master *pmaster;
   struct sonic_bus *bus;
   bus = i2c_get_adapdata(adap);
   pmaster = bus->master;

   master_lock(pmaster);

   req.reg = 0;
   req.bs = bus->id;
   req.t = 1;

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
         master_unlock(pmaster);
         ret = sonic_smbus_access(adap, addr, flags, I2C_SMBUS_READ, command,
                                I2C_SMBUS_BYTE_DATA, data);
         master_lock(pmaster);
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
         req.dat = 3;
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
      write_req(pmaster, req);
      req.ti++;
      req.st = 0;
   }

   req.ti = 0;
   for (i = 0; i < ss; i++) {
      resp = read_resp(pmaster);
      ret = check_resp(pmaster, resp, req.ti);
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

   master_unlock(pmaster);
   return 0;

  fail:
   sonic_dbg("smbus %s failed addr=0x%02x reg=0x%02x size=0x%02x adapter=\"%s\"\n",
             (read_write) ? "read" : "write", addr, command, size, adap->name);
   smbus_reset(pmaster);
   master_unlock(pmaster);
   return ret;
}

static s32 sonic_smbus_access_retry(struct i2c_adapter *adap, u16 addr,
                                    unsigned short flags, char read_write,
                                    u8 command, int size,
                                    union i2c_smbus_data *data)
{
   int retry = 0;
   int ret;

   do {
      ret = sonic_smbus_access(adap, addr, flags, read_write, command, size, data);
      if (ret != -EIO)
         return ret;
      retry++;
      sonic_dbg("smbus retrying... %d/%d", retry, SMBUS_RETRY_COUNT);
   } while (retry < SMBUS_RETRY_COUNT);

   sonic_warn("smbus %s failed addr=0x%02x reg=0x%02x size=0x%02x "
              "adapter=\"%s\"\n", (read_write) ? "read" : "write",
              addr, command, size, adap->name);

   return -EIO;
}

static struct i2c_algorithm sonic_smbus_algorithm = {
   .smbus_xfer    = sonic_smbus_access_retry,
   .functionality = sonic_smbus_func,
};

static void smbus_remove(void)
{
   int master_id;
   int bus_id;
   struct sonic_master *pmaster;
   struct sonic_bus *bus;
   struct list_head *ptr;
   struct sonic_i2c_client *entry;

   /* unregister all i2c clients */
   ptr = client_list.next;
   while (ptr != &client_list) {
      entry = list_entry(ptr, struct sonic_i2c_client, next);
      ptr = ptr->next;
      i2c_unregister_device(entry->client);
      kfree(entry);
   }

   for (master_id = 0; master_id < master_addrs[0]; master_id++) {
      pmaster = &master[master_id];
      if (!pmaster) {
         continue;
      }
      for (bus_id = 0; bus_id < ARRAY_SIZE(master->bus); bus_id++) {
         bus = &pmaster->bus[bus_id];
         i2c_del_adapter(&bus->adap);
      }
   }
}

static s32 smbus_init(void)
{
   int master_id;
   int bus_id;
   int err;
   u32 addr;
   struct sonic_master *pmaster;
   struct sonic_bus *bus;

   for (master_id = 0; master_id < master_addrs[0]; master_id++) {
      addr = master_addrs[master_id + 1];
      pmaster = &master[master_id];
      pmaster->id = master_id;
      pmaster->req = addr + SMBUS_REQUEST_OFFSET;
      pmaster->cs = addr + SMBUS_CONTROL_STATUS_OFFSET;
      pmaster->resp = addr + SMBUS_RESPONSE_OFFSET;

      mutex_init(&pmaster->mutex);
      smbus_reset(pmaster);
      for (bus_id = 0; bus_id < ARRAY_SIZE(pmaster->bus); bus_id++) {
         bus = &pmaster->bus[bus_id];
         bus->master = pmaster;
         bus->id = bus_id;
         bus->adap.owner = THIS_MODULE;
         bus->adap.class = 0;
         bus->adap.algo = &sonic_smbus_algorithm;
         bus->adap.dev.parent = &(pdev_ref->dev);
         scnprintf(bus->adap.name,
                   sizeof(bus->adap.name),
                   "SCD SMBus master %d bus %d", pmaster->id, bus->id);
         i2c_set_adapdata(&bus->adap, bus);
         err = i2c_add_adapter(&bus->adap);

         if (err) {
            err = -ENODEV;
            goto fail;
         }
      }
   }
   return 0;

fail:
   smbus_reset(pmaster);
   return err;
}

static void brightness_set(struct led_classdev *led_cdev, enum led_brightness value)
{
   struct sonic_led *pled = container_of(led_cdev, struct sonic_led, cdev);
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
   scd_write_register(pdev_ref, pled->addr, reg);
}

static void led_remove(void)
{
   int i;
   struct sonic_led *pled;
   for (i = 0; i < led_addrs[0]; i++) {
      pled = &led[i];
      if (pled) {
         led_classdev_unregister(&pled->cdev);
      }
   }
}


static s32 led_init(void)
{
   int i;
   struct sonic_led *pled;
   int ret = 0;
   for (i = 0; i < led_addrs[0]; i++) {
      pled = &led[i];
      pled->addr = led_addrs[i + 1];
      pled->cdev.name = led_names[i];
      pled->cdev.brightness_set = brightness_set;
      ret = led_classdev_register(&(pdev_ref->dev), &pled->cdev);
      if (ret) {
         goto fail;
      }
   }

   return 0;

  fail:
   led_remove();
   return ret;
}

static u32 bit_mask(u32 mask, unsigned num)
{
   /* Returns the numth set bit in mask */
   int i;
   for (i = 0; i < num; i++) {
      mask &= mask - 1;
   }
   return mask & ~(mask - 1);
}

static int gpio_get(struct gpio_chip *gc, unsigned gpio_num)
{
   struct sonic_gpio *pgpio = container_of(gc, struct sonic_gpio, chip);
   u32 mask = bit_mask(pgpio->mask, gpio_num);
   return (scd_read_register(pdev_ref, pgpio->addr) & mask);
}

static void gpio_set(struct gpio_chip *gc, unsigned gpio_num, int val)
{
   struct sonic_gpio *pgpio = container_of(gc, struct sonic_gpio, chip);
   u32 mask = bit_mask(pgpio->mask, gpio_num);
   u32 reg = scd_read_register(pdev_ref, pgpio->addr);
   reg ^= (((-val) ^ reg) & mask);
   scd_write_register(pdev_ref, pgpio->addr, reg);
}

static int direction_input(struct gpio_chip *gc, unsigned gpio_num)
{
   return 0;
}

static int direction_output(struct gpio_chip *gc, unsigned gpio_num, int val)
{
   struct sonic_gpio *pgpio = container_of(gc, struct sonic_gpio, chip);
   u32 mask = bit_mask(pgpio->mask, gpio_num);
   if (pgpio->ro & mask) {
      return -EINVAL;
   } else {
      gpio_set(gc, gpio_num, val);
   }
   return 0;
}

static int sonic_gpio_add(struct gpio_chip *chip, u16 hwnum, const char *name,
                          bool direction_may_change, int active_low)
{
   int ret = 0;
   struct gpio_desc *desc;

   sonic_dbg("creating gpio %s hwnum %d\n", name, hwnum);

   desc = gpiochip_request_own_desc(chip, hwnum, name);
   if (IS_ERR(desc)) {
      sonic_err("failed to request desc for GPIO %s\n", name);
      goto fail;
   }

   ret = gpiod_export(desc, direction_may_change);
   if (ret) {
      sonic_err("failed to export GPIO %s\n", name);
      goto fail_export;
   }

   ret = gpiod_export_link(chip->dev, name, desc);
   if (ret) {
      sonic_err("failed to export link for GPIO %s\n", name);
      goto fail_export_link;
   }

   ret = gpiod_sysfs_set_active_low(desc, active_low);
   if (ret) {
      sonic_err("failed to set active_low setting for GPIO %s\n", name);
      goto fail_set_active_mode;
   }

   return ret;

  fail_set_active_mode:
   sysfs_remove_link(&pdev_ref->dev.kobj, name);
  fail_export_link:
   gpiod_unexport(desc);
  fail_export:
   gpiochip_free_own_desc(desc);
  fail:
   return ret;
}

static void sonic_gpio_remove(struct gpio_chip *chip, u16 hwnum, const char *name)
{
   u16 gpio = chip->base + hwnum;
   struct gpio_desc *desc = gpio_to_desc(gpio);

   sysfs_remove_link(&pdev_ref->dev.kobj, name);
   gpiod_unexport(desc);
   gpiochip_free_own_desc(desc);
}

static void gpio_remove(void)
{
   int i;
   int j;
   int k = 0;
   struct sonic_gpio *pgpio;
   u32 addr;
   char gpio_name_buffer[50];

   for (i = 0; i < gpio_addrs[0]; i++) {
      addr = gpio_addrs[i + 1];
      pgpio = &gpio[i];
      if (!pgpio->addr) {
         continue;
      }
      for (j = 0; j < pgpio->chip.ngpio; j++) {

         strcpy(gpio_name_buffer, gpio_names[k]);
         switch (pgpio->gpio_type) {
         case QSFPTYPE:
            strcat(gpio_name_buffer, qsfpGpioSuffixes[j]);
            if (j == numQsfpBits - 1) {
               k++;
            }
            break;
         case SFPTYPE:
            strcat(gpio_name_buffer, sfpGpioSuffixes[j]);
            if (j == numSfpBits - 1) {
               k++;
            }
            break;
         case PSUTYPE:
            strcat(gpio_name_buffer, psuGpioSuffixes[j]);
            if (j == numPsuBits - 1) {
               k++;
            }
            break;
         case MUXTYPE:
            strcat(gpio_name_buffer, muxGpioSuffixes[j]);
            if (j == numMuxBits - 1) {
               k++;
            }
            break;
         default:
            k++;
            break;
         }

         sonic_gpio_remove(&pgpio->chip, j, gpio_name_buffer);
      }
      if (gpiochip_remove(&pgpio->chip) < 0) {
          sonic_err("Failed to remove GPIO chip\n");
      }
   }
}

static s32 gpio_init(void)
{
   int i;
   int j;
   int k = 0;
   struct sonic_gpio *pgpio;
   int ret = 0;
   u32 addr;
   u32 mask;
   char gpio_name_buffer[50];

   for (i = 0; i < gpio_addrs[0]; i++) {
      addr = gpio_addrs[i + 1];
      pgpio = &gpio[i];
      pgpio->addr = addr;
      pgpio->mask = gpio_masks[i + 1];
      pgpio->ro = gpio_ro[0] ? gpio_ro[i + 1] : 0;
      pgpio->active_low = gpio_active_low[0] ? gpio_active_low[i + 1] : 0;
      snprintf(pgpio->name, sizeof(pgpio->name), "gpio%d", i + 1);
      pgpio->gpio_type = gpio_type[0] ? gpio_type[i + 1] : 0;
      pgpio->chip.label = pgpio->name;
      pgpio->chip.owner = THIS_MODULE;
      pgpio->chip.base = -1;
      pgpio->chip.ngpio = hweight_long(pgpio->mask);
      pgpio->chip.dev = &(pdev_ref->dev);
      pgpio->chip.get = gpio_get;
      pgpio->chip.set = gpio_set;
      pgpio->chip.direction_input = direction_input;
      pgpio->chip.direction_output = direction_output;
      ret = gpiochip_add(&pgpio->chip);
      if (ret) {
         sonic_err("Failed to create GPIO chip\n");
         goto fail;
      }
      for (j = 0; j < pgpio->chip.ngpio; j++) {
         mask = bit_mask(pgpio->mask, j);
         strcpy(gpio_name_buffer, gpio_names[k]);

         switch (pgpio->gpio_type) {
         case QSFPTYPE:
            strcat(gpio_name_buffer, qsfpGpioSuffixes[j]);
            if (j == numQsfpBits - 1) {
               k++;
            }
            break;
         case SFPTYPE:
            strcat(gpio_name_buffer, sfpGpioSuffixes[j]);
            if (j == numSfpBits - 1) {
               k++;
            }
            break;
         case PSUTYPE:
            strcat(gpio_name_buffer, psuGpioSuffixes[j]);
            if (j == numPsuBits - 1) {
               k++;
            }
            break;
         case MUXTYPE:
            strcat(gpio_name_buffer, muxGpioSuffixes[j]);
            if (j == numMuxBits - 1) {
               k++;
            }
            break;
         default:
            k++;
            break;
         }

         ret = sonic_gpio_add(&pgpio->chip, j, gpio_name_buffer, !(pgpio->ro & mask),
                              !!(pgpio->active_low & mask));
         if (ret) {
            goto fail;
         }
      }
   }

   return 0;

  fail:
   sonic_err("Failed to initialize GPIOs\n");
   gpio_remove();
   return ret;
}

static int reset_get(struct gpio_chip *gc, unsigned reset_num)
{
   struct sonic_reset *pReset = container_of(gc, struct sonic_reset, chip);
   u32 mask = bit_mask(pReset->mask, reset_num);
   return (scd_read_register(pdev_ref, pReset->addr) & mask);
}

static void reset_set(struct gpio_chip *gc, unsigned reset_num, int val)
{
   struct sonic_reset *pReset = container_of(gc, struct sonic_reset, chip);
   u32 mask = bit_mask(pReset->mask, reset_num);
   u32 offset = (val ? RESET_SET_OFFSET : RESET_CLEAR_OFFSET);
   scd_write_register(pdev_ref, pReset->addr+offset, mask);
}

static int reset_direction_input(struct gpio_chip *gc, unsigned reset_num)
{
   return 0;
}

static int reset_direction_output(struct gpio_chip *gc, unsigned reset_num, int val)
{
   reset_set(gc, reset_num, val);
   return 0;
}

static void reset_remove(void)
{
   int i;
   int j;
   int k = 0;
   struct sonic_reset *pReset;
   u32 addr;
   for (i = 0; i < reset_addrs[0]; i++) {
      addr = reset_addrs[i + 1];
      pReset = &reset[i];
      if (!pReset) {
         continue;
      }
      for (j = 0; j < pReset->chip.ngpio; j++, k++) {
         sonic_gpio_remove(&pReset->chip, j, reset_names[k]);
      }
      if (gpiochip_remove(&pReset->chip) < 0) {
         sonic_err("Failed to remove GPIO chip for reset\n");
      }
   }
}

static s32 reset_init(void)
{
   int i;
   int j;
   int k = 0;
   struct sonic_reset *pReset;
   int ret = 0;
   u32 addr;
   for (i = 0; i < reset_addrs[0]; i++) {
      addr = reset_addrs[i + 1];
      pReset = &reset[i];
      pReset->addr = addr;
      pReset->mask = reset_masks[i + 1];
      snprintf(pReset->name, sizeof(pReset->name), "pReset%d", i + 1);
      pReset->chip.label = pReset->name;
      pReset->chip.owner = THIS_MODULE;
      pReset->chip.base = -1;
      pReset->chip.ngpio = hweight_long(pReset->mask);
      pReset->chip.dev = &(pdev_ref->dev);
      pReset->chip.get = reset_get;
      pReset->chip.set = reset_set;
      pReset->chip.direction_input = reset_direction_input;
      pReset->chip.direction_output = reset_direction_output;
      ret = gpiochip_add(&pReset->chip);
      if (ret) {
         goto fail;
      }
      for (j = 0; j < pReset->chip.ngpio; j++, k++) {
         ret = sonic_gpio_add(&pReset->chip, j, reset_names[k], true, 0);
         if (ret) {
            goto fail;
         }
      }
   }

   return 0;

  fail:
   reset_remove();
   return ret;
}

static int sonic_finish_init(void)
{
   int err = 0;

   sonic_dbg("Initialize SCD SMBus adapters\n");
   err = smbus_init();
   if (err) {
      sonic_err("Error initializing SCD SMBus adapter\n");
      goto fail_smbus;
   }

   sonic_dbg("Initialize SCD LEDs adapters\n");
   err = led_init();
   if (err) {
      sonic_err("Error initializing SCD LEDs\n");
      goto fail_led;
   }

   sonic_dbg("Initialize SCD GPIOs\n");
   err = gpio_init();
   if (err) {
      sonic_err("Error initializing GPIOs\n");
      goto fail_gpio;
   }

   sonic_dbg("Initialize SCD resets\n");
   err = reset_init();
   if (err) {
      sonic_err("Error initializing resets\n");
      goto fail_reset;
   }

   initialized = 1;
   sonic_info("sonic support initialization complete\n");
   return 0;

fail_reset:
   gpio_remove();
fail_gpio:
   led_remove();
fail_led:
   smbus_remove();
fail_smbus:
   return err;
}

static ssize_t read_u32_array(u32 array[], char *buf)
{
   ssize_t len = 0;
   int i;
   sonic_lock();
   for (i = 1; i < array[0] + 1; i++) {
      len += scnprintf(buf + len, PAGE_SIZE - len, "0x%08x\n", array[i]);
   }
   sonic_unlock();
   return len;
}
static ssize_t write_u32_array(u32 array[], int arraylen, const char *buf,
                               struct device *dev)
{
   ssize_t status = 0;
   char * parse;

   sonic_lock();
   if (!initialized) {
      parse = get_options(buf, arraylen, array);
   } else {
      dev_warn(dev, "attempt to change parameter after device initialization\n");
   }
   sonic_unlock();
   return status;
}
static ssize_t read_str_array(char array[][NAME_LENGTH], u32 arraylen, char *buf)
{
   ssize_t len = 0;
   int i;
   sonic_lock();
   for (i = 0; i < arraylen; i++) {
      len += scnprintf(buf + len, PAGE_SIZE - len, "%s\n", array[i]);
   }
   sonic_unlock();
   return len;
}
static ssize_t write_str_array(char array[][NAME_LENGTH], u32 *arraylen,
                               const char *buf, struct device *dev)
{
   ssize_t status = 0;
   char *running = (char *) buf;
   char *token;
   int i = 0;
   sonic_lock();
   if (!initialized) {
      do {
         token = strsep(&running, ",\n");
         if (token && token[0]) {
            strncpy(array[i], token, sizeof(array[i]));
            i++;
         }
      } while (token);
      *arraylen = i;
   } else {
      dev_warn(dev, "attempt to change parameter after device initialization\n");
   }
   sonic_unlock();
   return status;
}

#define SCD_U32_ARRAY_ATTR(_name)                                               \
static ssize_t show_##_name(struct device *dev, struct device_attribute *attr,  \
char *buf)                                                                      \
{                                                                               \
   return read_u32_array(_name, buf);                                           \
}                                                                               \
static ssize_t store_##_name(struct device *dev, struct device_attribute *attr, \
const char *buf, size_t count)                                                  \
{                                                                               \
   write_u32_array(_name, ARRAY_SIZE(_name), buf, dev);                         \
   return count;                                                                \
}                                                                               \
static DEVICE_ATTR(_name, S_IRUGO|S_IWUSR|S_IWGRP, show_##_name, store_##_name);

#define SCD_STR_ARRAY_ATTR(_name)                                               \
static ssize_t show_##_name(struct device *dev, struct device_attribute *attr,  \
char *buf)                                                                      \
{                                                                               \
   return read_str_array(_name, num_##_name, buf);                              \
}                                                                               \
static ssize_t store_##_name(struct device *dev, struct device_attribute *attr, \
const char *buf, size_t count)                                                  \
{                                                                               \
   write_str_array(_name, &num_##_name, buf, dev);                              \
   return count;                                                                \
}                                                                               \
static DEVICE_ATTR(_name, S_IRUGO|S_IWUSR|S_IWGRP, show_##_name, store_##_name);

#define SCD_DEVICE_ATTR(_name)                                                  \
static ssize_t show_##_name(struct device *dev, struct device_attribute *attr,  \
char *buf)                                                                      \
{                                                                               \
   int count = 0;                                                               \
   sonic_lock();                                                                \
   count = sprintf(buf, "%lu\n", _name);                                        \
   sonic_unlock();                                                              \
   return count;                                                                \
}                                                                               \
static ssize_t store_##_name(struct device *dev, struct device_attribute *attr, \
const char *buf, size_t count)                                                  \
{                                                                               \
   unsigned long new_value = simple_strtoul(buf, NULL, 10);                     \
   sonic_lock();                                                                \
   _name = new_value;                                                           \
   sonic_unlock();                                                              \
   return count;                                                                \
}                                                                               \
static DEVICE_ATTR(_name, S_IRUGO|S_IWUSR|S_IWGRP, show_##_name, store_##_name);

SCD_U32_ARRAY_ATTR(master_addrs);

SCD_U32_ARRAY_ATTR(led_addrs);
SCD_STR_ARRAY_ATTR(led_names);

SCD_U32_ARRAY_ATTR(gpio_addrs);
SCD_U32_ARRAY_ATTR(gpio_masks);
SCD_U32_ARRAY_ATTR(gpio_ro);
SCD_U32_ARRAY_ATTR(gpio_type);
SCD_U32_ARRAY_ATTR(gpio_active_low);
SCD_STR_ARRAY_ATTR(gpio_names);

SCD_U32_ARRAY_ATTR(reset_addrs);
SCD_U32_ARRAY_ATTR(reset_masks);
SCD_STR_ARRAY_ATTR(reset_names);

static struct attribute *sonic_attrs[] = {
   &dev_attr_master_addrs.attr,
   &dev_attr_led_addrs.attr,
   &dev_attr_led_names.attr,
   &dev_attr_reset_addrs.attr,
   &dev_attr_reset_masks.attr,
   &dev_attr_gpio_addrs.attr,
   &dev_attr_gpio_masks.attr,
   &dev_attr_gpio_ro.attr,
   &dev_attr_gpio_type.attr,
   &dev_attr_gpio_active_low.attr,
   &dev_attr_gpio_names.attr,
   &dev_attr_reset_names.attr,
   NULL,
};

static struct attribute_group sonic_attr_group = {
         .attrs = sonic_attrs,
         .name = "sonic_support_driver",
};

static int
sonic_probe(struct pci_dev *pdev)
{
   int error = 0;

   master_addrs[0] = 0;
   led_addrs[0] = 0;
   num_led_names = 0;
   gpio_addrs[0] = 0;
   gpio_masks[0] = 0;
   gpio_ro[0] = 0;
   gpio_type[0] = 0;
   gpio_active_low[0] = 0;
   num_gpio_names = 0;
   reset_addrs[0] = 0;
   reset_masks[0] = 0;
   num_reset_names = 0;

   pdev_ref = pdev;

   error = sysfs_create_link(&pdev->dev.kobj, sonic_kobject, sonic_attr_group.name);
   if (error) {
      sonic_err("Failed to create the sonic sysfs entry link in scd driver\n");
      dev_err(&(pdev->dev), "sysfs_create_link() error %d\n", error);
      return -ENODEV;
   }
   initialized = 0;

   return 0;
}

static void
sonic_remove(struct pci_dev *pdev)
{
   smbus_remove();
   led_remove();
   gpio_remove();
   reset_remove();

   sysfs_remove_link(&pdev->dev.kobj, sonic_attr_group.name);

   initialized = 0;
   pdev_ref = NULL;
   sonic_info("Removed sonic Support Driver\n");
}

static int
sonic_init_trigger(struct pci_dev *pdev) {
   sonic_finish_init();
   initialized = 1;
   return 0;
}

static struct scd_ext_ops sonic_ops = {
   .probe  = sonic_probe,
   .remove = sonic_remove,
   .init_trigger = sonic_init_trigger,
};

static int __init sonic_init(void)
{
   int err = 0;

   sonic_info("Module sonic support init\n");

   mutex_init(&sonic_mutex);
   INIT_LIST_HEAD(&client_list);
   sonic_kobject = kobject_get(kernel_kobj);

   err = sysfs_create_group(sonic_kobject, &sonic_attr_group);
   if (err) {
      sonic_err("Could not create sonic sysfs entries\n");
      goto fail_sysfs;
   }

   err = scd_register_ext_ops(&sonic_ops);
   if (err) {
      sonic_warn("scd-sonic: scd_register_sonic_ops failed\n");
      goto fail_ops;
   }

   return err;

fail_ops:
   sysfs_remove_group(sonic_kobject, &sonic_attr_group);
fail_sysfs:
   mutex_destroy(&sonic_mutex);
   return err;
}

static void __exit sonic_exit(void)
{
   scd_unregister_ext_ops();
   sysfs_remove_group(sonic_kobject, &sonic_attr_group);
   kobject_put(sonic_kobject);
   sonic_info("Module sonic support driver removed\n");
}

module_init(sonic_init);
module_exit(sonic_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Arista Networks");
MODULE_DESCRIPTION("Sonic Support Driver");
