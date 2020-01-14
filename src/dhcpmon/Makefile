RM := rm -rf
DHCPMON_TARGET := dhcpmon
CP := cp
MKDIR := mkdir
CC := gcc
MV := mv

# All of the sources participating in the build are defined here
-include src/subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

# Add inputs and outputs from these tool invocations to the build variables 

# All Target
all: sonic-dhcpmon

# Tool invocations
sonic-dhcpmon: $(OBJS) $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: GCC C Linker'
	$(CC) -o "$(DHCPMON_TARGET)" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

# Other Targets
install:
	$(MKDIR) -p $(DESTDIR)/usr/sbin
	$(MV) $(DHCPMON_TARGET) $(DESTDIR)/usr/sbin

deinstall:
	$(RM) $(DESTDIR)/usr/sbin/$(DHCPMON_TARGET)
	$(RM) -rf $(DESTDIR)/usr/sbin

clean:
	-$(RM) $(EXECUTABLES)$(OBJS)$(C_DEPS) $(DHCPMON_TARGET)
	-@echo ' '

.PHONY: all clean dependents
