obj-m := dx010_cpld.o mc24lc64t.o emc2305.o dx010_wdt.o leds-dx010.o lm75.o
KVERSION = $(shell uname -r)
all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
