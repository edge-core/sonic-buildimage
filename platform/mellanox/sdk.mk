MLNX_SDK_BASE_URL = https://github.com/Mellanox/SAI-Implementation/raw/62388a4712aa68409a638d49f79bed07c1433b2e/sdk
MLNX_SDK_VERSION = 4.3.1646
MLNX_SDK_DEB_VERSION = $(subst _,.,$(MLNX_SDK_VERSION))
MLNX_SDK_ISSU_VERSION = 101

MLNX_SDK_RDEBS += $(APPLIBS) $(IPROUTE2_MLNX) $(SX_ACL_RM) $(SX_COMPLIB) \
		  $(SX_EXAMPLES) $(SX_GEN_UTILS) $(SX_SCEW) $(SX_SDN_HAL) \
		  $(SXD_LIBS) $(TESTX) $(WJH_LIBS)

MLNX_SDK_DEBS += $(APPLIBS_DEV) $(IPROUTE2_MLNX_DEV) $(SX_ACL_RM_DEV) \
		 $(SX_COMPLIB_DEV) $(SX_COMPLIB_DEV_STATIC) $(SX_EXAMPLES_DEV) \
		 $(SX_GEN_UTILS_DEV) $(SX_SCEW_DEV) $(SX_SCEW_DEV_STATIC) \
		 $(SX_SDN_HAL_DEV) $(SX_SDN_HAL_DEV_STATIC) $(SXD_LIBS_DEV) \
		 $(SXD_LIBS_DEV_STATIC) $(TESTX_DEV) $(WJH_LIBS_DEV)

# Place here URL where SDK sources exist
MLNX_SDK_SOURCE_BASE_URL =

ifneq ($(MLNX_SDK_SOURCE_BASE_URL), )
SDK_FROM_SRC = y
else
SDK_FROM_SRC = n
endif

export MLNX_SDK_SOURCE_BASE_URL MLNX_SDK_VERSION MLNX_SDK_ISSU_VERSION MLNX_SDK_DEB_VERSION

APPLIBS = applibs_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(APPLIBS)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/applibs
$(APPLIBS)_DEPENDS += $(SX_COMPLIB) $(SX_GEN_UTILS) $(SXD_LIBS) $(LIBNL3) $(LIBNL_GENL3)
$(APPLIBS)_RDEPENDS += $(SX_COMPLIB) $(SX_GEN_UTILS) $(SXD_LIBS) $(LIBNL3) $(LIBNL_GENL3)
APPLIBS_DEV = applibs-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(APPLIBS),$(APPLIBS_DEV)))
IPROUTE2_MLNX = iproute2_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(IPROUTE2_MLNX)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/iproute2
IPROUTE2_MLNX_DEV = iproute2-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(IPROUTE2_MLNX),$(IPROUTE2_MLNX_DEV)))
SX_COMPLIB = sx-complib_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(SX_COMPLIB)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sx-complib
SX_COMPLIB_DEV = sx-complib-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_COMPLIB),$(SX_COMPLIB_DEV)))
SX_EXAMPLES = sx-examples_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(SX_EXAMPLES)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sx-examples
$(SX_EXAMPLES)_DEPENDS += $(APPLIBS) $(SX_SCEW) $(SXD_LIBS)
$(SX_EXAMPLES)_RDEPENDS += $(APPLIBS) $(SX_SCEW) $(SXD_LIBS)
SX_EXAMPLES_DEV = sx-examples-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_EXAMPLES),$(SX_EXAMPLES_DEV)))
SX_GEN_UTILS = sx-gen-utils_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(SX_GEN_UTILS)_SRC_PATH += $(PLATFORM_PATH)/sdk-src/sx-gen-utils
$(SX_GEN_UTILS)_DEPENDS += $(SX_COMPLIB) $(SXD_LIBS)
$(SX_GEN_UTILS)_RDEPENDS += $(SX_COMPLIB)
SX_GEN_UTILS_DEV = sx-gen-utils-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_GEN_UTILS),$(SX_GEN_UTILS_DEV)))
SX_SCEW = sx-scew_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(SX_SCEW)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sx-scew
SX_SCEW_DEV = sx-scew-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_SCEW),$(SX_SCEW_DEV)))
SXD_LIBS = sxd-libs_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(SXD_LIBS)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sxd-libs
$(SXD_LIBS)_DEPENDS += $(SX_COMPLIB_DEV)
SXD_LIBS_DEV = sxd-libs-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SXD_LIBS),$(SXD_LIBS_DEV)))
#packages that are required for runtime only
PYTHON_SDK_API = python-sdk-api_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(PYTHON_SDK_API)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/python-sdk-api
$(PYTHON_SDK_API)_DEPENDS += $(APPLIBS) $(SXD_LIBS)
$(PYTHON_SDK_API)_RDEPENDS += $(APPLIBS) $(SXD_LIBS)
SX_KERNEL = sx-kernel_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(SX_KERNEL)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sx-kernel
$(SX_KERNEL)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SX_KERNEL_DEV = sx-kernel-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(SX_KERNEL),$(SX_KERNEL_DEV)))

WJH_LIBS = wjh-libs_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(WJH_LIBS)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/wjh-libs
$(WJH_LIBS)_DEPENDS += $(SX_COMPLIB_DEV) $(SXD_LIBS_DEV) $(APPLIBS_DEV)
$(WJH_LIBS)_RDEPENDS += $(SX_COMPLIB) $(PYTHON_SDK_API)
WJH_LIBS_DEV = wjh-libs-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(WJH_LIBS),$(WJH_LIBS_DEV)))

define make_url
	$(1)_URL = $(MLNX_SDK_BASE_URL)/$(1)

endef

$(eval $(foreach deb,$(MLNX_SDK_DEBS),$(call make_url,$(deb))))
$(eval $(foreach deb,$(MLNX_SDK_RDEBS),$(call make_url,$(deb))))
$(eval $(foreach deb,$(PYTHON_SDK_API) $(SX_KERNEL) $(SX_KERNEL_DEV),$(call make_url,$(deb))))

ifeq ($(SDK_FROM_SRC), y)
SONIC_MAKE_DEBS += $(MLNX_SDK_RDEBS) $(PYTHON_SDK_API) $(SX_KERNEL)
else
SONIC_ONLINE_DEBS += $(MLNX_SDK_RDEBS) $(PYTHON_SDK_API) $(SX_KERNEL)
endif

SONIC_STRETCH_DEBS += $(SX_KERNEL)

