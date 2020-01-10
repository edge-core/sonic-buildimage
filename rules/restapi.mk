# sonic-rest-api package

RESTAPI = sonic-rest-api_1.0.1_amd64.deb
$(RESTAPI)_SRC_PATH = $(SRC_PATH)/sonic-restapi
$(RESTAPI)_DEPENDS += $(LIBHIREDIS_DEV) $(LIBNL3_DEV) $(LIBNL_GENL3_DEV) \
                            $(LIBNL_ROUTE3_DEV) $(LIBSWSSCOMMON_DEV) $(LIBSWSSCOMMON)
$(RESTAPI)_RDEPENDS += $(LIBHIREDIS) $(LIBNL3) $(LIBNL_GENL3) \
                             $(LIBNL_ROUTE3) $(LIBSWSSCOMMON)
SONIC_DPKG_DEBS += $(RESTAPI)
