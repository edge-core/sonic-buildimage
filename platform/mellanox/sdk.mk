MLNX_SDK_BASE_URL = https://github.com/Mellanox/SAI-Implementation/raw/sonic/sdk
MLNX_SDK_VERSION = 4.2.3002
MLNX_SDK_RDEBS += $(APPLIBS) $(IPROUTE2) $(SX_ACL_RM) $(SX_COMPLIB) \
		  $(SX_EXAMPLES) $(SX_GEN_UTILS) $(SX_SCEW) $(SX_SDN_HAL) \
		  $(SXD_LIBS) $(TESTX)

MLNX_SDK_DEBS += $(APPLIBS_DEV) $(IPROUTE2_DEV) $(SX_ACL_RM_DEV) \
		 $(SX_COMPLIB_DEV) $(SX_COMPLIB_DEV_STATIC) $(SX_EXAMPLES_DEV) \
		 $(SX_GEN_UTILS_DEV) $(SX_SCEW_DEV) $(SX_SCEW_DEV_STATIC) \
		 $(SX_SDN_HAL_DEV) $(SX_SDN_HAL_DEV_STATIC) $(SXD_LIBS_DEV) \
		 $(SXD_LIBS_DEV_STATIC) $(TESTX_DEV)

APPLIBS = applibs_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
APPLIBS_DEV = applibs-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(APPLIBS),$(APPLIBS_DEV)))
IPROUTE2 = iproute2_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
IPROUTE2_DEV = iproute2-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(IPROUTE2),$(IPROUTE2_DEV)))
SX_COMPLIB = sx-complib_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SX_COMPLIB_DEV = sx-complib-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_COMPLIB),$(SX_COMPLIB_DEV)))
SX_COMPLIB_DEV_STATIC = sx-complib-dev-static_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_COMPLIB),$(SX_COMPLIB_DEV_STATIC)))
SX_EXAMPLES = sx-examples_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SX_EXAMPLES_DEV = sx-examples-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_EXAMPLES),$(SX_EXAMPLES_DEV)))
SX_GEN_UTILS = sx-gen-utils_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SX_GEN_UTILS_DEV = sx-gen-utils-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_GEN_UTILS),$(SX_GEN_UTILS_DEV)))
SX_SCEW = sx-scew_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SX_SCEW_DEV = sx-scew-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_SCEW),$(SX_SCEW_DEV)))
SX_SCEW_DEV_STATIC = sx-scew-dev-static_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_SCEW),$(SX_SCEW_DEV_STATIC)))
SXD_LIBS = sxd-libs_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
SXD_LIBS_DEV = sxd-libs-dev_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SXD_LIBS),$(SXD_LIBS_DEV)))
SXD_LIBS_DEV_STATIC = sxd-libs-dev-static_1.mlnx.$(MLNX_SDK_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SXD_LIBS),$(SXD_LIBS_DEV_STATIC)))

define make_url
	$(1)_URL = $(MLNX_SDK_BASE_URL)/$(1)

endef

$(eval $(foreach deb,$(MLNX_SDK_DEBS),$(call make_url,$(deb))))
$(eval $(foreach deb,$(MLNX_SDK_RDEBS),$(call make_url,$(deb))))

SONIC_ONLINE_DEBS += $(MLNX_SDK_RDEBS)
