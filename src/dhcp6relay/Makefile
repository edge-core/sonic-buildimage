RM := rm -rf
DHCP6RELAY_TARGET := dhcp6relay
CP := cp
MKDIR := mkdir
CC := g++
MV := mv
LIBS := -levent -lhiredis -lswsscommon -pthread -lboost_thread -lboost_system
CFLAGS += -Wall -std=c++14 -fPIE -I$(PWD)/../sonic-swss-common/common
PWD := $(shell pwd)

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS) $(OBJS)
endif
endif

-include src/subdir.mk
 
all: sonic-dhcp6relay

sonic-dhcp6relay: $(OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: G++ Linker'
	$(CC) $(LDFLAGS) -o $(DHCP6RELAY_TARGET) $(OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

install:
	$(MKDIR) -p $(DESTDIR)/usr/sbin
	$(MV) $(DHCP6RELAY_TARGET) $(DESTDIR)/usr/sbin

deinstall:
	$(RM) $(DESTDIR)/usr/sbin/$(DHCP6RELAY_TARGET)
	$(RM) -rf $(DESTDIR)/usr/sbin

clean:
	-$(RM) $(EXECUTABLES) $(C_DEPS) $(OBJS) $(DHCP6RELAY_TARGET)
	-@echo ' '

.PHONY: all clean dependents


