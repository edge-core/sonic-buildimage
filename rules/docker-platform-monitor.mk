# Docker image for SONiC platform monitoring tools

DOCKER_PLATFORM_MONITOR = docker-platform-monitor.gz
$(DOCKER_PLATFORM_MONITOR)_PATH = $(DOCKERS_PATH)/docker-platform-monitor
$(DOCKER_PLATFORM_MONITOR)_DEPENDS += $(SONIC_LEDD)
$(DOCKER_PLATFORM_MONITOR)_LOAD_DOCKERS = $(DOCKER_CONFIG_ENGINE)

SONIC_DOCKER_IMAGES += $(DOCKER_PLATFORM_MONITOR)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_PLATFORM_MONITOR)

$(DOCKER_PLATFORM_MONITOR)_CONTAINER_NAME = pmon
$(DOCKER_PLATFORM_MONITOR)_RUN_OPT += --net=host --privileged -t
$(DOCKER_PLATFORM_MONITOR)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

# Mount Arista python library on Aboot images to be used by plugins
$(DOCKER_PLATFORM_MONITOR)_aboot_RUN_OPT += -v /usr/lib/python2.7/dist-packages/arista:/usr/lib/python2.7/dist-packages/arista:ro

$(DOCKER_PLATFORM_MONITOR)_BASE_IMAGE_FILES += sensors:/usr/bin/sensors
