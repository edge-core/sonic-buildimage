SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

THRIFT_VERSION = 0.9.3
THRIFT_VERSION_FULL = $(THRIFT_VERSION)-2

MAIN_TARGET = libthrift-$(THRIFT_VERSION)_$(THRIFT_VERSION_FULL)_amd64.deb
DERIVED_TARGETS = libthrift-dev_$(THRIFT_VERSION_FULL)_amd64.deb \
		  python-thrift_$(THRIFT_VERSION_FULL)_amd64.deb \
		  thrift-compiler_$(THRIFT_VERSION_FULL)_amd64.deb

#THRIFT_LINK_PRE = http://http.debian.net/debian/pool/main/t/thrift
THRIFT_LINK_PRE = https://sonicstorage.blob.core.windows.net/packages/debian

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf thrift-$(THRIFT_VERSION)

	wget -NO "thrift_$(THRIFT_VERSION).orig.tar.gz" "$(THRIFT_LINK_PRE)/thrift_$(THRIFT_VERSION).orig.tar.gz?sv=2015-04-05&sr=b&sig=wM3B01UnZQYYr7ZGXmCvRn6MMeS5hn5Oa5G5%2Btub53g%3D&se=2028-11-11T02%3A20%3A36Z&sp=r"
	wget -NO "thrift_$(THRIFT_VERSION_FULL).debian.tar.xz" "$(THRIFT_LINK_PRE)/thrift_$(THRIFT_VERSION_FULL).debian.tar.xz?sv=2015-04-05&sr=b&sig=76bx%2BN8uxYbuI%2BEq8uK%2B8cTKTzVmjtjsQ9weejWNINk%3D&se=2028-11-11T02%3A19%3A30Z&sp=r"
	wget -NO "thrift_$(THRIFT_VERSION_FULL).dsc" "$(THRIFT_LINK_PRE)/thrift_$(THRIFT_VERSION_FULL).dsc?sv=2015-04-05&sr=b&sig=Vpk1eJ97I5aWrtjAYS8w8AKyLXcJKFGIVFOOBGR3a5I%3D&se=2028-11-11T02%3A20%3A20Z&sp=r"

	dpkg-source -x thrift_$(THRIFT_VERSION_FULL).dsc
	pushd thrift-$(THRIFT_VERSION)
	patch -p1 < ../patch/THRIFT-3577-assertion-failed.patch
	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -d -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
