# docker image for mlnx saiserver

DOCKER_SAISERVER_MLNX = docker-saiserver-mlnx.gz
$(DOCKER_SAISERVER_MLNX)_PATH = $(PLATFORM_PATH)/docker-saiserver-mlnx
$(DOCKER_SAISERVER_MLNX)_DEPENDS += $(SAISERVER) $(PYTHON_SDK_API) $(MLNX_SFPD) $(CRIU)
$(DOCKER_SAISERVER_MLNX)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SAISERVER_MLNX)

$(DOCKER_SAISERVER_MLNX)_CONTAINER_NAME = saiserver
$(DOCKER_SAISERVER_MLNX)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SAISERVER_MLNX)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SAISERVER_MLNX)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_MLNX)_RUN_OPT += --tmpfs /run/criu
