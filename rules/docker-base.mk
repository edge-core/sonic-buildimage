# docker base image

DOCKER_BASE = docker-base.gz
$(DOCKER_BASE)_PATH = $(DOCKERS_PATH)/docker-base

ifeq ($(SONIC_CONFIG_DEBUG),y)
GDB = gdb
VIM = vim
OPENSSH = openssh-client
SSHPASS = sshpass
$(DOCKER_BASE)_DBG_PACKAGES += $(GDB) $(VIM) $(OPENSSH) $(SSHPASS)
endif

SONIC_DOCKER_IMAGES += $(DOCKER_BASE)
