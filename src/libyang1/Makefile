.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(LIBYANG1)
DERIVED_TARGETS = $(LIBYANG1_DEV) $(LIBYANG1_DBG) $(LIBYANG1_CPP) $(LIBYANG1_CPP_DEV) $(LIBYANG1_CPP_DBG)


$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
        # Obtaining the libyang
#	rm -fr ./libyang-$(LIBYANG1_VERSION)
#	git clone https://github.com/CESNET/libyang.git libyang-$(LIBYANG1_VERSION)
#	pushd libyang-$(LIBYANG1_VERSION)
#	git checkout tags/v1.0.184 -b libyang
#	git cherry-pick 1054200178d0277010e832f270841a586a62b31b
#	git cherry-pick aab48f14db4d8d21b22c50bdc6b29d0198f21996
#	mkdir build
#	pushd build
#	cmake -DENABLE_STATIC=ON -DENABLE_LYD_PRIV=ON -DCMAKE_INSTALL_PREFIX:PATH=/usr -D CMAKE_BUILD_TYPE:String="Package" ..
#	make build-deb
	rm -fr ./libyang-1.0.184
	wget -NO libyang_1.0.184-2.dsc http://deb.debian.org/debian/pool/main/liby/libyang/libyang_1.0.184-2.dsc
	wget -NO libyang_1.0.184.orig.tar.gz http://deb.debian.org/debian/pool/main/liby/libyang/libyang_1.0.184.orig.tar.gz
	wget -NO libyang_1.0.184-2.debian.tar.xz http://deb.debian.org/debian/pool/main/liby/libyang/libyang_1.0.184-2.debian.tar.xz
	dpkg-source -x libyang_1.0.184-2.dsc
	pushd libyang-1.0.184
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd
	mv $* $(DEST)/
	mv $(DERIVED_TARGETS) $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
