# docker image for mrvl syncd
# docker image for syncd


DOCKER_SYNCD_PLATFORM_CODE = mrvl
include $(PLATFORM_PATH)/../template/docker-syncd-base.mk

$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD) $(MRVL_FPA) $(REDIS_TOOLS)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_DBG) \
									$(LIBSWSSCOMMON_DBG) \
									$(LIBSAIMETADATA_DBG) \
									$(LIBSAIREDIS_DBG)


$(DOCKER_SYNCD_BASE)_BASE_IMAGE_FILES += monit_syncd:/etc/monit/conf.d
