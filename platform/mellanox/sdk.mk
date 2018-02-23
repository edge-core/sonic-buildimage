MLNX_SDK_BASE_URL = https://github.com/Mellanox/SAI-Implementation/raw/05493363f389a5601322d664bdb004434e1a7a39/sdk
MLNX_SDK_VERSION = 4.2.7004X004
MLNX_SDK_RDEBS += $(APPLIBS) $(IPROUTE2_MLNX) $(SX_ACL_RM) $(SX_COMPLIB) \
		  $(SX_EXAMPLES) $(SX_GEN_UTILS) $(SX_SCEW) $(SX_SDN_HAL) \
		  $(SXD_LIBS) $(TESTX)

MLNX_SDK_DEBS += $(APPLIBS_DEV) $(IPROUTE2_MLNX_DEV) $(SX_ACL_RM_DEV) \
		 $(SX_COMPLIB_DEV) $(SX_COMPLIB_DEV_STATIC) $(SX_EXAMPLES_DEV) \
		 $(SX_GEN_UTILS_DEV) $(SX_SCEW_DEV) $(SX_SCEW_DEV_STATIC) \
		 $(SX_SDN_HAL_DEV) $(SX_SDN_HAL_DEV_STATIC) $(SXD_LIBS_DEV) \
		 $(SXD_LIBS_DEV_STATIC) $(TESTX_DEV)

APPLIBS = applibs_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(APPLIBS)_DEPENDS += $(SX_COMPLIB) $(SX_GEN_UTILS) $(SXD_LIBS) $(LIBNL3) $(LIBNL_GENL3)
APPLIBS_DEV = applibs-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(APPLIBS),$(APPLIBS_DEV)))
IPROUTE2_MLNX = iproute2_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
IPROUTE2_MLNX_DEV = iproute2-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(IPROUTE2_MLNX),$(IPROUTE2_MLNX_DEV)))
SX_COMPLIB = sx-complib_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SX_COMPLIB_DEV = sx-complib-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_COMPLIB),$(SX_COMPLIB_DEV)))
SX_EXAMPLES = sx-examples_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(SX_EXAMPLES)_DEPENDS += $(APPLIBS) $(SX_SCEW) $(SXD_LIBS)
SX_EXAMPLES_DEV = sx-examples-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_EXAMPLES),$(SX_EXAMPLES_DEV)))
SX_GEN_UTILS = sx-gen-utils_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(SX_GEN_UTILS)_DEPENDS += $(SX_COMPLIB)
SX_GEN_UTILS_DEV = sx-gen-utils-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_GEN_UTILS),$(SX_GEN_UTILS_DEV)))
SX_SCEW = sx-scew_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SX_SCEW_DEV = sx-scew-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_SCEW),$(SX_SCEW_DEV)))
SXD_LIBS = sxd-libs_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SXD_LIBS_DEV = sxd-libs-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SXD_LIBS),$(SXD_LIBS_DEV)))
#packages that are required for runtime only
PYTHON_SDK_API = python-sdk-api_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(PYTHON_SDK_API)_DEPENDS += $(APPLIBS) $(SXD_LIBS)
SX_KERNEL = sx-kernel_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SX_KERNEL_DEV = sx-kernel-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_KERNEL),$(SX_KERNEL_DEV)))

define make_url
	$(1)_URL = $(MLNX_SDK_BASE_URL)/$(1)

endef

$(eval $(foreach deb,$(MLNX_SDK_DEBS),$(call make_url,$(deb))))
$(eval $(foreach deb,$(MLNX_SDK_RDEBS),$(call make_url,$(deb))))
$(eval $(foreach deb,$(PYTHON_SDK_API) $(SX_KERNEL) $(SX_KERNEL_DEV),$(call make_url,$(deb))))

SONIC_ONLINE_DEBS += $(MLNX_SDK_RDEBS) $(PYTHON_SDK_API) $(SX_KERNEL)
