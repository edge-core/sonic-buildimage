.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(FRR)
DERIVED_TARGET = $(FRR_PYTHONTOOLS) $(FRR_DBG) $(FRR_SNMP) $(FRR_SNMP_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Build the package
	pushd ./frr
	patch -p1 < ../patch/0001-Add-support-of-bgp-tcp-DSCP-value.patch
	patch -p1 < ../patch/0002-Reduce-severity-of-Vty-connected-from-message.patch
	patch -p1 < ../patch/0003-ignore-nexthop-attribute-when-NLRI-is-present.patch
	patch -p1 < ../patch/0004-Allow-BGP-attr-NEXT_HOP-to-be-0.0.0.0-due-to-allevia.patch
	patch -p1 < ../patch/0005-Support-VRF.patch
	tools/tarsource.sh -V -e '-sonic'
	dpkg-buildpackage -rfakeroot -b -us -uc -Ppkg.frr.nortrlib -j$(SONIC_CONFIG_MAKE_JOBS)
	popd
	mv $(DERIVED_TARGET) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGET)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
