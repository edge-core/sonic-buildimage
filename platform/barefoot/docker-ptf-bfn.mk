# docker image for docker-ptf

DOCKER_PTF_BFN = docker-ptf-bfn.gz
$(DOCKER_PTF_BFN)_PATH = $(DOCKERS_PATH)/docker-ptf-saithrift
$(DOCKER_PTF_BFN)_LOAD_DOCKERS += $(DOCKER_PTF)
SONIC_STRETCH_DOCKERS += $(DOCKER_PTF_BFN)
