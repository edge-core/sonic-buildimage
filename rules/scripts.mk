
ARP_UPDATE_SCRIPT = arp_update
$(ARP_UPDATE_SCRIPT)_PATH = files/scripts

CONFIGDB_LOAD_SCRIPT = configdb-load.sh
$(CONFIGDB_LOAD_SCRIPT)_PATH = files/scripts

SONIC_COPY_FILES += $(CONFIGDB_LOAD_SCRIPT) \
                    $(ARP_UPDATE_SCRIPT)


