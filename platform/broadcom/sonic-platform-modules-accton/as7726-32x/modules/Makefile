ifneq ($(KERNELRELEASE),)
obj-m:= accton_as7726_32x_cpld.o accton_as7726_32x_fan.o  \
	    accton_as7726_32x_leds.o accton_as7726_32x_psu.o ym2651y.o
	    
else
ifeq (,$(KERNEL_SRC))
#$(error KERNEL_SRC is not defined)
KVERSION=3.16.0-6-amd64
KERNEL_DIR   = /usr/src/linux-headers-$(KVERSION)/
KERNELDIR:=$(KERNEL_DIR)
else
KERNELDIR:=$(KERNEL_SRC)
endif
PWD:=$(shell pwd)
default:
	$(MAKE) -C $(KERNELDIR)  M=$(PWD) modules
clean:
	rm -rf *.o *.mod.o *.mod.o *.ko .*cmd .tmp_versions Module.markers Module.symvers modules.order
endif
