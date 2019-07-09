# docker image for cavium syncd

DOCKER_SYNCD_PLATFORM_CODE = cavm
include $(PLATFORM_PATH)/../template/docker-syncd-base.mk

$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD) $(CAVM_LIBSAI) $(XP_TOOLS) $(REDIS_TOOLS)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_DBG) \
									$(LIBSWSSCOMMON_DBG) \
									$(LIBSAIMETADATA_DBG) \
									$(LIBSAIREDIS_DBG)

