# docker image for centec syncd

DOCKER_SYNCD_PLATFORM_CODE = centec
include $(PLATFORM_PATH)/../template/docker-syncd-base.mk

$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_DBG) \
									$(LIBSWSSCOMMON_DBG) \
									$(LIBSAIMETADATA_DBG) \
									$(LIBSAIREDIS_DBG)

$(DOCKER_SYNCD_CENTEC)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
$(DOCKER_SYNCD_CENTEC)_BASE_IMAGE_FILES += monit_syncd:/etc/monit/conf.d
