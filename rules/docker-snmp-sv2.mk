# docker image for snmp agent

DOCKER_SNMP_SV2 = docker-snmp-sv2.gz
$(DOCKER_SNMP_SV2)_PATH = $(DOCKERS_PATH)/docker-snmp-sv2
## TODO: remove LIBPY3_DEV if we can get pip3 directly
$(DOCKER_SNMP_SV2)_DEPENDS += $(SNMP) $(SNMPD) $(PY3) $(LIBPY3_DEV)
$(DOCKER_SNMP_SV2)_PYTHON_WHEELS += $(SONIC_PLATFORM_COMMON_PY3) $(SWSSSDK_PY3) $(ASYNCSNMP_PY3)
$(DOCKER_SNMP_SV2)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE)
SONIC_DOCKER_IMAGES += $(DOCKER_SNMP_SV2)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SNMP_SV2)

$(DOCKER_SNMP_SV2)_CONTAINER_NAME = snmp
$(DOCKER_SNMP_SV2)_RUN_OPT += --net=host --privileged -t
$(DOCKER_SNMP_SV2)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SNMP_SV2)_RUN_OPT += -v /host/machine.conf:/host/machine.conf
# mount Arista platform python libraries to support corresponding platforms SNMP power status query
$(DOCKER_SNMP_SV2)_RUN_OPT += -v /usr/lib/python3/dist-packages/arista:/usr/lib/python3/dist-packages/arista:ro
