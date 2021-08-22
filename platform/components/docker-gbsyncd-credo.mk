DOCKER_GBSYNCD_PLATFORM_CODE = credo

LIBSAI_CREDO = libsaicredo_0.5.2_amd64.deb
$(LIBSAI_CREDO)_URL = "https://sonicstorage.blob.core.windows.net/packages/credosai/libsaicredo_0.5.2_amd64.deb?st=2021-08-20T01%3A39%3A58Z&se=2100-08-21T01%3A39%3A00Z&sp=rl&sv=2018-03-28&sr=b&sig=H3Ew%2Be17i9VN%2BZ6cmAmLuTEDDK%2FsJ65WUHiINTzB9eE%3D"
LIBSAI_CREDO_OWL = libsaicredo-owl_0.5.2_amd64.deb
$(LIBSAI_CREDO_OWL)_URL = "https://sonicstorage.blob.core.windows.net/packages/credosai/libsaicredo-owl_0.5.2_amd64.deb?st=2021-08-20T01%3A39%3A09Z&se=2100-08-21T01%3A39%3A00Z&sp=rl&sv=2018-03-28&sr=b&sig=YB%2BnILFF2Z4tIbu3utcCG857Y6ae7vS5Qmyk3pzscIw%3D"

ifneq ($($(LIBSAI_CREDO)_URL),)
include $(PLATFORM_PATH)/../template/docker-gbsyncd-base.mk
$(DOCKER_GBSYNCD_BASE)_VERSION = 1.0.0
$(DOCKER_GBSYNCD_BASE)_PACKAGE_NAME = gbsyncd
$(DOCKER_GBSYNCD_BASE)_CONTAINER_NAME = gbsyncd-$(DOCKER_GBSYNCD_PLATFORM_CODE)
$(DOCKER_GBSYNCD_BASE)_PATH = $(PLATFORM_PATH)/../components/docker-gbsyncd-$(DOCKER_GBSYNCD_PLATFORM_CODE)
SONIC_ONLINE_DEBS += $(LIBSAI_CREDO) $(LIBSAI_CREDO_OWL)
$(DOCKER_GBSYNCD_BASE)_DEPENDS += $(SYNCD) $(LIBSAI_CREDO) $(LIBSAI_CREDO_OWL)
endif
