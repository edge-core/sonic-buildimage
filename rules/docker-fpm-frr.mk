# docker image for fpm-frr

DOCKER_FPM_FRR = docker-fpm-frr.gz
$(DOCKER_FPM_FRR)_PATH = $(DOCKERS_PATH)/docker-fpm-frr
$(DOCKER_FPM_FRR)_DEPENDS += $(FRR) $(SWSS)
$(DOCKER_FPM_FRR)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_FPM_FRR)

$(DOCKER_FPM_FRR)_CONTAINER_NAME = bgp
$(DOCKER_FPM_FRR)_RUN_OPT += --net=host --privileged -t
$(DOCKER_FPM_FRR)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

$(DOCKER_FPM_FRR)_BASE_IMAGE_FILES += vtysh:/usr/bin/vtysh
