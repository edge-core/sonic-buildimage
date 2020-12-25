# SONiC make file

NOJESSIE ?= 1
NOSTRETCH ?= 0

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

clean configure reset showtag sonic-slave-build sonic-slave-bash :
	@echo "+++ Making $@ +++"
ifeq ($(NOJESSIE), 0)
	make -f Makefile.work $@
endif
ifeq ($(NOSTRETCH), 0)
	BLDENV=stretch make -f Makefile.work $@
endif
	BLDENV=buster make -f Makefile.work $@

# Freeze the versions, see more detail options: scripts/versions_manager.py freeze -h
freeze:
	@scripts/versions_manager.py freeze $(FREEZE_VERSION_OPTIONS)
