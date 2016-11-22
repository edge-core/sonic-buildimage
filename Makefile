## TODO: if install dev package really happens, rebuild the depending project

## Arguments from make command line
USERNAME=
PASSWORD_ENCRYPTED=

## Redis server/tools version
REDIS_VERSION=3.2.4-1~bpo8+1_amd64

## Select bash for commands
SHELL := /bin/bash

## Capture all the files in SDK directories
MLNX-SDK-DEBS=$(notdir $(wildcard src/mlnx-sdk/*.deb))
BRCM-SDK-DEBS=$(notdir $(wildcard src/brcm-sdk/*.deb))
CAVM-SDK-DEBS=$(notdir $(wildcard src/cavm-sdk/*.deb))

LIBNL-DEBS=libnl-3-200_3.2.27-1_amd64.deb libnl-3-dev_3.2.27-1_amd64.deb libnl-genl-3-200_3.2.27-1_amd64.deb libnl-genl-3-dev_3.2.27-1_amd64.deb libnl-route-3-200_3.2.27-1_amd64.deb libnl-route-3-dev_3.2.27-1_amd64.deb  libnl-nf-3-200_3.2.27-1_amd64.deb libnl-nf-3-dev_3.2.27-1_amd64.deb libnl-cli-3-200_3.2.27-1_amd64.deb libnl-cli-3-dev_3.2.27-1_amd64.deb
LIBTEAM-DEBS=libteam5_1.26-1_amd64.deb libteamdctl0_1.26-1_amd64.deb libteam-dev_1.26-1_amd64.deb libteam-utils_1.26-1_amd64.deb

## Function: build_docker, image_name save_file
## build a docker image and save to a file
define build_docker
	docker build --no-cache -t $(1) dockers/$(1)
	mkdir -p `dirname $(2)`
	docker save $(1) | gzip -c > $(2)
endef

## Rules: phony targets
.phony : brcm-all mlnx-all cavm-all p4-all

## Rules: redirect to sub directory
src/%:
	$(MAKE) 											\
	REDIS_VERSION=$(REDIS_VERSION)						\
	LIBNL-DEBS="$(LIBNL-DEBS)"							\
	LIBTEAM-DEBS="$(LIBTEAM-DEBS)"						\
	-C src $(subst src/,,$@)

## Rules: docker-fpm
dockers/docker-fpm/deps/fpmsyncd: src/fpmsyncd
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-fpm/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-team
dockers/docker-team/deps/teamsyncd: src/teamsyncd
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-team/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-orchagent-mlnx
$(addprefix dockers/docker-orchagent-mlnx/deps/,libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb swss_1.0.0_amd64.deb) : dockers/docker-orchagent-mlnx/deps/%.deb : src/mlnx/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-orchagent-mlnx/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-orchagent-cavm
$(addprefix dockers/docker-orchagent-cavm/deps/,libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb swss_1.0.0_amd64.deb) : dockers/docker-orchagent-cavm/deps/%.deb : src/cavm/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-orchagent-cavm/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-orchagent (brcm)
$(addprefix dockers/docker-orchagent/deps/,libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb swss_1.0.0_amd64.deb) : dockers/docker-orchagent/deps/%.deb : src/brcm/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-orchagent/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-syncd-mlnx
$(addprefix dockers/docker-syncd-mlnx/deps/,$(MLNX-SDK-DEBS)) : dockers/docker-syncd-mlnx/deps/%.deb : src/mlnx-sdk/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
$(addprefix dockers/docker-syncd-mlnx/deps/,syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb) : dockers/docker-syncd-mlnx/deps/%.deb : src/mlnx/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-syncd-mlnx/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-syncd-mlnx/deps/fw-SPC.mfa: src/mlnx-sdk/fw-SPC.mfa
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-syncd-cavm
$(addprefix dockers/docker-syncd-cavm/deps/,$(CAVM-SDK-DEBS)) : dockers/docker-syncd-cavm/deps/%.deb : src/cavm-sdk/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
$(addprefix dockers/docker-syncd-cavm/deps/,syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb) : dockers/docker-syncd-cavm/deps/%.deb : src/cavm/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-syncd-cavm/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-syncd (brcm)
$(addprefix dockers/docker-syncd/deps/,$(BRCM-SDK-DEBS)) : dockers/docker-syncd/deps/%.deb : src/brcm-sdk/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
$(addprefix dockers/docker-syncd/deps/,syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb): dockers/docker-syncd/deps/%.deb : src/brcm/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-syncd/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-database
dockers/docker-database/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker-sonic (p4)
$(addprefix dockers/docker-sonic-p4/deps/,swss_1.0.0_amd64.deb syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb) : dockers/docker-sonic-p4/deps/%.deb : src/p4/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
dockers/docker-sonic-p4/deps/%.deb: src/%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

## Rules: docker images
target/docker-base.gz:
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-syncd.gz: target/docker-base.gz $(addprefix dockers/docker-syncd/deps/,$(BRCM-SDK-DEBS) libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb syncd_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb $(LIBNL-DEBS))
	## TODO: remove placeholders for the dependencies
	touch dockers/docker-syncd/deps/{dsserve,bcmcmd}
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-syncd-mlnx.gz: target/docker-base.gz $(addprefix dockers/docker-syncd-mlnx/deps/,$(MLNX-SDK-DEBS) libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb $(LIBNL-DEBS)) dockers/docker-syncd-mlnx/deps/fw-SPC.mfa
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-syncd-cavm.gz: target/docker-base.gz $(addprefix dockers/docker-syncd-cavm/deps/,$(CAVM-SDK-DEBS) libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb $(LIBNL-DEBS))
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-orchagent.gz: target/docker-base.gz $(addprefix dockers/docker-orchagent/deps/,libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb swss_1.0.0_amd64.deb $(LIBNL-DEBS) $(LIBTEAM-DEBS))
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-orchagent-mlnx.gz: target/docker-base.gz $(addprefix dockers/docker-orchagent-mlnx/deps/,libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb swss_1.0.0_amd64.deb $(LIBNL-DEBS) $(LIBTEAM-DEBS))
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-orchagent-cavm.gz: target/docker-base.gz $(addprefix dockers/docker-orchagent-cavm/deps/,libhiredis0.13_0.13.3-2_amd64.deb libswsscommon_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb swss_1.0.0_amd64.deb $(LIBNL-DEBS) $(LIBTEAM-DEBS))
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-fpm.gz: target/docker-base.gz $(addprefix dockers/docker-fpm/deps/,libswsscommon_1.0.0_amd64.deb libhiredis0.13_0.13.3-2_amd64.deb quagga_0.99.24.1-2.1_amd64.deb fpmsyncd $(LIBNL-DEBS))
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-team.gz: target/docker-base.gz $(addprefix dockers/docker-team/deps/,libswsscommon_1.0.0_amd64.deb libhiredis0.13_0.13.3-2_amd64.deb $(LIBNL-DEBS) $(LIBTEAM-DEBS) teamsyncd)
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-database.gz: target/docker-base.gz $(addprefix dockers/docker-database/deps/,redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb)
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

target/docker-sonic-p4.gz: target/docker-base.gz $(addprefix dockers/docker-sonic-p4/deps/,libswsscommon_1.0.0_amd64.deb libhiredis0.13_0.13.3-2_amd64.deb quagga_0.99.24.1-2.1_amd64.deb syncd_1.0.0_amd64.deb swss_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb libthrift-0.9.3_0.9.3-2_amd64.deb redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb p4-bmv2_1.0.0_amd64.deb p4-switch_1.0.0_amd64.deb)
	docker load < $<
	$(call build_docker,$(patsubst target/%.gz,%,$@),$@)

## Rules: linux image content
deps/linux-image-3.16.0-4-amd64_%.deb: src/sonic-linux-kernel/linux-image-3.16.0-4-amd64_%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)
deps/initramfs-tools_%.deb: src/initramfs-tools/initramfs-tools_%.deb
	mkdir -p `dirname $@` && cp $< $(dir $@)

target/sonic-generic.bin: deps/linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb deps/initramfs-tools_0.120_all.deb
	./build_debian.sh "$(USERNAME)" "$(PASSWORD_ENCRYPTED)" && TARGET_MACHINE=generic ./build_image.sh
target/sonic-aboot.bin: deps/linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb deps/initramfs-tools_0.120_all.deb
	./build_debian.sh "$(USERNAME)" "$(PASSWORD_ENCRYPTED)" && TARGET_MACHINE=aboot ./build_image.sh

## Note: docker-fpm.gz must be the last to build the implicit dependency fpmsyncd
brcm-all: target/sonic-generic.bin $(addprefix target/,docker-syncd.gz docker-orchagent.gz docker-fpm.gz docker-team.gz docker-database.gz)

## Note: docker-fpm.gz must be the last to build the implicit dependency fpmsyncd
mlnx-all: target/sonic-generic.bin $(addprefix target/,docker-syncd-mlnx.gz docker-orchagent-mlnx.gz docker-fpm.gz docker-team.gz docker-database.gz)

## Note: docker-fpm.gz must be the last to build the implicit dependency fpmsyncd
cavm-all: target/sonic-generic.bin $(addprefix target/,docker-syncd-cavm.gz docker-orchagent-cavm.gz docker-fpm.gz docker-team.gz docker-database.gz)

p4-all: $(addprefix target/,docker-sonic-p4.gz)
