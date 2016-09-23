## TODO: if install dev package really happens, rebuild the depending project

## Arguments from make command line
USERNAME=
PASSWORD_ENCRYPTED=

## Select bash for commands
SHELL := /bin/bash

## Capture all the files in SDK directories
MLNX-SDK-DEBS=$(notdir $(wildcard src/mlnx-sdk/*.deb))
BRCM-SDK-DEBS=$(notdir $(wildcard src/brcm-sdk/*.deb))

## Function: build_docker, image_name save_file
## build a docker image and save to a file
define build_docker
	docker build --no-cache -t $(1) dockers/$(1)
	mkdir -p `dirname $(2)`
	docker save $(1) | gzip -c > $(2)
endef
	
## Rules
.phony : brcm-all mlnx-all

src/%:
	$(MAKE) -C src $(subst src/,,$@)
	
dockers/docker-fpm/deps/fpmsyncd: src/fpmsyncd
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-fpm/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-orchagent-mlnx/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-orchagent-mlnx/deps/%: src/mlnx/%
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-orchagent/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-orchagent/deps/%: src/brcm/%
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-%-mlnx/deps/syncd_1.0.0_amd64.deb: src/mlnx/syncd_1.0.0_amd64.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-%/deps/syncd_1.0.0_amd64.deb: src/brcm/syncd_1.0.0_amd64.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-%-mlnx/deps/libsairedis_1.0.0_amd64.deb: src/mlnx/syncd_1.0.0_amd64.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-%/deps/libsairedis_1.0.0_amd64.deb: src/brcm/syncd_1.0.0_amd64.deb
	mkdir -p `dirname $@` && cp $< $@
	
$(addprefix dockers/docker-syncd-mlnx/deps/,$(MLNX-SDK-DEBS)) : dockers/docker-syncd-mlnx/deps/%.deb : src/mlnx-sdk/%.deb
	mkdir -p `dirname $@` && cp $< $@
	
$(addprefix dockers/docker-syncd/deps/,$(BRCM-SDK-DEBS)) : dockers/docker-syncd/deps/%.deb : src/brcm-sdk/%.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-syncd-mlnx/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $@
	
dockers/docker-syncd/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $@
	
deps/linux-image-3.16.0-4-amd64_%.deb: src/sonic-linux-kernel/linux-image-3.16.0-4-amd64_%.deb
	mkdir -p `dirname $@` && cp $< $@

deps/initramfs-tools_%.deb: src/initramfs-tools/initramfs-tools_%.deb
	mkdir -p `dirname $@` && cp $< $@

target/docker-base.gz:
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-syncd.gz: target/docker-base.gz $(addprefix dockers/docker-syncd/deps/,$(BRCM-SDK-DEBS) libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb syncd_1.0.0_amd64.deb)
	## TODO: remove placeholders for the dependencies
	touch dockers/docker-syncd/deps/{dsserve,bcmcmd}
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)
	
target/docker-syncd-mlnx.gz: target/docker-base.gz $(addprefix dockers/docker-syncd-mlnx/deps/,$(MLNX-SDK-DEBS) applibs_1.mlnx.4.2.2100_amd64.deb libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb)
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)
	
target/docker-orchagent.gz: target/docker-base.gz $(addprefix dockers/docker-orchagent/deps/,libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb swss_1.0.0_amd64.deb)
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)
	
target/docker-orchagent-mlnx.gz: target/docker-base.gz $(addprefix dockers/docker-orchagent-mlnx/deps/,libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb swss_1.0.0_amd64.deb)
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)
	
target/docker-fpm.gz: target/docker-base.gz $(addprefix dockers/docker-fpm/deps/,libswsscommon_1.0.0_amd64.deb libhiredis0.13_0.13.3-2_amd64.deb quagga_0.99.24.1-2_amd64.deb fpmsyncd)
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)
	
target/docker-database.gz: target/docker-base.gz
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/sonic-generic.bin: deps/linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb deps/initramfs-tools_0.120_all.deb
	./build_debian.sh "$(USERNAME)" "$(PASSWORD_ENCRYPTED)" && TARGET_MACHINE=generic ./build_image.sh

target/sonic-aboot.bin: deps/linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb deps/initramfs-tools_0.120_all.deb
	./build_debian.sh "$(USERNAME)" "$(PASSWORD_ENCRYPTED)" && TARGET_MACHINE=aboot ./build_image.sh

## Note: docker-fpm.gz must be the last to build the implicit dependency fpmsyncd
brcm-all: target/sonic-generic.bin $(addprefix target/,docker-syncd.gz docker-orchagent.gz docker-fpm.gz docker-database.gz)

## Note: docker-fpm.gz must be the last to build the implicit dependency fpmsyncd
mlnx-all: target/sonic-generic.bin $(addprefix target/,docker-syncd-mlnx.gz docker-orchagent-mlnx.gz docker-fpm.gz docker-database.gz)
