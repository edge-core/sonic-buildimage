# lm-senensors package

LM_SENSORS_VERSION=3.4.0
LM_SENSORS_VERSION_FULL=$(LM_SENSORS_VERSION)-4

LM_SENSORS = lm-sensors_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(LM_SENSORS)_SRC_PATH = $(SRC_PATH)/lm-sensors

LM_SENSORS_DBG = lm-sensors-dbgsym_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LM_SENSORS),$(LM_SENSORS_DBG)))

FANCONTROL = fancontrol_$(LM_SENSORS_VERSION_FULL)_all.deb
$(eval $(call add_derived_package,$(LM_SENSORS),$(FANCONTROL)))

LIBSENSORS = libsensors4_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LM_SENSORS),$(LIBSENSORS)))

LIBSENSORS_DBG = libsensors4-dbgsym_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LIBSENSORS),$(LIBSENSORS_DBG)))

SENSORD = sensord_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LM_SENSORS),$(SENSORD)))
$(SENSORD)_DEPENDS += $(LIBSENSORS) $(LM_SENSORS)

SENSORD_DBG = sensord-dbgsym_$(LM_SENSORS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(SENSORD),$(SENSORD_DBG)))

SONIC_MAKE_DEBS += $(LM_SENSORS)

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += lm-sensors

export LM_SENSORS
export FANCONTROL
export LIBSENSORS
export SENSORD
export LM_SENSORS_VERSION
export LM_SENSORS_VERSION_FULL
export LM_SENSORS_DBG
export LIBSENSORS_DBG
export SENSORD_DBG
