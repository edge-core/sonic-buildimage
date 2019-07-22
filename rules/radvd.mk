# radvd package

RADVD_VERSION = 1.9.1-1.3

export RADVD_VERSION

RADVD = radvd_$(RADVD_VERSION)_amd64.deb
$(RADVD)_SRC_PATH = $(SRC_PATH)/radvd
SONIC_MAKE_DEBS += $(RADVD)


# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += radvd

