# ntp package

NTP_VERSION = 4.2.8p12+dfsg
export NTP_VERSION

NTP = ntp_$(NTP_VERSION)-4+deb10u2_amd64.deb
$(NTP)_SRC_PATH = $(SRC_PATH)/ntp
SONIC_MAKE_DEBS += $(NTP)
SONIC_STRETCH_DEBS += $(NTP)

export NTP
