# SONiC make file

NOJESSIE ?= 1
NOSTRETCH ?= 0
NOBUSTER ?= 0
NOBULLSEYE ?= 1

%::
	@echo "+++ --- Making $@ --- +++"
ifeq ($(NOJESSIE), 0)
	EXTRA_DOCKER_TARGETS=$(notdir $@) make -f Makefile.work jessie
endif
ifeq ($(NOSTRETCH), 0)
	EXTRA_DOCKER_TARGETS=$(notdir $@) BLDENV=stretch make -f Makefile.work stretch
endif
ifeq ($(NOBUSTER), 0)
	BLDENV=buster make -f Makefile.work $@
endif
ifeq ($(NOBULLSEYE), 0)
	BLDENV=bullseye make -f Makefile.work $@
endif

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

buster:
	@echo "+++ Making $@ +++"
ifeq ($(NOBUSTER), 0)
	make -f Makefile.work buster
endif

init:
	@echo "+++ Making $@ +++"
	make -f Makefile.work $@

clean configure reset showtag sonic-slave-build sonic-slave-bash :
	@echo "+++ Making $@ +++"
ifeq ($(NOJESSIE), 0)
	make -f Makefile.work $@
endif
ifeq ($(NOSTRETCH), 0)
	BLDENV=stretch make -f Makefile.work $@
endif
ifeq ($(NOBUSTER), 0)
	BLDENV=buster make -f Makefile.work $@
endif
ifeq ($(NOBULLSEYE), 0)
	BLDENV=bullseye make -f Makefile.work $@
endif

# Freeze the versions, see more detail options: scripts/versions_manager.py freeze -h
freeze:
	@scripts/versions_manager.py freeze $(FREEZE_VERSION_OPTIONS)
