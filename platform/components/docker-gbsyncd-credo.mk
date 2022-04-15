DOCKER_GBSYNCD_PLATFORM_CODE = credo

LIBSAI_CREDO = libsaicredo_0.7.5_amd64.deb
$(LIBSAI_CREDO)_URL = "https://sonicstorage.blob.core.windows.net/packages/credosai/libsaicredo_0.7.5_amd64.deb?sv=2020-10-02&st=2022-04-14T02%3A21%3A31Z&se=2100-04-15T02%3A21%3A00Z&sr=b&sp=r&sig=iDv9Fprntpw9iVBFYVjW8iygy4qcSWT8O90nAXdXR0A%3D"
LIBSAI_CREDO_OWL = libsaicredo-owl_0.7.5_amd64.deb
$(LIBSAI_CREDO_OWL)_URL = "https://sonicstorage.blob.core.windows.net/packages/credosai/libsaicredo-owl_0.7.5_amd64.deb?sv=2020-10-02&st=2022-04-14T02%3A23%3A22Z&se=2100-04-15T02%3A23%3A00Z&sr=b&sp=r&sig=58z6E2nPcLIGjqAoxRAo7du%2FzjIBZkFdoXfSzw96Kxc%3D"

ifneq ($($(LIBSAI_CREDO)_URL),)
include $(PLATFORM_PATH)/../template/docker-gbsyncd-base.mk
$(DOCKER_GBSYNCD_BASE)_VERSION = 1.0.0
$(DOCKER_GBSYNCD_BASE)_PACKAGE_NAME = gbsyncd
$(DOCKER_GBSYNCD_BASE)_PATH = $(PLATFORM_PATH)/../components/docker-gbsyncd-$(DOCKER_GBSYNCD_PLATFORM_CODE)
SONIC_ONLINE_DEBS += $(LIBSAI_CREDO) $(LIBSAI_CREDO_OWL)
$(DOCKER_GBSYNCD_BASE)_DEPENDS += $(SYNCD) $(LIBSAI_CREDO) $(LIBSAI_CREDO_OWL)
endif
