# docker image for brcm syncd

DOCKER_SYNCD_PLATFORM_CODE = brcm
include $(PLATFORM_PATH)/../template/docker-syncd-base.mk

$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD)
$(DOCKER_SYNCD_BASE)_FILES += $(DSSERVE) $(BCMCMD)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_DBG) \
                                $(LIBSWSSCOMMON_DBG) \
                                $(LIBSAIMETADATA_DBG) \
                                $(LIBSAIREDIS_DBG)

SONIC_STRETCH_DOCKERS += $(DOCKER_SYNCD_BASE)
SONIC_STRETCH_DBG_DOCKERS += $(DOCKER_SYNCD_BASE_DBG)

$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /host/warmboot:/var/warmboot

$(DOCKER_SYNCD_BASE)_BASE_IMAGE_FILES += bcmcmd:/usr/bin/bcmcmd
$(DOCKER_SYNCD_BASE)_BASE_IMAGE_FILES += bcmsh:/usr/bin/bcmsh
$(DOCKER_SYNCD_BASE)_BASE_IMAGE_FILES += bcm_common:/usr/bin/bcm_common
$(DOCKER_SYNCD_BASE)_BASE_IMAGE_FILES += monit_syncd:/etc/monit/conf.d
