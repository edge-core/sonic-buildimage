SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = libsnmp-base_$(SNMPD_VERSION_FULL)_all.deb
DERIVED_TARGETS = snmptrapd_$(SNMPD_VERSION_FULL)_amd64.deb \
		  snmp_$(SNMPD_VERSION_FULL)_amd64.deb \
		  snmpd_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp30_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp30-dbg_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp-dev_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp-perl_$(SNMPD_VERSION_FULL)_amd64.deb \
		  python-netsnmp_$(SNMPD_VERSION_FULL)_amd64.deb \
		  tkmib_$(SNMPD_VERSION_FULL)_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf net-snmp-$(SNMPD_VERSION)

	# download debian net-snmp
	wget http://http.debian.net/debian/pool/main/n/net-snmp/net-snmp_$(SNMPD_VERSION_FULL).dsc
	wget http://http.debian.net/debian/pool/main/n/net-snmp/net-snmp_$(SNMPD_VERSION).orig.tar.xz
	wget http://http.debian.net/debian/pool/main/n/net-snmp/net-snmp_$(SNMPD_VERSION_FULL).debian.tar.xz
	dpkg-source -x net-snmp_$(SNMPD_VERSION_FULL).dsc

	pushd net-snmp-$(SNMPD_VERSION)
	fakeroot debian/rules binary
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
