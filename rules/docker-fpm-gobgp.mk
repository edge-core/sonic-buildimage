# docker image for fpm-gobgp

DOCKER_FPM_GOBGP = docker-fpm-gobgp.gz
$(DOCKER_FPM_GOBGP)_PATH = $(DOCKERS_PATH)/docker-fpm-gobgp
$(DOCKER_FPM_GOBGP)_DEPENDS += $(GOBGP)
$(DOCKER_FPM_GOBGP)_LOAD_DOCKERS += $(DOCKER_FPM)
SONIC_DOCKER_IMAGES += $(DOCKER_FPM_GOBGP)

$(DOCKER_FPM_GOBGP)_CONTAINER_NAME = bgp
$(DOCKER_FPM_GOBGP)_RUN_OPT += --net=host --privileged -t
$(DOCKER_FPM_GOBGP)_RUN_OPT += --volumes-from database
$(DOCKER_FPM_GOBGP)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

