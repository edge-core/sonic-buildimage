# SONiC make file

NOJESSIE ?= 0

%::
	@echo "+++ --- Making $@ --- +++"
ifeq ($(NOJESSIE), 0)
	EXTRA_JESSIE_TARGETS=$(notdir $@) make -f Makefile.work jessie
endif
	BLDENV=stretch make -f Makefile.work $@

jessie:
	@echo "+++ Making $@ +++"
ifeq ($(NOJESSIE), 0)
	make -f Makefile.work jessie
endif

clean reset init configure showtag sonic-slave-build sonic-slave-bash :
	@echo "+++ Making $@ +++"
ifeq ($(NOJESSIE), 0)
	make -f Makefile.work $@
endif
	BLDENV=stretch make -f Makefile.work $@
