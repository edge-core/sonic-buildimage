# docker image for brcm syncd

DOCKER_SYNCD_BRCM = docker-syncd-brcm.gz
$(DOCKER_SYNCD_BRCM)_PATH = $(PLATFORM_PATH)/docker-syncd-brcm
$(DOCKER_SYNCD_BRCM)_DEPENDS += $(SYNCD)
$(DOCKER_SYNCD_BRCM)_FILES += $(DSSERVE) $(BCMCMD)
$(DOCKER_SYNCD_BRCM)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_BRCM)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_BRCM)
endif

$(DOCKER_SYNCD_BRCM)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_BRCM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_BRCM)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_BRCM)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
$(DOCKER_SYNCD_BRCM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

$(DOCKER_SYNCD_BRCM)_BASE_IMAGE_FILES += bcmcmd:/usr/bin/bcmcmd
$(DOCKER_SYNCD_BRCM)_BASE_IMAGE_FILES += bcmsh:/usr/bin/bcmsh
