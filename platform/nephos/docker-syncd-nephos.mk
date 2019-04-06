# docker image for nephos syncd

DOCKER_SYNCD_NEPHOS = docker-syncd-nephos.gz
$(DOCKER_SYNCD_NEPHOS)_PATH = $(PLATFORM_PATH)/docker-syncd-nephos
$(DOCKER_SYNCD_NEPHOS)_DEPENDS += $(SYNCD)
$(DOCKER_SYNCD_NEPHOS)_FILES += $(DSSERVE) $(NPX_DIAG)
$(DOCKER_SYNCD_NEPHOS)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_NEPHOS)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_NEPHOS)
endif

$(DOCKER_SYNCD_NEPHOS)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_NEPHOS)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_NEPHOS)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_NEPHOS)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
$(DOCKER_SYNCD_NEPHOS)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

$(DOCKER_SYNCD_NEPHOS)_BASE_IMAGE_FILES += npx_diag:/usr/bin/npx_diag
