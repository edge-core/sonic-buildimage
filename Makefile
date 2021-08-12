# SONiC make file

NOJESSIE ?= 1
NOSTRETCH ?= 0

ifeq ($(NOJESSIE),0)
BUILD_JESSIE=1
endif

ifeq ($(NOSTRETCH),0)
BUILD_STRETCH=1
endif

PLATFORM_PATH := platform/$(if $(PLATFORM),$(PLATFORM),$(CONFIGURED_PLATFORM))
PLATFORM_CHECKOUT := platform/checkout
PLATFORM_CHECKOUT_FILE := $(PLATFORM_CHECKOUT)/$(PLATFORM).ini
PLATFORM_CHECKOUT_CMD := $(shell if [ -f $(PLATFORM_CHECKOUT_FILE) ]; then PLATFORM_PATH=$(PLATFORM_PATH) j2 $(PLATFORM_CHECKOUT)/template.j2 $(PLATFORM_CHECKOUT_FILE); fi)

%::
	@echo "+++ --- Making $@ --- +++"
ifeq ($(NOJESSIE), 0)
	EXTRA_DOCKER_TARGETS=$(notdir $@) make -f Makefile.work jessie
endif
ifeq ($(NOSTRETCH), 0)
	EXTRA_DOCKER_TARGETS=$(notdir $@) BLDENV=stretch make -f Makefile.work stretch
endif
	BLDENV=buster make -f Makefile.work $@

jessie:
	@echo "+++ Making $@ +++"
ifeq ($(NOJESSIE), 0)
	make -f Makefile.work jessie
endif

stretch:
	@echo "+++ Making $@ +++"
ifeq ($(NOSTRETCH), 0)
	make -f Makefile.work stretch
endif

init:
	@echo "+++ Making $@ +++"
	make -f Makefile.work $@

#
# Function to invoke target $@ in Makefile.work with proper BLDENV
#
define make_work
	@echo "+++ Making $@ +++"
	$(if $(BUILD_JESSIE),make -f Makefile.work $@,)
	$(if $(BUILD_STRETCH),BLDENV=stretch make -f Makefile.work $@,)
	BLDENV=buster make -f Makefile.work $@
endef

.PHONY: $(PLATFORM_PATH)

$(PLATFORM_PATH):
	@echo "+++ Cheking $@ +++"
	$(PLATFORM_CHECKOUT_CMD)

configure : $(PLATFORM_PATH)
	$(call make_work, $@)

clean reset showtag sonic-slave-build sonic-slave-bash :
	$(call make_work, $@)

# Freeze the versions, see more detail options: scripts/versions_manager.py freeze -h
freeze:
	@scripts/versions_manager.py freeze $(FREEZE_VERSION_OPTIONS)
