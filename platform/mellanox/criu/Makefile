.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = criu_$(CRIU_VERSION)-1_amd64.deb

CRIU_DEPS = iptables,protobuf-c-compiler,protobuf-compiler,python-protobuf,libprotobuf-c1,python-future,python-ipaddr,libnet1,pkg-config,asciidoc,xmlto

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf criu
	git clone -b v$(CRIU_VERSION) https://github.com/checkpoint-restore/criu.git
	pushd criu
	RUNDIR=/run/criu make
	sudo checkinstall --default --install=no --fstrans=no --pkgversion=$(CRIU_VERSION) --maintainer='@' --requires=$(CRIU_DEPS) --pakdir=$(DEST)
