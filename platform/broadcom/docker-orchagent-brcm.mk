# docker image for orchagent

DOCKER_ORCHAGENT_BRCM = docker-orchagent-brcm.gz
$(DOCKER_ORCHAGENT_BRCM)_PATH = $(DOCKERS_PATH)/docker-orchagent
$(DOCKER_ORCHAGENT_BRCM)_DEPENDS += $(SWSS) $(REDIS_TOOLS)
$(DOCKER_ORCHAGENT_BRCM)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_BRCM)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_BRCM)

$(DOCKER_ORCHAGENT_BRCM)_CONTAINER_NAME = swss
$(DOCKER_ORCHAGENT_BRCM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_ORCHAGENT_BRCM)_RUN_OPT += --volumes-from database
$(DOCKER_ORCHAGENT_BRCM)_RUN_OPT += -v /etc/network/interfaces:/etc/network/interfaces:ro
$(DOCKER_ORCHAGENT_BRCM)_RUN_OPT += -v /etc/network/interfaces.d/:/etc/network/interfaces.d/:ro
$(DOCKER_ORCHAGENT_BRCM)_RUN_OPT += -v /host/machine.conf:/host/machine.conf
$(DOCKER_ORCHAGENT_BRCM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
