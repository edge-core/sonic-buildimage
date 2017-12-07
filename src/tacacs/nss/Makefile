.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libnss-tacplus_$(NSS_TACPLUS_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain libnss-tacplus
	rm -rf ./libnss-tacplus
	git clone https://github.com/daveolson53/libnss-tacplus.git
	pushd ./libnss-tacplus
	git checkout -f 19008ab

	# Apply patch
	git apply ../0001-Modify-user-map-profile.patch

	dpkg-buildpackage -rfakeroot -b -us -uc
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
