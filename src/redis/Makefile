SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

REDIS_VERSION = 3.2.13
REDIS_VERSION_FULL = $(REDIS_VERSION)-1~bpo8+1

MAIN_TARGET = redis-server_$(REDIS_VERSION_FULL)_amd64.deb
DERIVED_TARGETS = redis-tools_$(REDIS_VERSION_FULL)_amd64.deb \
		  redis-sentinel_$(REDIS_VERSION_FULL)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	wget -O redis_$(REDIS_VERSION).orig.tar.gz -N "https://sonicstorage.blob.core.windows.net/packages/redis/redis_$(REDIS_VERSION).orig.tar.gz?sv=2015-04-05&sr=b&sig=DE%2F3Gb3%2BabCrtUJqCPyfU1OTJCANGYkBrdEKi%2FJYMQQ%3D&se=2033-05-19T16%3A43%3A53Z&sp=r"
	wget -O redis_$(REDIS_VERSION_FULL).dsc -N "https://sonicstorage.blob.core.windows.net/packages/redis/redis_$(REDIS_VERSION_FULL).dsc?sv=2015-04-05&sr=b&sig=mQ502FHWRiOFb9cjEUcK0r1gXAc3bBv0fmVEWtroy5c%3D&se=2033-05-19T16%3A43%3A29Z&sp=r"
	wget -O redis_$(REDIS_VERSION_FULL).debian.tar.xz -N "https://sonicstorage.blob.core.windows.net/packages/redis/redis_$(REDIS_VERSION_FULL).debian.tar.xz?sv=2015-04-05&sr=b&sig=iboHl5%2BV6zUcS5%2B8CaNnE9A0qLa7H%2BU8P1H0eofWjig%3D&se=2033-05-19T16%3A43%3A00Z&sp=r"
	dpkg-source -x redis_$(REDIS_VERSION_FULL).dsc

	pushd redis-$(REDIS_VERSION)
	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
