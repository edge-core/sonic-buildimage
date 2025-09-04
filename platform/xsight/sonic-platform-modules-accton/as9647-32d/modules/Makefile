ifneq ($(KERNELRELEASE),)
obj-m += x86-64-as9647-32d-cpld.o \
	x86-64-as9647-32d-fan.o x86-64-as9647-32d-leds.o \
	x86-64-as9647-32d-psu.o dps850.o
else
ifeq (,$(KERNEL_SRC))
$(error KERNEL_SRC is not defined)
else
KERNELDIR:=$(KERNEL_SRC)
endif
PWD:=$(shell pwd)
default:
	$(MAKE) -C $(KERNELDIR)  M=$(PWD) modules
clean:
	rm -rf *.o *.mod.o *.mod.o *.ko .*cmd .tmp_versions Module.markers Module.symvers modules.order
endif

