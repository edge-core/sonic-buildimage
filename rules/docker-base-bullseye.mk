# Docker base image (based on Debian Bullseye)

DOCKER_BASE_BULLSEYE = docker-base-bullseye.gz
$(DOCKER_BASE_BULLSEYE)_PATH = $(DOCKERS_PATH)/docker-base-bullseye

$(DOCKER_BASE_BULLSEYE)_DEPENDS += $(SOCAT)

GDB = gdb
GDBSERVER = gdbserver
VIM = vim
OPENSSH = openssh-client
SSHPASS = sshpass
STRACE = strace
$(DOCKER_BASE_BULLSEYE)_DBG_IMAGE_PACKAGES += $(GDB) $(GDBSERVER) $(VIM) $(OPENSSH) $(SSHPASS) $(STRACE)

SONIC_DOCKER_IMAGES += $(DOCKER_BASE_BULLSEYE)
