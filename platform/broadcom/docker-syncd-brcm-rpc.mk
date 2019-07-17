# docker image for brcm syncd with rpc

DOCKER_SYNCD_PLATFORM_CODE = brcm
include $(PLATFORM_PATH)/../template/docker-syncd-base-rpc.mk

$(DOCKER_SYNCD_BASE_RPC)_FILES += $(DSSERVE) $(BCMCMD)

$(DOCKER_SYNCD_BASE_RPC)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
