# ethtool

ETHTOOL_VERSION_BASE = 5.9
export ETHTOOL_VERSION_BASE

ETHTOOL = ethtool_$(ETHTOOL_VERSION_BASE)-1_amd64.deb
$(ETHTOOL)_SRC_PATH = $(SRC_PATH)/ethtool
SONIC_MAKE_DEBS += $(ETHTOOL)

ETHTOOL_DBG = ethtool-dbgsym_$(ETHTOOL_VERSION_BASE)-1_amd64.deb
$(eval $(call add_extra_package,$(ETHTOOL),$(ETHTOOL_DBG)))

export ETHTOOL ETHTOOL_DBG
