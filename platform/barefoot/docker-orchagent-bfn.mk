# docker image for orchagent

DOCKER_ORCHAGENT_BFN = docker-orchagent-bfn.gz
$(DOCKER_ORCHAGENT_BFN)_PATH = $(DOCKERS_PATH)/docker-orchagent
$(DOCKER_ORCHAGENT_BFN)_DEPENDS += $(SWSS) $(REDIS_TOOLS)
$(DOCKER_ORCHAGENT_BFN)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_BFN)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_BFN)

$(DOCKER_ORCHAGENT_BFN)_CONTAINER_NAME = swss
$(DOCKER_ORCHAGENT_BFN)_RUN_OPT += --net=host --privileged -t
$(DOCKER_ORCHAGENT_BFN)_RUN_OPT += -v /etc/network/interfaces:/etc/network/interfaces:ro
$(DOCKER_ORCHAGENT_BFN)_RUN_OPT += -v /etc/network/interfaces.d/:/etc/network/interfaces.d/:ro
$(DOCKER_ORCHAGENT_BFN)_RUN_OPT += -v /host/machine.conf:/host/machine.conf:ro
$(DOCKER_ORCHAGENT_BFN)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_ORCHAGENT_BFN)_RUN_OPT += -v /var/log/swss:/var/log/swss:rw

$(DOCKER_ORCHAGENT_BFN)_BASE_IMAGE_FILES += swssloglevel:/usr/bin/swssloglevel
$(DOCKER_ORCHAGENT_BFN)_FILES += $(ARP_UPDATE_SCRIPT)
