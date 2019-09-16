.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(PSAMPLE)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	rm -fr ./libpsample
	git clone https://github.com/Mellanox/libpsample.git
	cp -r debian libpsample

	pushd ./libpsample
	git checkout -b libpsample -f e48fad2

	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/

