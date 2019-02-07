SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = ntp_$(NTP_VERSION_FULL)_amd64.deb

DSC_FILE = ntp_$(NTP_VERSION_FULL).dsc
ORIG_FILE = ntp_$(NTP_VERSION).orig.tar.gz
DEBIAN_FILE = ntp_$(NTP_VERSION_FULL).debian.tar.xz

DSC_FILE_URL = "https://sonicstorage.blob.core.windows.net/packages/debian/$(DSC_FILE)?sv=2015-04-05&sr=b&sig=HxuXOJsIfkj3lF2TlCShil7lFFf90Zh8oBNTfaka%2FNc%3D&se=2155-12-30T06%3A25%3A21Z&sp=r"
ORIG_FILE_URL = "https://sonicstorage.blob.core.windows.net/packages/debian/$(ORIG_FILE)?sv=2015-04-05&sr=b&sig=bZcv%2B25Ke%2FBcWWd8WdBuK9sMDkcF45Yd2hAmmHBHfTk%3D&se=2155-12-30T06%3A26%3A27Z&sp=r"
DEBIAN_FILE_URL = "https://sonicstorage.blob.core.windows.net/packages/debian/$(DEBIAN_FILE)?sv=2015-04-05&sr=b&sig=WGy6DcbTXo9FDRq%2F0gaiwV7oAYY86dHSUlvGaMrINBM%3D&se=2155-12-30T06%3A21%3A57Z&sp=r"

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf ntp-$(NTP_VERSION)
	wget -O "$(DSC_FILE)" $(DSC_FILE_URL)
	wget -O "$(ORIG_FILE)" $(ORIG_FILE_URL)
	wget -O "$(DEBIAN_FILE)" $(DEBIAN_FILE_URL)

	dpkg-source -x $(DSC_FILE)

	pushd ntp-$(NTP_VERSION)

	git init
	git add -f *
	git commit -m "original source files"

	stg init
	stg import -s ../patch/series

	dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/
