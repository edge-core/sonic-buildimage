# docker image for brcm saiserver

DOCKER_SAISERVER_BRCM = docker-saiserver-brcm.gz
$(DOCKER_SAISERVER_BRCM)_PATH = $(PLATFORM_PATH)/docker-saiserver-brcm
$(DOCKER_SAISERVER_BRCM)_DEPENDS += $(SAISERVER)
$(DOCKER_SAISERVER_BRCM)_FILES += $(DSSERVE) $(BCMCMD)
$(DOCKER_SAISERVER_BRCM)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_STRETCH)
SONIC_DOCKER_IMAGES += $(DOCKER_SAISERVER_BRCM)
SONIC_STRETCH_DOCKERS += $(DOCKER_SAISERVER_BRCM)

$(DOCKER_SAISERVER_BRCM)_CONTAINER_NAME = saiserver
$(DOCKER_SAISERVER_BRCM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SAISERVER_BRCM)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SAISERVER_BRCM)_RUN_OPT += -v /var/run/docker-saiserver:/var/run/sswsyncd
$(DOCKER_SAISERVER_BRCM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SAISERVER_BRCM)_RUN_OPT += -v /host/warmboot:/var/warmboot

$(DOCKER_SAISERVER_BRCM)_BASE_IMAGE_FILES += bcmcmd:/usr/bin/bcmcmd
$(DOCKER_SAISERVER_BRCM)_BASE_IMAGE_FILES += bcmsh:/usr/bin/bcmsh
