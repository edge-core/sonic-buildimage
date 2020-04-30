.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = iccpd_$(ICCPD_VERSION)_$(CONFIGURED_ARCH).deb
DEB_PATH = debian

all: iccpd-build mclagdctl-build

iccpd-build:
	make -C src

mclagdctl-build:
	make -C src/mclagdctl

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	make all
	if [ ! -d $(DEB_PATH)/usr/bin ]; then
		mkdir -p $(DEB_PATH)/usr/bin
	fi
	cp iccpd $(DEB_PATH)/usr/bin/iccpd
	cp src/mclagdctl/mclagdctl $(DEB_PATH)/usr/bin/mclagdctl
	chmod +x $(DEB_PATH)/usr/bin/iccpd
	chmod +x $(DEB_PATH)/usr/bin/mclagdctl
	md5sum $(DEB_PATH)/usr/bin/iccpd > $(DEB_PATH)/DEBIAN/md5sums
	md5sum $(DEB_PATH)/usr/bin/mclagdctl >> $(DEB_PATH)/DEBIAN/md5sums
	sed -i "s/Package: .*/Package: iccpd-$(ICCPD_VERSION)-$(CONFIGURED_ARCH)/g" $(DEB_PATH)/DEBIAN/control
	sed -i "s/Architecture: .*/Architecture: $(CONFIGURED_ARCH)/g" $(DEB_PATH)/DEBIAN/control
	dpkg-deb -b $(DEB_PATH) $(DEST)/$(MAIN_TARGET)

clean: iccpd-clean mclagdctl-clean

iccpd-clean:
	make -C src clean

mclagdctl-clean:
	make -C src/mclagdctl clean
