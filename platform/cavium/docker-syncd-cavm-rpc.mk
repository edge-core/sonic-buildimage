# docker image for cavium syncd with rpc

DOCKER_SYNCD_PLATFORM_CODE = cavm
include $(PLATFORM_PATH)/../template/docker-syncd-base-rpc.mk

$(DOCKER_SYNCD_BASE_RPC)_DEPENDS += $(CAVM_LIBSAI) $(XP_TOOLS) $(REDIS_TOOLS)

