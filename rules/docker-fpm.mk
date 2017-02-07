# docker image for fpm

DOCKER_FPM = docker-fpm.gz
$(DOCKER_FPM)_PATH = $(DOCKERS_PATH)/docker-fpm
$(DOCKER_FPM)_DEPENDS += $(QUAGGA) $(SWSS) $(SONIC_CONFIG_ENGINE)
$(DOCKER_FPM)_LOAD_DOCKERS += $(DOCKER_BASE)
SONIC_DOCKER_IMAGES += $(DOCKER_FPM)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_FPM)

$(DOCKER_FPM)_CONTAINER_NAME = bgp
$(DOCKER_FPM)_RUN_OPT += --net=host --privileged -t
$(DOCKER_FPM)_RUN_OPT += --volumes-from database
$(DOCKER_FPM)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

$(DOCKER_FPM)_BASE_IMAGE_FILES += vtysh:/usr/bin/vtysh
