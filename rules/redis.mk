# redis package

REDIS_VERSION = 3.2.4-1~bpo8+1

REDIS_TOOLS = redis-tools_$(REDIS_VERSION)_amd64.deb
$(REDIS_TOOLS)_SRC_PATH = $(SRC_PATH)/redis
SONIC_MAKE_DEBS += $(REDIS_TOOLS)

REDIS_SERVER = redis-server_$(REDIS_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(REDIS_TOOLS),$(REDIS_SERVER)))

REDIS_SENTINEL = redis-sentinel_$(REDIS_VERSION)_amd64.deb
$(REDIS_SENTINEL)_DEPENDS += $(REDIS_SERVER)
$(REDIS_SENTINEL)_RDEPENDS += $(REDIS_SERVER)
$(eval $(call add_derived_package,$(REDIS_TOOLS),$(REDIS_SENTINEL)))
