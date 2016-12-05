# docker image for team agent

DOCKER_TEAM = docker-team.gz
$(DOCKER_TEAM)_PATH = $(DOCKERS_PATH)/docker-team
$(DOCKER_TEAM)_DEPENDS += $(SWSS)
$(DOCKER_TEAM)_LOAD_DOCKERS += $(DOCKER_BASE)
SONIC_DOCKER_IMAGES += $(DOCKER_TEAM)
