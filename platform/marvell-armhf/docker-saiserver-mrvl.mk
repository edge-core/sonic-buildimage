# docker image for mrvl saiserver

DOCKER_SAISERVER_MRVL = docker-saiserver$(SAITHRIFT_VER)-mrvl.gz
$(DOCKER_SAISERVER_MRVL)_PATH = $(PLATFORM_PATH)/docker-saiserver-mrvl
$(DOCKER_SAISERVER_MRVL)_DEPENDS += $(SAISERVER)

$(DOCKER_SAISERVER_MRVL)_DEPENDS += $(MRVL_FPA) $(MRVL_SAI)

# Use syncd_init_common.sh to init hardware platform
SYNCD_INIT_COMMON_SCRIPT = syncd_init_common.sh
$(SYNCD_INIT_COMMON_SCRIPT)_PATH = $(SRC_PATH)/sonic-sairedis/syncd/scripts
SONIC_COPY_FILES += $(SYNCD_INIT_COMMON_SCRIPT)

$(DOCKER_SAISERVER_MRVL)_FILES += $(SYNCD_INIT_COMMON_SCRIPT)
$(DOCKER_SAISERVER_MRVL)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_BULLSEYE)
SONIC_BULLSEYE_DOCKERS += $(DOCKER_SAISERVER_MRVL)
SONIC_DOCKER_IMAGES += $(DOCKER_SAISERVER_MRVL)

$(DOCKER_SAISERVER_MRVL)_CONTAINER_NAME = saiserver$(SAITHRIFT_VER)
$(DOCKER_SAISERVER_MRVL)_RUN_OPT += --privileged -t
$(DOCKER_SAISERVER_MRVL)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SAISERVER_MRVL)_RUN_OPT += -v /var/run/docker-saiserver:/var/run/sswsyncd
$(DOCKER_SAISERVER_MRVL)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SAISERVER_MRVL)_RUN_OPT += -v /host/warmboot:/var/warmboot
