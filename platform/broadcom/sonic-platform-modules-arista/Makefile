SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = $(ARISTA_PLATFORM_MODULE)
EXTRA_TARGETS = $(ARISTA_PLATFORM_MODULE_DRIVERS) \
		$(ARISTA_PLATFORM_MODULE_PYTHON2) \
		$(ARISTA_PLATFORM_MODULE_PYTHON3)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Build the package
	export PYBUILD_INSTALL_ARGS_python2=--install-scripts=/dev/null
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)

	mv $(addprefix ../, $* $(EXTRA_TARGETS)) $(DEST)/

$(addprefix $(DEST)/, $(EXTRA_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
