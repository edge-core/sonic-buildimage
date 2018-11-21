# docker image for vs syncd

DOCKER_SYNCD_VS = docker-syncd-vs.gz
$(DOCKER_SYNCD_VS)_PATH = $(PLATFORM_PATH)/docker-syncd-vs
$(DOCKER_SYNCD_VS)_DEPENDS += $(SYNCD_VS)
$(DOCKER_SYNCD_VS)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_VS)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_VS)

$(DOCKER_SYNCD_VS)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_VS)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_VS)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_VS)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_VS)_RUN_OPT += -v /host/warmboot:/var/warmboot
