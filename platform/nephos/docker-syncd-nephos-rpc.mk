# docker image for nephos syncd with rpc

DOCKER_SYNCD_PLATFORM_CODE = nephos
include $(PLATFORM_PATH)/../template/docker-syncd-base-rpc.mk

$(DOCKER_SYNCD_BASE_RPC)_FILES += $(DSSERVE) $(NPX_DIAG)

$(DOCKER_SYNCD_BASE_RPC)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
