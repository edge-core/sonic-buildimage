# docker image for vs syncd

DOCKER_SYNCD_PLATFORM_CODE = vs
include $(PLATFORM_PATH)/../template/docker-syncd-base.mk

$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD_VS)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_VS_DBG) \
									$(LIBSWSSCOMMON_DBG) \
									$(LIBSAIMETADATA_DBG) \
									$(LIBSAIREDIS_DBG) \
									$(LIBSAIVS_DBG)

SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_VS)

$(DOCKER_SYNCD_VS)_RUN_OPT += -v /host/warmboot:/var/warmboot
