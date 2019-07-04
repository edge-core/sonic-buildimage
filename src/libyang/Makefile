.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(LIBYANG)
DERIVED_TARGETS = $(LIBYANG_DEV) $(LIBYANG_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -fr ./libyang-$(LIBYANG_VERSION)
	wget -O libyang_$(LIBYANG_VERSION).orig.tar.gz                         'https://sonicstorage.blob.core.windows.net/packages/libyang_0.16.105.orig.tar.gz?sv=2015-04-05&sr=b&sig=yTWDhl6B9TTXWAQ46zpLiNxUib61W7U0%2F%2FGvhRibKOc%3D&se=2046-09-30T22%3A10%3A27Z&sp=r'
	wget -O libyang_$(LIBYANG_VERSION).dsc                                 'https://sonicstorage.blob.core.windows.net/packages/libyang_0.16.105-1.dsc?sv=2015-04-05&sr=b&sig=eLkO5wzB1C5oKNIaUPro4gwrgEC3EygIO6eCyTzHmeI%3D&se=2046-09-30T22%3A10%3A12Z&sp=r'
	wget -O libyang_$(LIBYANG_VERSION)-$(LIBYANG_SUBVERSION).debian.tar.xz 'https://sonicstorage.blob.core.windows.net/packages/libyang_0.16.105-1.debian.tar.xz?sv=2015-04-05&sr=b&sig=AH18p7pKK0xIBVxZuA8EMv9%2FhXbCFKmbWAn7Za8%2BZW4%3D&se=2046-09-30T22%3A09%3A36Z&sp=r'
	dpkg-source -x libyang_$(LIBYANG_VERSION).dsc

	pushd ./libyang-$(LIBYANG_VERSION)
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
