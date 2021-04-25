.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libpam-radius-auth_$(PAM_RADIUS_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Build freeradius-server v1.1.x
	pushd freeradius
	-rm -rf freeradius-server
	git clone https://github.com/FreeRADIUS/freeradius-server.git
	popd
	pushd freeradius/freeradius-server
	git checkout -f 5f715dba4d2dbdb268bf60fcc656352274930941
	# Apply patch
	patch -p1 < ../patches/freeradius_configure.patch
	patch -p1 < ../patches/freeradius_2007-04-06.patch
	patch -p1 < ../patches/freeradius_libeap_deprecated_openssl_1_0.patch
	./configure --disable-static --enable-libtool-lock
	make
	popd

	# Obtain pam_radius
	-rm -rf ./pam_radius
	git clone https://github.com/FreeRADIUS/pam_radius.git
	pushd ./pam_radius
	# This is the latest commit with Radius MPL support
	git checkout -f 149c25df84cf5cd0e9addd9346699a9ca8fdddd2

	cp -r ../debian .
	cp -r ../patches .

	# Apply patch
	git apply patches/0001-chap-support.patch
	git apply patches/0002-peap-mschapv2-support.patch
	git apply patches/0003-nas-ip-address-config.patch

	dpkg-buildpackage -rfakeroot -b -us -uc -nc
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
