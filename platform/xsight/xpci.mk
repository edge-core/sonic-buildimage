# Xsight xpci

# Fallback when no xpci-dkms_*.deb in SONiC root (/sonic)
XPCI_VERSION_GITHUB ?= 1.0
XPCI_GITHUB_URL = https://github.com/xsightlabs/sonic-xsight-binaries/raw/refs/heads/main/amd64/kernel

XPCI_DKMS_CANDIDATES := $(sort $(wildcard xpci-dkms_*_amd64.deb))
XPCI_DKMS_COUNT := $(words $(XPCI_DKMS_CANDIDATES))

ifeq ($(XPCI_DKMS_COUNT),0)
  XPCI_USE_LOCAL = n
  XPCI_VERSION = $(XPCI_VERSION_GITHUB)
  XPCI = xpci-dkms_$(XPCI_VERSION)_amd64.deb
else ifeq ($(XPCI_DKMS_COUNT),1)
  XPCI_USE_LOCAL = y
  XPCI = $(firstword $(XPCI_DKMS_CANDIDATES))
  XPCI_VERSION = $(patsubst xpci-dkms_%_amd64.deb,%,$(XPCI))
else
  $(error Multiple xpci-dkms packages in SONiC root: $(XPCI_DKMS_CANDIDATES). Leave only one.)
endif

export XPCI_VERSION

KERNEL_XPCI = xpci-modules-$(KVERSION)_$(XPCI_VERSION)_amd64.deb

ifeq ($(XPCI_USE_LOCAL),y)
XSIGHT_XPCI_URL_PREFIX = "file:///sonic"
else
XSIGHT_XPCI_URL_PREFIX = "$(XPCI_GITHUB_URL)"
endif

$(XPCI)_URL = "$(XSIGHT_XPCI_URL_PREFIX)/$(XPCI)"
SONIC_ONLINE_DEBS += $(XPCI)

$(KERNEL_XPCI)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON) $(XPCI)
$(KERNEL_XPCI)_SRC_PATH = $(PLATFORM_PATH)/xpci
SONIC_MAKE_DEBS += $(KERNEL_XPCI)
