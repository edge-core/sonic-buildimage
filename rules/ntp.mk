# ntp package

NTP_VERSION = 4.2.8p15+dfsg
export NTP_VERSION

NTP = ntp_$(NTP_VERSION)-1+deb10u2_$(CONFIGURED_ARCH).deb
$(NTP)_SRC_PATH = $(SRC_PATH)/ntp
SONIC_MAKE_DEBS += $(NTP)
SONIC_STRETCH_DEBS += $(NTP)

export NTP
