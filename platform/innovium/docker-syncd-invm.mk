# docker image for innovium syncd

DOCKER_SYNCD_INVM = docker-syncd-invm.gz
$(DOCKER_SYNCD_INVM)_PATH = $(PLATFORM_PATH)/docker-syncd-invm
$(DOCKER_SYNCD_INVM)_DEPENDS += $(SYNCD) $(INVM_LIBSAI)
$(DOCKER_SYNCD_INVM)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_INVM)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_INVM)
endif

$(DOCKER_SYNCD_INVM)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_INVM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_INVM)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_INVM)_RUN_OPT += -v /var/run/docker-syncd:/var/run/sswsyncd
$(DOCKER_SYNCD_INVM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_INVM)_RUN_OPT += -v /host/warmboot:/var/warmboot
