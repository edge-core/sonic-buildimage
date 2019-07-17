# docker image for mlnx syncd with rpc

DOCKER_SYNCD_PLATFORM_CODE = mlnx
include $(PLATFORM_PATH)/../template/docker-syncd-base-rpc.mk

$(DOCKER_SYNCD_BASE_RPC)_DEPENDS += $(MLNX_SFPD)

$(DOCKER_SYNCD_BASE_RPC)_RUN_OPT += -v /host/warmboot:/var/warmboot
