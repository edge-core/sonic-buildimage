# isc-dhcp packages

ISC_DHCP_VERSION = 4.3.5-2

export ISC_DHCP_VERSION

ISC_DHCP_RELAY = isc-dhcp-relay_$(ISC_DHCP_VERSION)_amd64.deb
$(ISC_DHCP_RELAY)_SRC_PATH = $(SRC_PATH)/isc-dhcp
SONIC_MAKE_DEBS += $(ISC_DHCP_RELAY)

SONIC_STRETCH_DEBS += $(ISC_DHCP_RELAY)

ISC_DHCP_RELAY_DBG = isc-dhcp-relay-dbgsym_$(ISC_DHCP_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(ISC_DHCP_RELAY),$(ISC_DHCP_RELAY_DBG)))
