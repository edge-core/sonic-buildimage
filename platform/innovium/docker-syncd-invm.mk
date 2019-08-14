# docker image for innovium syncd

DOCKER_SYNCD_PLATFORM_CODE = invm
include $(PLATFORM_PATH)/../template/docker-syncd-base.mk

$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD) $(PYTHON_SDK_API) $(INVM_LIBSAI)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_DBG) \
                                $(LIBSWSSCOMMON_DBG) \
                                $(LIBSAIMETADATA_DBG) \
                                $(LIBSAIREDIS_DBG)

$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /host/warmboot:/var/warmboot
