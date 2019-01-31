# Docker base image (based on Debian Stretch)

DOCKER_BASE_STRETCH = docker-base-stretch.gz
$(DOCKER_BASE_STRETCH)_PATH = $(DOCKERS_PATH)/docker-base-stretch
$(DOCKER_BASE_STRETCH)_DEPENDS += $(SUPERVISOR)
$(DOCKER_BASE_STRETCH)_DEPENDS += $(SOCAT)

ifeq ($(INSTALL_DEBUG_TOOLS),y)
GDB = gdb
GDBSERVER = gdbserver
VIM = vim
OPENSSH = openssh-client
SSHPASS = sshpass
STRACE = strace
$(DOCKER_BASE_STRETCH)_DBG_PACKAGES += $(GDB) $(GDBSERVER) $(VIM) $(OPENSSH) $(SSHPASS) $(STRACE)
endif

SONIC_DOCKER_IMAGES += $(DOCKER_BASE_STRETCH)
