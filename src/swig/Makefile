.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(SWIG_BASE)
DERIVED_TARGETS = $(SWIG) $(SWIG_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -fr ./swig-$(SWIG_VERSION) *.deb
	wget -O swig_$(SWIG_VERSION).orig.tar.gz                      'https://sonicstorage.blob.core.windows.net/packages/swig_3.0.12.orig.tar.gz?sv=2015-04-05&sr=b&sig=kcSKFvlTQZst8Dbb8MUfckGbVEZU5sptFqT2HbwOUtA%3D&se=2046-09-30T22%3A11%3A59Z&sp=r'
	wget -O swig_$(SWIG_VERSION).dsc                              'https://sonicstorage.blob.core.windows.net/packages/swig_3.0.12-2.dsc?sv=2015-04-05&sr=b&sig=k3eLfmWgmCz1Kx8SYcirX18FSQdJ76ifo%2B9rbJBnrf8%3D&se=2046-09-30T22%3A11%3A45Z&sp=r'
	wget -O swig_$(SWIG_VERSION)-$(SWIG_SUBVERSION).debian.tar.xz 'https://sonicstorage.blob.core.windows.net/packages/swig_3.0.12-2.debian.tar.xz?sv=2015-04-05&sr=b&sig=SQICTE%2BR1BO7npUBNwTQjo447OaFz%2BooX6VAm912c7g%3D&se=2046-09-30T22%3A11%3A32Z&sp=r'
	dpkg-source -x swig_$(SWIG_VERSION).dsc

	pushd ./swig-$(SWIG_VERSION)
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
