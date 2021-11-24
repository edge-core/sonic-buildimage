DOCKER_GBSYNCD_PLATFORM_CODE = credo

LIBSAI_CREDO = libsaicredo_0.7.2_amd64.deb
$(LIBSAI_CREDO)_URL = "https://sonicstorage.blob.core.windows.net/packages/credosai/libsaicredo_0.7.2_amd64.deb?sv=2020-08-04&st=2021-11-23T03%3A17%3A40Z&se=2100-11-24T03%3A17%3A00Z&sr=b&sp=r&sig=q1hj3YHdkSnaKkN%2Bv0SYw01keE4ottLffuxSGre9mu0%3D"
LIBSAI_CREDO_OWL = libsaicredo-owl_0.7.2_amd64.deb
$(LIBSAI_CREDO_OWL)_URL = "https://sonicstorage.blob.core.windows.net/packages/credosai/libsaicredo-owl_0.7.2_amd64.deb?sv=2020-08-04&st=2021-11-23T03%3A50%3A31Z&se=2100-11-24T03%3A50%3A00Z&sr=b&sp=r&sig=mhiqfhHsBwa5AZOuNSj0U8uLsr46Tet6OGC41Mx5B6I%3D"

ifneq ($($(LIBSAI_CREDO)_URL),)
include $(PLATFORM_PATH)/../template/docker-gbsyncd-base.mk
$(DOCKER_GBSYNCD_BASE)_VERSION = 1.0.0
$(DOCKER_GBSYNCD_BASE)_PACKAGE_NAME = gbsyncd
$(DOCKER_GBSYNCD_BASE)_PATH = $(PLATFORM_PATH)/../components/docker-gbsyncd-$(DOCKER_GBSYNCD_PLATFORM_CODE)
SONIC_ONLINE_DEBS += $(LIBSAI_CREDO) $(LIBSAI_CREDO_OWL)
$(DOCKER_GBSYNCD_BASE)_DEPENDS += $(SYNCD) $(LIBSAI_CREDO) $(LIBSAI_CREDO_OWL)
endif
