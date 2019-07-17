# docker image for centec syncd with rpc

DOCKER_SYNCD_PLATFORM_CODE = centec
include $(PLATFORM_PATH)/../template/docker-syncd-base-rpc.mk

$(DOCKER_SYNCD_BASE_RPC)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
