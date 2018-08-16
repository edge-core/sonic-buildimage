# SONiC make file

NOSTRETCH ?= 0

%::
	@echo "+++ --- Making $@ --- +++"
ifeq ($(NOSTRETCH), 0)
	BLDENV=stretch make -f Makefile.work stretch
endif
	make -f Makefile.work $@

stretch:
	@echo "+++ Making $@ +++"
ifeq ($(NOSTRETCH), 0)
	BLDENV=stretch make -f Makefile.work stretch
endif

clean reset init configure showtag sonic-slave-build sonic-slave-bash :
	@echo "+++ Making $@ +++"
	make -f Makefile.work $@
