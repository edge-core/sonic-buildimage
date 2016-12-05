SHELL = /bin/bash
.ONESHELL:

MAIN_TARGET = p4-switch_1.0.0_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	pushd switch

	mkdir -p p4-build/bmv2/switch
	mkdir -p p4-build/bmv2/pd_thrift_gen

	./autogen.sh
	dpkg-buildpackage -us -uc -b -j4

	popd

	mv $* $(DEST)/
