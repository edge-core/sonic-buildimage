.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = socat_$(SOCAT_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./socat-1.7.3.1

	# Get source package
	wget -NO socat_$(SOCAT_VERSION).dsc "https://sonicstorage.blob.core.windows.net/packages/debian/socat_1.7.3.1-2+deb9u1.dsc?sv=2015-04-05&sr=b&sig=Ph7aMqb%2F%2FE%2F8qwxMXoXb5oK1YPkfVt6PV8mBBv5Wi%2F4%3D&se=2155-07-05T11%3A42%3A29Z&sp=r"
	wget -NO socat_$(SOCAT_VERSION).debian.tar.xz "https://sonicstorage.blob.core.windows.net/packages/debian/socat_1.7.3.1-2+deb9u1.debian.tar.xz?sv=2015-04-05&sr=b&sig=yv77Fr5RtZgRTPmJK3j0lZ0BzsCiGaSs2i7NqQKEy2Y%3D&se=2155-07-05T11%3A39%3A59Z&sp=r"
	wget -NO socat_1.7.3.1.orig.tar.gz "https://sonicstorage.blob.core.windows.net/packages/debian/socat_1.7.3.1.orig.tar.gz?sv=2015-04-05&sr=b&sig=0Ai1FM604aGsF5uBu2yN8w9O1a6zNjIDCdaiTo24DyQ%3D&se=2155-07-05T11%3A40%3A14Z&sp=r"

	dpkg-source -x socat_$(SOCAT_VERSION).dsc

	# Build source and Debian packages
	pushd socat-1.7.3.1
	patch -p0 < ../enable_readline.patch
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

