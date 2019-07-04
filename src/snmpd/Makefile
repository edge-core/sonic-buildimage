SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = libsnmp-base_$(SNMPD_VERSION_FULL)_all.deb
DERIVED_TARGETS = snmptrapd_$(SNMPD_VERSION_FULL)_amd64.deb \
		  snmp_$(SNMPD_VERSION_FULL)_amd64.deb \
		  snmpd_$(SNMPD_VERSION_FULL)_amd64.deb \
		  snmp-dbgsym_$(SNMPD_VERSION_FULL)_amd64.deb \
		  snmpd-dbgsym_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp30_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp30-dbg_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp-dev_$(SNMPD_VERSION_FULL)_amd64.deb \
		  libsnmp-perl_$(SNMPD_VERSION_FULL)_amd64.deb \
		  python-netsnmp_$(SNMPD_VERSION_FULL)_amd64.deb \
		  tkmib_$(SNMPD_VERSION_FULL)_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf net-snmp-$(SNMPD_VERSION)

	# download debian net-snmp
	wget -NO net-snmp_$(SNMPD_VERSION_FULL).dsc "https://sonicstorage.blob.core.windows.net/packages/net-snmp_5.7.3+dfsg-1.5.dsc?sv=2015-04-05&sr=b&sig=vDAYAKlwi7JjF%2FesdJUyf4VIEXPsCfLhqqTqNr75zBs%3D&se=2030-10-12T13%3A59%3A45Z&sp=r"
	wget -NO net-snmp_$(SNMPD_VERSION).orig.tar.xz "https://sonicstorage.blob.core.windows.net/packages/net-snmp_5.7.3+dfsg.orig.tar.xz?sv=2015-04-05&sr=b&sig=UjIh%2FTcHrIEzEV7a%2BV2ZP4ks3xHlAA3wqyxkyV7Ms8I%3D&se=2030-10-12T13%3A58%3A19Z&sp=r"
	wget -NO net-snmp_$(SNMPD_VERSION_FULL).debian.tar.xz "https://sonicstorage.blob.core.windows.net/packages/net-snmp_5.7.3+dfsg-1.5.debian.tar.xz?sv=2015-04-05&sr=b&sig=xJkmxjtKXYcPe4yR%2FuCA0TXUfT40rj4XUMBaiK9CjsA%3D&se=2030-10-12T14%3A00%3A15Z&sp=r" 
	dpkg-source -x net-snmp_$(SNMPD_VERSION_FULL).dsc

	pushd net-snmp-$(SNMPD_VERSION)
	git init
	git add -f *
	git commit -m "unmodified snmpd source"

	# Apply patches
	stg init
	stg import -s ../patch-$(SNMPD_VERSION)/series

	fakeroot debian/rules -j$(SONIC_CONFIG_MAKE_JOBS) binary
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
