# docker image for mlnx syncd

DOCKER_SYNCD_MLNX = docker-syncd-mlnx.gz
$(DOCKER_SYNCD_MLNX)_PATH = $(PLATFORM_PATH)/docker-syncd-mlnx
$(DOCKER_SYNCD_MLNX)_DEPENDS += $(SYNCD) $(MFT) $(PYTHON_SDK_API)
$(DOCKER_SYNCD_MLNX)_FILES += $(MLNX_FW)
$(DOCKER_SYNCD_MLNX)_LOAD_DOCKERS += $(DOCKER_BASE)
SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_MLNX)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_MLNX)

$(DOCKER_SYNCD_MLNX)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_MLNX)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SYNCD_MLNX)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_MLNX)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
