# SONiC make file

NOJESSIE ?= 1
NOSTRETCH ?= 1
NOBUSTER ?= 0
NOBULLSEYE ?= 0

override Q := @
ifeq ($(QUIET),n)
  override Q := 
endif
override SONIC_OVERRIDE_BUILD_VARS += $(SONIC_BUILD_VARS)
override SONIC_OVERRIDE_BUILD_VARS += Q=$(Q)
export Q SONIC_OVERRIDE_BUILD_VARS

ifeq ($(NOJESSIE),0)
BUILD_JESSIE=1
endif

ifeq ($(NOSTRETCH),0)
BUILD_STRETCH=1
endif

ifeq ($(NOBUSTER),0)
BUILD_BUSTER=1
endif

ifeq ($(NOBULLSEYE),0)
BUILD_BULLSEYE=1
endif

PLATFORM_PATH := platform/$(if $(PLATFORM),$(PLATFORM),$(CONFIGURED_PLATFORM))
PLATFORM_CHECKOUT := platform/checkout
PLATFORM_CHECKOUT_FILE := $(PLATFORM_CHECKOUT)/$(PLATFORM).ini
PLATFORM_CHECKOUT_CMD := $(shell if [ -f $(PLATFORM_CHECKOUT_FILE) ]; then PLATFORM_PATH=$(PLATFORM_PATH) j2 $(PLATFORM_CHECKOUT)/template.j2 $(PLATFORM_CHECKOUT_FILE); fi)

%::
	@echo "+++ --- Making $@ --- +++"
ifeq ($(NOJESSIE), 0)
	EXTRA_DOCKER_TARGETS=$(notdir $@) $(MAKE) -f Makefile.work jessie
endif
ifeq ($(NOSTRETCH), 0)
	EXTRA_DOCKER_TARGETS=$(notdir $@) BLDENV=stretch $(MAKE) -f Makefile.work stretch
endif
ifeq ($(NOBUSTER), 0)
	EXTRA_DOCKER_TARGETS=$(notdir $@) BLDENV=buster $(MAKE) -f Makefile.work buster
endif
ifeq ($(NOBULLSEYE), 0)
	BLDENV=bullseye $(MAKE) -f Makefile.work $@
endif
	BLDENV=bullseye $(MAKE) -f Makefile.work docker-cleanup

jessie:
	@echo "+++ Making $@ +++"
ifeq ($(NOJESSIE), 0)
	$(MAKE) -f Makefile.work jessie
endif

stretch:
	@echo "+++ Making $@ +++"
ifeq ($(NOSTRETCH), 0)
	$(MAKE) -f Makefile.work stretch
endif

buster:
	@echo "+++ Making $@ +++"
ifeq ($(NOBUSTER), 0)
	$(MAKE) -f Makefile.work buster
endif

init:
	@echo "+++ Making $@ +++"
	$(MAKE) -f Makefile.work $@

#
# Function to invoke target $@ in Makefile.work with proper BLDENV
#
define make_work
	@echo "+++ Making $@ +++"
	$(if $(BUILD_JESSIE),$(MAKE) -f Makefile.work $@,)
	$(if $(BUILD_STRETCH),BLDENV=stretch $(MAKE) -f Makefile.work $@,)
	$(if $(BUILD_BUSTER),BLDENV=buster $(MAKE) -f Makefile.work $@,)
	$(if $(BUILD_BULLSEYE),BLDENV=bullseye $(MAKE) -f Makefile.work $@,)
endef

.PHONY: $(PLATFORM_PATH)

$(PLATFORM_PATH):
	@echo "+++ Cheking $@ +++"
	$(PLATFORM_CHECKOUT_CMD)

configure : $(PLATFORM_PATH)
	$(call make_work, $@)

clean reset showtag docker-cleanup sonic-slave-build sonic-slave-bash :
	$(call make_work, $@)

# Freeze the versions, see more detail options: scripts/versions_manager.py freeze -h
freeze:
	@scripts/versions_manager.py freeze $(FREEZE_VERSION_OPTIONS)
