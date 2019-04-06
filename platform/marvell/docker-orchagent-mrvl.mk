# docker image for orchagent

DOCKER_ORCHAGENT_MRVL = docker-orchagent-mrvl.gz
$(DOCKER_ORCHAGENT_MRVL)_PATH = $(DOCKERS_PATH)/docker-orchagent
$(DOCKER_ORCHAGENT_MRVL)_DEPENDS += $(SWSS) $(REDIS_TOOLS)
$(DOCKER_ORCHAGENT_MRVL)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_MRVL)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_MRVL)

$(DOCKER_ORCHAGENT_MRVL)_CONTAINER_NAME = swss
$(DOCKER_ORCHAGENT_MRVL)_RUN_OPT += --net=host --privileged -t
$(DOCKER_ORCHAGENT_MRVL)_RUN_OPT += -v /etc/network/interfaces:/etc/network/interfaces:ro
$(DOCKER_ORCHAGENT_MRVL)_RUN_OPT += -v /etc/network/interfaces.d/:/etc/network/interfaces.d/:ro
$(DOCKER_ORCHAGENT_MRVL)_RUN_OPT += -v /host/machine.conf:/host/machine.conf
$(DOCKER_ORCHAGENT_MRVL)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

$(DOCKER_ORCHAGENT_MRVL)_BASE_IMAGE_FILES += swssloglevel:/usr/bin/swssloglevel
$(DOCKER_ORCHAGENT_MRVL)_FILES += $(ARP_UPDATE_SCRIPT)
