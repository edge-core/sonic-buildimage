# docker image for orchagent

DOCKER_ORCHAGENT_CAVM = docker-orchagent-cavm.gz
$(DOCKER_ORCHAGENT_CAVM)_PATH = $(DOCKERS_PATH)/docker-orchagent
$(DOCKER_ORCHAGENT_CAVM)_DEPENDS += $(SWSS) $(REDIS_TOOLS)
$(DOCKER_ORCHAGENT_CAVM)_LOAD_DOCKERS += $(DOCKER_BASE)
SONIC_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_CAVM)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_ORCHAGENT_CAVM)

$(DOCKER_ORCHAGENT_CAVM)_CONTAINER_NAME = swss
$(DOCKER_ORCHAGENT_CAVM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_ORCHAGENT_CAVM)_RUN_OPT += --volumes-from database
$(DOCKER_ORCHAGENT_CAVM)_RUN_OPT += -v /etc/ssw/:/etc/ssw/:ro
$(DOCKER_ORCHAGENT_CAVM)_RUN_OPT += -v /etc/network/interfaces:/etc/network/interfaces:ro
$(DOCKER_ORCHAGENT_CAVM)_RUN_OPT += -v /etc/network/interfaces.d/:/etc/network/interfaces.d/:ro
$(DOCKER_ORCHAGENT_CAVM)_RUN_OPT += -v /host/machine.conf:/host/machine.conf
$(DOCKER_ORCHAGENT_CAVM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
