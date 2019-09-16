.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(SFLOWTOOL)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	rm -fr ./sflowtool
	git clone https://github.com/sflow/sflowtool
	cp -r debian sflowtool

	pushd ./sflowtool
	git checkout -b sflowtool -f 6c2963b
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/

