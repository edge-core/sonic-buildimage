ifeq ($(BLDENV),bullseye)

    LIBLUA_VERSION = 5.1.5-8.1

    LIBLUA = liblua5.1-0_$(LIBLUA_VERSION)_$(CONFIGURED_ARCH).deb
    $(LIBLUA)_SRC_PATH = $(SRC_PATH)/liblua
    SONIC_MAKE_DEBS += $(LIBLUA)

    $(eval $(call add_derived_package,$(LIBLUA)))
endif
