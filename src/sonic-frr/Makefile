.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(FRR)
DERIVED_TARGET = $(FRR_PYTHONTOOLS) $(FRR_DBG) $(FRR_SNMP) $(FRR_SNMP_DBG)
SUFFIX = $(shell date +%Y%m%d\.%H%M%S)
STG_BRANCH = stg_temp.$(SUFFIX)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Build the package
	pushd ./frr
	git checkout -b $(FRR_BRANCH) origin/$(FRR_BRANCH)
	stg branch --create $(STG_BRANCH) $(FRR_TAG)
	stg import -s ../patch/series
	tools/tarsource.sh -V -e '-sonic'
	dpkg-buildpackage -rfakeroot -b -us -uc -Ppkg.frr.nortrlib -j$(SONIC_CONFIG_MAKE_JOBS)
	stg undo || true
	git clean -xfdf
	git checkout $(FRR_BRANCH)
	stg branch --delete $(STG_BRANCH)
	git rev-parse --short HEAD | xargs git checkout
	git branch -D $(FRR_BRANCH)
	popd
	mv $(DERIVED_TARGET) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGET)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
