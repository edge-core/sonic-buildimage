# lm-senensors package

LM_SENSORS_VERSION=3.4.0
LM_SENSORS_VERSION_FULL=$(LM_SENSORS_VERSION)-4

LM_SENSORS = lm-sensors_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(LM_SENSORS)_SRC_PATH = $(SRC_PATH)/lm-sensors

FANCONTROL = fancontrol_$(LM_SENSORS_VERSION_FULL)_all.deb
$(eval $(call add_derived_package,$(LM_SENSORS),$(FANCONTROL)))

LIBSENSORS = libsensors4_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LM_SENSORS),$(LIBSENSORS)))

SENSORD = sensord_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LM_SENSORS),$(SENSORD)))
$(SENSORD)_DEPENDS += $(LIBSENSORS) $(LM_SENSORS)

SONIC_MAKE_DEBS += $(LM_SENSORS)

export LM_SENSORS
export FANCONTROL
export LIBSENSORS
export SENSORD
export LM_SENSORS_VERSION
export LM_SENSORS_VERSION_FULL
