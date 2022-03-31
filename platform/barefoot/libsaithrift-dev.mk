# libsaithrift-dev package
SAI_VER = 0.9.4
LIBSAITHRIFT_DEV = libsaithrift-dev_$(SAI_VER)_$(CONFIGURED_ARCH).deb
$(LIBSAITHRIFT_DEV)_SRC_PATH = $(SRC_PATH)/sonic-sairedis/SAI
$(LIBSAITHRIFT_DEV)_DEPENDS += $(LIBTHRIFT_0_14_1) $(LIBTHRIFT_0_14_1_DEV) \
                               $(PYTHON3_THRIFT_0_14_1) $(THRIFT_0_14_1_COMPILER)  \
                               $(BFN_SAI)

#$(LIBSAIVS) $(LIBSAIVS_DEV) $(LIBSAIMETADATA) $(LIBSAIMETADATA_DEV)

# $(LIBSAITHRIFT_DEV)_BUILD_ENV = platform=v

$(LIBSAITHRIFT_DEV)_RDEPENDS += $(LIBTHRIFT_0_14_1) $(BFN_SAI)
SONIC_DPKG_DEBS += $(LIBSAITHRIFT_DEV)

PYTHON_SAITHRIFT = python-saithrift_$(SAI_VER)_amd64.deb
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(PYTHON_SAITHRIFT)))

SAISERVER = saiserver_$(SAI_VER)_amd64.deb
$(SAISERVER)_RDEPENDS += $(LIBTHRIFT_0_14_1) $(BFN_SAI)
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(SAISERVER)))

SAISERVER_DBG = saiserver-dbg_$(SAI_VER)_amd64.deb
$(SAISERVER_DBG)_RDEPENDS += $(SAISERVER)
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(SAISERVER_DBG)))
