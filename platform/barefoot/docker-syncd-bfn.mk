# docker image for syncd

DOCKER_SYNCD_PLATFORM_CODE = bfn
include $(PLATFORM_PATH)/../template/docker-syncd-base.mk

$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_DBG) \
                               $(LIBSWSSCOMMON_DBG) \
                               $(LIBSAIMETADATA_DBG) \
                               $(LIBSAIREDIS_DBG)

$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /host/warmboot:/var/warmboot
