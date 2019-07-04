###############################################################################
## Presettings
###############################################################################

# Select bash for commands
.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e
USER = $(shell id -un)
UID = $(shell id -u)
GUID = $(shell id -g)
SONIC_GET_VERSION=$(shell export BUILD_TIMESTAMP=$(BUILD_TIMESTAMP) && export BUILD_NUMBER=$(BUILD_NUMBER) && . functions.sh && sonic_get_version)

.SECONDEXPANSION:

NULL :=
SPACE := $(NULL) $(NULL)

###############################################################################
## General definitions
###############################################################################

SRC_PATH = src
RULES_PATH = rules
TARGET_PATH = target
DOCKERS_PATH = dockers
ifdef BLDENV
DEBS_PATH = $(TARGET_PATH)/debs/$(BLDENV)
FILES_PATH = $(TARGET_PATH)/files/$(BLDENV)
else
DEBS_PATH = $(TARGET_PATH)/debs
FILES_PATH = $(TARGET_PATH)/files
endif
PYTHON_DEBS_PATH = $(TARGET_PATH)/python-debs
PYTHON_WHEELS_PATH = $(TARGET_PATH)/python-wheels
PROJECT_ROOT = $(shell pwd)
STRETCH_DEBS_PATH = $(TARGET_PATH)/debs/stretch
STRETCH_FILES_PATH = $(TARGET_PATH)/files/stretch
DBG_IMAGE_MARK = dbg

CONFIGURED_PLATFORM := $(shell [ -f .platform ] && cat .platform || echo generic)
PLATFORM_PATH = platform/$(CONFIGURED_PLATFORM)
export BUILD_NUMBER
export BUILD_TIMESTAMP
export CONFIGURED_PLATFORM

###############################################################################
## Utility rules
## Define configuration, help etc.
###############################################################################

.platform :
ifneq ($(CONFIGURED_PLATFORM),generic)
	@echo Build system is not configured, please run make configure
	@exit 1
endif

configure :
	@mkdir -p target/debs
	@mkdir -p target/debs/stretch
	@mkdir -p target/files
	@mkdir -p target/files/stretch
	@mkdir -p target/python-debs
	@mkdir -p target/python-wheels
	@echo $(PLATFORM) > .platform

distclean : .platform clean
	@rm -f .platform

list :
	@$(foreach target,$(SONIC_TARGET_LIST),echo $(target);)

###############################################################################
## Include other rules
###############################################################################

ifeq ($(SONIC_ENABLE_PFCWD_ON_START),y)
ENABLE_PFCWD_ON_START = y
endif

ifeq ($(SONIC_ENABLE_SYSTEM_TELEMETRY),y)
ENABLE_SYSTEM_TELEMETRY = y
endif

ifeq ($(SONIC_ENABLE_SYNCD_RPC),y)
ENABLE_SYNCD_RPC = y
endif

ifeq ($(SONIC_INSTALL_DEBUG_TOOLS),y)
INSTALL_DEBUG_TOOLS = y
endif

include $(RULES_PATH)/config
include $(RULES_PATH)/functions
include $(RULES_PATH)/*.mk
ifneq ($(CONFIGURED_PLATFORM), undefined)
include $(PLATFORM_PATH)/rules.mk
endif

ifeq ($(USERNAME),)
override USERNAME := $(DEFAULT_USERNAME)
else
$(warning USERNAME given on command line: could be visible to other users)
endif

ifeq ($(PASSWORD),)
override PASSWORD := $(DEFAULT_PASSWORD)
else
$(warning PASSWORD given on command line: could be visible to other users)
endif

ifeq ($(SONIC_DEBUGGING_ON),y)
DEB_BUILD_OPTIONS_GENERIC := nostrip
endif

ifeq ($(SONIC_PROFILING_ON),y)
DEB_BUILD_OPTIONS_GENERIC := nostrip noopt
endif

ifeq ($(SONIC_BUILD_JOBS),)
override SONIC_BUILD_JOBS := $(SONIC_CONFIG_BUILD_JOBS)
endif

ifeq ($(VS_PREPARE_MEM),)
override VS_PREPARE_MEM := $(DEFAULT_VS_PREPARE_MEM)
endif

ifeq ($(KERNEL_PROCURE_METHOD),)
override KERNEL_PROCURE_METHOD := $(DEFAULT_KERNEL_PROCURE_METHOD)
endif

MAKEFLAGS += -j $(SONIC_BUILD_JOBS)
export SONIC_CONFIG_MAKE_JOBS

###############################################################################
## Routing stack related exports
###############################################################################

export SONIC_ROUTING_STACK
export FRR_USER_UID
export FRR_USER_GID

###############################################################################
## Dumping key config attributes associated to current building exercise
###############################################################################

$(info SONiC Build System)
$(info )
$(info Build Configuration)
$(info "CONFIGURED_PLATFORM"             : "$(if $(PLATFORM),$(PLATFORM),$(CONFIGURED_PLATFORM))")
$(info "SONIC_CONFIG_PRINT_DEPENDENCIES" : "$(SONIC_CONFIG_PRINT_DEPENDENCIES)")
$(info "SONIC_BUILD_JOBS"                : "$(SONIC_BUILD_JOBS)")
$(info "SONIC_CONFIG_MAKE_JOBS"          : "$(SONIC_CONFIG_MAKE_JOBS)")
$(info "SONIC_USE_DOCKER_BUILDKIT"       : "$(SONIC_USE_DOCKER_BUILDKIT)")
$(info "USERNAME"                        : "$(USERNAME)")
$(info "PASSWORD"                        : "$(PASSWORD)")
$(info "ENABLE_DHCP_GRAPH_SERVICE"       : "$(ENABLE_DHCP_GRAPH_SERVICE)")
$(info "SHUTDOWN_BGP_ON_START"           : "$(SHUTDOWN_BGP_ON_START)")
$(info "ENABLE_PFCWD_ON_START"           : "$(ENABLE_PFCWD_ON_START)")
$(info "INSTALL_DEBUG_TOOLS"             : "$(INSTALL_DEBUG_TOOLS)")
$(info "ROUTING_STACK"                   : "$(SONIC_ROUTING_STACK)")
ifeq ($(SONIC_ROUTING_STACK),frr)
$(info "FRR_USER_UID"                    : "$(FRR_USER_UID)")
$(info "FRR_USER_GID"                    : "$(FRR_USER_GID)")
endif
$(info "ENABLE_SYNCD_RPC"                : "$(ENABLE_SYNCD_RPC)")
$(info "ENABLE_ORGANIZATION_EXTENSIONS"  : "$(ENABLE_ORGANIZATION_EXTENSIONS)")
$(info "HTTP_PROXY"                      : "$(HTTP_PROXY)")
$(info "HTTPS_PROXY"                     : "$(HTTPS_PROXY)")
$(info "ENABLE_SYSTEM_TELEMETRY"         : "$(ENABLE_SYSTEM_TELEMETRY)")
$(info "SONIC_DEBUGGING_ON"              : "$(SONIC_DEBUGGING_ON)")
$(info "SONIC_PROFILING_ON"              : "$(SONIC_PROFILING_ON)")
$(info "KERNEL_PROCURE_METHOD"           : "$(KERNEL_PROCURE_METHOD)")
$(info "BUILD_TIMESTAMP"                 : "$(BUILD_TIMESTAMP)")
$(info "BLDENV"                          : "$(BLDENV)")
$(info "VS_PREPARE_MEM"                  : "$(VS_PREPARE_MEM)")
$(info )

ifeq ($(SONIC_USE_DOCKER_BUILDKIT),y)
$(warning "Using SONIC_USE_DOCKER_BUILDKIT will produce larger installable SONiC image because of a docker bug (more details: https://github.com/moby/moby/issues/38903)")
export DOCKER_BUILDKIT=1
endif


###############################################################################
## Generic rules section
## All rules must go after includes for propper targets expansion
###############################################################################

export kernel_procure_method=$(KERNEL_PROCURE_METHOD)
export vs_build_prepare_mem=$(VS_PREPARE_MEM)

###############################################################################
## Local targets
###############################################################################

# Copy debian packages from local directory
# Add new package for copy:
#     SOME_NEW_DEB = some_new_deb.deb
#     $(SOME_NEW_DEB)_PATH = path/to/some_new_deb.deb
#     SONIC_COPY_DEBS += $(SOME_NEW_DEB)
$(addprefix $(DEBS_PATH)/, $(SONIC_COPY_DEBS)) : $(DEBS_PATH)/% : .platform
	$(HEADER)
	$(foreach deb,$* $($*_DERIVED_DEBS), \
	    { cp $($(deb)_PATH)/$(deb) $(DEBS_PATH)/ $(LOG) || exit 1 ; } ; )
	$(FOOTER)


SONIC_TARGET_LIST += $(addprefix $(DEBS_PATH)/, $(SONIC_COPY_DEBS))

# Copy regular files from local directory
# Add new package for copy:
#     SOME_NEW_FILE = some_new_file
#     $(SOME_NEW_FILE)_PATH = path/to/some_new_file
#     SONIC_COPY_FILES += $(SOME_NEW_FILE)
$(addprefix $(FILES_PATH)/, $(SONIC_COPY_FILES)) : $(FILES_PATH)/% : .platform
	$(HEADER)
	cp $($*_PATH)/$* $(FILES_PATH)/ $(LOG) || exit 1
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(FILES_PATH)/, $(SONIC_COPY_FILES))

###############################################################################
## Online targets
###############################################################################

# Download debian packages from online location
# Add new package for download:
#     SOME_NEW_DEB = some_new_deb.deb
#     $(SOME_NEW_DEB)_URL = https://url/to/this/deb.deb
#     SONIC_ONLINE_DEBS += $(SOME_NEW_DEB)
$(addprefix $(DEBS_PATH)/, $(SONIC_ONLINE_DEBS)) : $(DEBS_PATH)/% : .platform
	$(HEADER)
	$(foreach deb,$* $($*_DERIVED_DEBS), \
	    { wget --no-use-server-timestamps -O $(DEBS_PATH)/$(deb) $($(deb)_URL) $(LOG) || exit 1 ; } ; )
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(DEBS_PATH)/, $(SONIC_ONLINE_DEBS))

# Download regular files from online location
# Files are stored in deb packages directory for convenience
# Add new file for download:
#     SOME_NEW_FILE = some_new_file
#     $(SOME_NEW_FILE)_URL = https://url/to/this/file
#     SONIC_ONLINE_FILES += $(SOME_NEW_FILE)
$(addprefix $(FILES_PATH)/, $(SONIC_ONLINE_FILES)) : $(FILES_PATH)/% : .platform
	$(HEADER)
	wget --no-use-server-timestamps -O  $@ $($*_URL) $(LOG)
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(FILES_PATH)/, $(SONIC_ONLINE_FILES))

###############################################################################
## Build targets
###############################################################################

# Build project using build.sh script
# They are essentially a one-time build projects that get sources from some URL
# and compile them
# Add new file for build:
#     SOME_NEW_FILE = some_new_deb.deb
#     $(SOME_NEW_FILE)_SRC_PATH = $(SRC_PATH)/project_name
#     $(SOME_NEW_FILE)_DEPENDS = $(SOME_OTHER_DEB1) $(SOME_OTHER_DEB2) ...
#     SONIC_MAKE_FILES += $(SOME_NEW_FILE)
$(addprefix $(FILES_PATH)/, $(SONIC_MAKE_FILES)) : $(FILES_PATH)/% : .platform $$(addsuffix -install,$$(addprefix $(DEBS_PATH)/,$$($$*_DEPENDS)))
	$(HEADER)
	# Remove target to force rebuild
	rm -f $(addprefix $(FILES_PATH)/, $*)
	# Apply series of patches if exist
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && QUILT_PATCHES=../$(notdir $($*_SRC_PATH)).patch quilt push -a; popd; fi
	# Build project and take package
	make DEST=$(shell pwd)/$(FILES_PATH) -C $($*_SRC_PATH) $(shell pwd)/$(FILES_PATH)/$* $(LOG)
	# Clean up
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && quilt pop -a -f; popd; fi
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(FILES_PATH)/, $(SONIC_MAKE_FILES))

###############################################################################
## Debian package related targets
###############################################################################

# Build project using build.sh script
# They are essentially a one-time build projects that get sources from some URL
# and compile them
# Add new package for build:
#     SOME_NEW_DEB = some_new_deb.deb
#     $(SOME_NEW_DEB)_SRC_PATH = $(SRC_PATH)/project_name
#     $(SOME_NEW_DEB)_DEPENDS = $(SOME_OTHER_DEB1) $(SOME_OTHER_DEB2) ...
#     SONIC_MAKE_DEBS += $(SOME_NEW_DEB)
$(addprefix $(DEBS_PATH)/, $(SONIC_MAKE_DEBS)) : $(DEBS_PATH)/% : .platform $$(addsuffix -install,$$(addprefix $(DEBS_PATH)/,$$($$*_DEPENDS)))
	$(HEADER)
	# Remove target to force rebuild
	rm -f $(addprefix $(DEBS_PATH)/, $* $($*_DERIVED_DEBS) $($*_EXTRA_DEBS))
	# Apply series of patches if exist
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && QUILT_PATCHES=../$(notdir $($*_SRC_PATH)).patch quilt push -a; popd; fi
	# Build project and take package
	DEB_BUILD_OPTIONS="${DEB_BUILD_OPTIONS_GENERIC}" make DEST=$(shell pwd)/$(DEBS_PATH) -C $($*_SRC_PATH) $(shell pwd)/$(DEBS_PATH)/$* $(LOG)
	# Clean up
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && quilt pop -a -f; popd; fi
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(DEBS_PATH)/, $(SONIC_MAKE_DEBS))

# Build project with dpkg-buildpackage
# Add new package for build:
#     SOME_NEW_DEB = some_new_deb.deb
#     $(SOME_NEW_DEB)_SRC_PATH = $(SRC_PATH)/project_name
#     $(SOME_NEW_DEB)_DEPENDS = $(SOME_OTHER_DEB1) $(SOME_OTHER_DEB2) ...
#     SONIC_DPKG_DEBS += $(SOME_NEW_DEB)
$(addprefix $(DEBS_PATH)/, $(SONIC_DPKG_DEBS)) : $(DEBS_PATH)/% : .platform $$(addsuffix -install,$$(addprefix $(DEBS_PATH)/,$$($$*_DEPENDS)))
	$(HEADER)
	# Remove old build logs if they exist
	rm -f $($*_SRC_PATH)/debian/*.debhelper.log
	# Apply series of patches if exist
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && QUILT_PATCHES=../$(notdir $($*_SRC_PATH)).patch quilt push -a; popd; fi
	# Build project
	pushd $($*_SRC_PATH) $(LOG)
	[ ! -f ./autogen.sh ] || ./autogen.sh $(LOG)
	$(if $($*_DPKG_TARGET),
		DEB_BUILD_OPTIONS="${DEB_BUILD_OPTIONS_GENERIC} ${$*_DEB_BUILD_OPTIONS}" dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --as-root -T$($*_DPKG_TARGET) $(LOG),
		DEB_BUILD_OPTIONS="${DEB_BUILD_OPTIONS_GENERIC} ${$*_DEB_BUILD_OPTIONS}" dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) $(LOG)
	)
	popd $(LOG)
	# Clean up
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && quilt pop -a -f; popd; fi
	# Take built package(s)
	mv $(addprefix $($*_SRC_PATH)/../, $* $($*_DERIVED_DEBS) $($*_EXTRA_DEBS)) $(DEBS_PATH) $(LOG)
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(DEBS_PATH)/, $(SONIC_DPKG_DEBS))

# Rules for derived debian packages (dev, dbg, etc.)
# All noise takes place in main deb recipe, so we are just telling that
# we depend on it and move our deb to other targets
# Add new dev package:
#     $(eval $(call add_derived_package,$(ORIGINAL_DEB),derived_deb_file.deb))
$(addprefix $(DEBS_PATH)/, $(SONIC_DERIVED_DEBS)) : $(DEBS_PATH)/% : .platform $$(addsuffix -install,$$(addprefix $(DEBS_PATH)/,$$($$*_DEPENDS)))
	$(HEADER)
	# All noise takes place in main deb recipe, so we are just telling that
	# we depend on it
	# Put newer timestamp
	[ -f $@ ] && touch $@
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(DEBS_PATH)/, $(SONIC_DERIVED_DEBS))

# Rules for extra debian packages
# All noise takes place in main deb recipe, so we are just telling that
# we need to build the main deb and move our deb to other targets
# Add new dev package:
#     $(eval $(call add_extra_package,$(ORIGINAL_DEB),extra_deb_file.deb))
$(addprefix $(DEBS_PATH)/, $(SONIC_EXTRA_DEBS)) : $(DEBS_PATH)/% : .platform $$(addprefix $(DEBS_PATH)/,$$($$*_MAIN_DEB))
	$(HEADER)
	# All noise takes place in main deb recipe, so we are just telling that
	# we depend on it
	# Put newer timestamp
	[ -f $@ ] && touch $@
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(DEBS_PATH)/, $(SONIC_EXTRA_DEBS))

# Targets for installing debian packages prior to build one that depends on them
SONIC_INSTALL_TARGETS = $(addsuffix -install,$(addprefix $(DEBS_PATH)/, \
			$(SONIC_ONLINE_DEBS) \
			$(SONIC_COPY_DEBS) \
			$(SONIC_MAKE_DEBS) \
			$(SONIC_DPKG_DEBS) \
			$(SONIC_PYTHON_STDEB_DEBS) \
			$(SONIC_DERIVED_DEBS) \
			$(SONIC_EXTRA_DEBS)))
$(SONIC_INSTALL_TARGETS) : $(DEBS_PATH)/%-install : .platform $$(addsuffix -install,$$(addprefix $(DEBS_PATH)/,$$($$*_DEPENDS))) $(DEBS_PATH)/$$*
	$(HEADER)
	[ -f $(DEBS_PATH)/$* ] || { echo $(DEBS_PATH)/$* does not exist $(LOG) && false $(LOG) }
	# put a lock here because dpkg does not allow installing packages in parallel
	while true; do
	if mkdir $(DEBS_PATH)/dpkg_lock &> /dev/null; then
	{ sudo dpkg -i $(DEBS_PATH)/$* $(LOG) && rm -d $(DEBS_PATH)/dpkg_lock && break; } || { rm -d $(DEBS_PATH)/dpkg_lock && exit 1 ; }
	fi
	done
	$(FOOTER)

###############################################################################
## Python packages
###############################################################################

# Build project with python setup.py --command-packages=stdeb.command
# Add new package for build:
#     SOME_NEW_DEB = some_new_deb.deb
#     $(SOME_NEW_DEB)_SRC_PATH = $(SRC_PATH)/project_name
#     $(SOME_NEW_DEB)_DEPENDS = $(SOME_OTHER_DEB1) $(SOME_OTHER_DEB2) ...
#     SONIC_PYTHON_STDEB_DEBS += $(SOME_NEW_DEB)
$(addprefix $(PYTHON_DEBS_PATH)/, $(SONIC_PYTHON_STDEB_DEBS)) : $(PYTHON_DEBS_PATH)/% : .platform \
		$$(addsuffix -install,$$(addprefix $(PYTHON_DEBS_PATH)/,$$($$*_DEPENDS))) \
		$$(addsuffix -install,$$(addprefix $(PYTHON_WHEELS_PATH)/,$$($$*_WHEEL_DEPENDS)))
	$(HEADER)
	# Apply series of patches if exist
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && QUILT_PATCHES=../$(notdir $($*_SRC_PATH)).patch quilt push -a; popd; fi
	# Build project
	pushd $($*_SRC_PATH) $(LOG)
	rm -rf deb_dist/* $(LOG)
	python setup.py --command-packages=stdeb.command bdist_deb $(LOG)
	popd $(LOG)
	# Clean up
	if [ -f $($*_SRC_PATH).patch/series ]; then pushd $($*_SRC_PATH) && quilt pop -a -f; popd; fi
	# Take built package(s)
	mv $(addprefix $($*_SRC_PATH)/deb_dist/, $* $($*_DERIVED_DEBS)) $(PYTHON_DEBS_PATH) $(LOG)
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(PYTHON_DEBS_PATH)/, $(SONIC_PYTHON_STDEB_DEBS))

# Build project using python setup.py bdist_wheel
# Projects that generate python wheels
# Add new package for build:
#     SOME_NEW_WHL = some_new_whl.whl
#     $(SOME_NEW_WHL)_SRC_PATH = $(SRC_PATH)/project_name
#     $(SOME_NEW_WHL)_PYTHON_VERSION = 2 (or 3)
#     $(SOME_NEW_WHL)_DEPENDS = $(SOME_OTHER_WHL1) $(SOME_OTHER_WHL2) ...
#     SONIC_PYTHON_WHEELS += $(SOME_NEW_WHL)
$(addprefix $(PYTHON_WHEELS_PATH)/, $(SONIC_PYTHON_WHEELS)) : $(PYTHON_WHEELS_PATH)/% : .platform $$(addsuffix -install,$$(addprefix $(PYTHON_WHEELS_PATH)/,$$($$*_DEPENDS)))
	$(HEADER)
	pushd $($*_SRC_PATH) $(LOG)
	# apply series of patches if exist
	if [ -f ../$(notdir $($*_SRC_PATH)).patch/series ]; then QUILT_PATCHES=../$(notdir $($*_SRC_PATH)).patch quilt push -a; fi
	[ "$($*_TEST)" = "n" ] || python$($*_PYTHON_VERSION) setup.py test $(LOG)
	python$($*_PYTHON_VERSION) setup.py bdist_wheel $(LOG)
	# clean up
	if [ -f ../$(notdir $($*_SRC_PATH)).patch/series ]; then quilt pop -a -f; fi
	popd $(LOG)
	mv $($*_SRC_PATH)/dist/$* $(PYTHON_WHEELS_PATH) $(LOG)
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(PYTHON_WHEELS_PATH)/, $(SONIC_PYTHON_WHEELS))

# Targets for installing python wheels.
# Autogenerated
SONIC_INSTALL_WHEELS = $(addsuffix -install, $(addprefix $(PYTHON_WHEELS_PATH)/, $(SONIC_PYTHON_WHEELS)))
$(SONIC_INSTALL_WHEELS) : $(PYTHON_WHEELS_PATH)/%-install : .platform $$(addsuffix -install,$$(addprefix $(PYTHON_WHEELS_PATH)/,$$($$*_DEPENDS))) $(PYTHON_WHEELS_PATH)/$$*
	$(HEADER)
	[ -f $(PYTHON_WHEELS_PATH)/$* ] || { echo $(PYTHON_WHEELS_PATH)/$* does not exist $(LOG) && exit 1; }
	# put a lock here to avoid race conditions
	while true; do
	if mkdir $(PYTHON_WHEELS_PATH)/pip_lock &> /dev/null; then
	{ sudo -E pip$($*_PYTHON_VERSION) install $(PYTHON_WHEELS_PATH)/$* $(LOG) && rm -d $(PYTHON_WHEELS_PATH)/pip_lock && break; } || { rm -d $(PYTHON_WHEELS_PATH)/pip_lock && exit 1 ; }
	fi
	done
	$(FOOTER)

###############################################################################
## Docker images related targets
###############################################################################

# start docker daemon
docker-start :
	@sudo sed -i '/http_proxy/d' /etc/default/docker
	@sudo bash -c "echo \"export http_proxy=$$http_proxy\" >> /etc/default/docker"
	@test x$(SONIC_CONFIG_USE_NATIVE_DOCKERD_FOR_BUILD) != x"y" && sudo service docker status &> /dev/null || ( sudo service docker start &> /dev/null && ./scripts/wait_for_docker.sh 60 )

# targets for building simple docker images that do not depend on any debian packages
$(addprefix $(TARGET_PATH)/, $(SONIC_SIMPLE_DOCKER_IMAGES)) : $(TARGET_PATH)/%.gz : .platform docker-start $$(addsuffix -load,$$(addprefix $(TARGET_PATH)/,$$($$*.gz_LOAD_DOCKERS)))
	$(HEADER)
	# Apply series of patches if exist
	if [ -f $($*.gz_PATH).patch/series ]; then pushd $($*.gz_PATH) && QUILT_PATCHES=../$(notdir $($*.gz_PATH)).patch quilt push -a; popd; fi
	docker info $(LOG)
	docker build --squash --no-cache \
		--build-arg http_proxy=$(HTTP_PROXY) \
		--build-arg https_proxy=$(HTTPS_PROXY) \
		--build-arg user=$(USER) \
		--build-arg uid=$(UID) \
		--build-arg guid=$(GUID) \
		--build-arg docker_container_name=$($*.gz_CONTAINER_NAME) \
		--label Tag=$(SONIC_GET_VERSION) \
		-t $* $($*.gz_PATH) $(LOG)
	docker save $* | gzip -c > $@
	# Clean up
	if [ -f $($*.gz_PATH).patch/series ]; then pushd $($*.gz_PATH) && quilt pop -a -f; popd; fi
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(TARGET_PATH)/, $(SONIC_SIMPLE_DOCKER_IMAGES))

# Build jessie docker images only in jessie slave docker,
# jessie docker images only in jessie slave docker
ifeq ($(BLDENV),)
	DOCKER_IMAGES_FOR_INSTALLERS := $(sort $(foreach installer,$(SONIC_INSTALLERS),$($(installer)_DOCKERS)))
	DOCKER_IMAGES := $(SONIC_JESSIE_DOCKERS)
	DOCKER_DBG_IMAGES := $(SONIC_JESSIE_DBG_DOCKERS)
	SONIC_JESSIE_DOCKERS_FOR_INSTALLERS = $(filter $(SONIC_JESSIE_DOCKERS),$(DOCKER_IMAGES_FOR_INSTALLERS) $(EXTRA_JESSIE_TARGETS))
	SONIC_JESSIE_DBG_DOCKERS_FOR_INSTALLERS = $(filter $(SONIC_JESSIE_DBG_DOCKERS), $(patsubst %.gz,%-$(DBG_IMAGE_MARK).gz, $(SONIC_JESSIE_DOCKERS_FOR_INSTALLERS)))
else
	DOCKER_IMAGES := $(filter-out $(SONIC_JESSIE_DOCKERS), $(SONIC_DOCKER_IMAGES))
	DOCKER_DBG_IMAGES := $(filter-out $(SONIC_JESSIE_DBG_DOCKERS), $(SONIC_DOCKER_DBG_IMAGES))
endif

# Targets for building docker images
$(addprefix $(TARGET_PATH)/, $(DOCKER_IMAGES)) : $(TARGET_PATH)/%.gz : .platform docker-start \
		$$(addprefix $(DEBS_PATH)/,$$($$*.gz_DEPENDS)) \
		$$(addprefix $(FILES_PATH)/,$$($$*.gz_FILES)) \
		$$(addprefix $(PYTHON_DEBS_PATH)/,$$($$*.gz_PYTHON_DEBS)) \
		$$(addprefix $(PYTHON_WHEELS_PATH)/,$$($$*.gz_PYTHON_WHEELS)) \
		$$(addsuffix -load,$$(addprefix $(TARGET_PATH)/,$$($$*.gz_LOAD_DOCKERS))) \
		$$($$*.gz_PATH)/Dockerfile.j2
	$(HEADER)
	# Apply series of patches if exist
	if [ -f $($*.gz_PATH).patch/series ]; then pushd $($*.gz_PATH) && QUILT_PATCHES=../$(notdir $($*.gz_PATH)).patch quilt push -a; popd; fi
	mkdir -p $($*.gz_PATH)/debs $(LOG)
	mkdir -p $($*.gz_PATH)/files $(LOG)
	mkdir -p $($*.gz_PATH)/python-debs $(LOG)
	mkdir -p $($*.gz_PATH)/python-wheels $(LOG)
	sudo mount --bind $(DEBS_PATH) $($*.gz_PATH)/debs $(LOG)
	sudo mount --bind $(FILES_PATH) $($*.gz_PATH)/files $(LOG)
	sudo mount --bind $(PYTHON_DEBS_PATH) $($*.gz_PATH)/python-debs $(LOG)
	sudo mount --bind $(PYTHON_WHEELS_PATH) $($*.gz_PATH)/python-wheels $(LOG)
	# Export variables for j2. Use path for unique variable names, e.g. docker_orchagent_debs
	$(eval export $(subst -,_,$(notdir $($*.gz_PATH)))_debs=$(shell printf "$(subst $(SPACE),\n,$(call expand,$($*.gz_DEPENDS),RDEPENDS))\n" | awk '!a[$$0]++'))
	$(eval export $(subst -,_,$(notdir $($*.gz_PATH)))_pydebs=$(shell printf "$(subst $(SPACE),\n,$(call expand,$($*.gz_PYTHON_DEBS)))\n" | awk '!a[$$0]++'))
	$(eval export $(subst -,_,$(notdir $($*.gz_PATH)))_whls=$(shell printf "$(subst $(SPACE),\n,$(call expand,$($*.gz_PYTHON_WHEELS)))\n" | awk '!a[$$0]++'))
	$(eval export $(subst -,_,$(notdir $($*.gz_PATH)))_dbgs=$(shell printf "$(subst $(SPACE),\n,$(call expand,$($*.gz_DBG_PACKAGES)))\n" | awk '!a[$$0]++'))
	j2 $($*.gz_PATH)/Dockerfile.j2 > $($*.gz_PATH)/Dockerfile
	docker info $(LOG)
	docker build --squash --no-cache \
		--build-arg http_proxy=$(HTTP_PROXY) \
		--build-arg https_proxy=$(HTTPS_PROXY) \
		--build-arg user=$(USER) \
		--build-arg uid=$(UID) \
		--build-arg guid=$(GUID) \
		--build-arg docker_container_name=$($*.gz_CONTAINER_NAME) \
		--build-arg frr_user_uid=$(FRR_USER_UID) \
		--build-arg frr_user_gid=$(FRR_USER_GID) \
		--label Tag=$(SONIC_GET_VERSION) \
		-t $* $($*.gz_PATH) $(LOG)
	docker save $* | gzip -c > $@
	# Clean up
	if [ -f $($*.gz_PATH).patch/series ]; then pushd $($*.gz_PATH) && quilt pop -a -f; popd; fi
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(TARGET_PATH)/, $(DOCKER_IMAGES))

# Targets for building docker images
$(addprefix $(TARGET_PATH)/, $(DOCKER_DBG_IMAGES)) : $(TARGET_PATH)/%-$(DBG_IMAGE_MARK).gz : .platform docker-start \
		$$(addprefix $(DEBS_PATH)/,$$($$*.gz_DBG_DEPENDS)) \
		$$(addsuffix -load,$$(addprefix $(TARGET_PATH)/,$$*.gz))
	$(HEADER)
	mkdir -p $($*.gz_PATH)/debs $(LOG)
	sudo mount --bind $(DEBS_PATH) $($*.gz_PATH)/debs $(LOG)
	# Export variables for j2. Use path for unique variable names, e.g. docker_orchagent_debs
	$(eval export $(subst -,_,$(notdir $($*.gz_PATH)))_dbg_debs=$(shell printf "$(subst $(SPACE),\n,$(call expand,$($*.gz_DBG_DEPENDS),RDEPENDS))\n" | awk '!a[$$0]++'))
	$(eval export $(subst -,_,$(notdir $($*.gz_PATH)))_image_dbgs=$(shell printf "$(subst $(SPACE),\n,$(call expand,$($*.gz_DBG_IMAGE_PACKAGES)))\n" | awk '!a[$$0]++'))
	./build_debug_docker_j2.sh $* $(subst -,_,$(notdir $($*.gz_PATH)))_dbg_debs $(subst -,_,$(notdir $($*.gz_PATH)))_image_dbgs > $($*.gz_PATH)/Dockerfile-dbg.j2
	j2 $($*.gz_PATH)/Dockerfile-dbg.j2 > $($*.gz_PATH)/Dockerfile-dbg
	docker info $(LOG)
	docker build \
		$(if $($*.gz_DBG_DEPENDS), --squash --no-cache, --no-cache) \
		--build-arg http_proxy=$(HTTP_PROXY) \
		--build-arg https_proxy=$(HTTPS_PROXY) \
		--build-arg docker_container_name=$($*.gz_CONTAINER_NAME) \
		--label Tag=$(SONIC_GET_VERSION) \
		--file $($*.gz_PATH)/Dockerfile-dbg \
		-t $*-dbg $($*.gz_PATH) $(LOG)
	docker save $*-dbg | gzip -c > $@
	# Clean up
	if [ -f $($*.gz_PATH).patch/series ]; then pushd $($*.gz_PATH) && quilt pop -a -f; popd; fi
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(TARGET_PATH)/, $(DOCKER_DBG_IMAGES))

DOCKER_LOAD_TARGETS = $(addsuffix -load,$(addprefix $(TARGET_PATH)/, \
		      $(SONIC_SIMPLE_DOCKER_IMAGES) \
		      $(DOCKER_IMAGES)))

$(DOCKER_LOAD_TARGETS) : $(TARGET_PATH)/%.gz-load : .platform docker-start $$(TARGET_PATH)/$$*.gz
	$(HEADER)
	docker load -i $(TARGET_PATH)/$*.gz $(LOG)
	$(FOOTER)

###############################################################################
## Installers
###############################################################################

# targets for building installers with base image
$(addprefix $(TARGET_PATH)/, $(SONIC_INSTALLERS)) : $(TARGET_PATH)/% : \
        .platform \
        onie-image.conf \
        build_debian.sh \
        scripts/dbg_files.sh \
        build_image.sh \
        $$(addsuffix -install,$$(addprefix $(STRETCH_DEBS_PATH)/,$$($$*_DEPENDS))) \
        $$(addprefix $(STRETCH_DEBS_PATH)/,$$($$*_INSTALLS)) \
        $$(addprefix $(STRETCH_DEBS_PATH)/,$$($$*_LAZY_INSTALLS)) \
        $(addprefix $(STRETCH_DEBS_PATH)/,$(INITRAMFS_TOOLS) \
                $(LINUX_KERNEL) \
                $(SONIC_DEVICE_DATA) \
                $(PYTHON_CLICK) \
                $(LIBPAM_TACPLUS) \
                $(LIBNSS_TACPLUS)) \
        $$(addprefix $(TARGET_PATH)/,$$($$*_DOCKERS)) \
        $$(addprefix $(FILES_PATH)/,$$($$*_FILES)) \
        $(addprefix $(STRETCH_FILES_PATH)/,$(IXGBE_DRIVER)) \
        $(addprefix $(PYTHON_DEBS_PATH)/,$(SONIC_UTILS)) \
        $(addprefix $(PYTHON_WHEELS_PATH)/,$(SONIC_CONFIG_ENGINE)) \
        $(addprefix $(PYTHON_WHEELS_PATH)/,$(SONIC_PLATFORM_COMMON_PY2)) \
        $(addprefix $(PYTHON_WHEELS_PATH)/,$(REDIS_DUMP_LOAD_PY2))
	$(HEADER)
	# Pass initramfs and linux kernel explicitly. They are used for all platforms
	export debs_path="$(STRETCH_DEBS_PATH)"
	export files_path="$(FILES_PATH)"
	export python_debs_path="$(PYTHON_DEBS_PATH)" 
	export initramfs_tools="$(STRETCH_DEBS_PATH)/$(INITRAMFS_TOOLS)"
	export linux_kernel="$(STRETCH_DEBS_PATH)/$(LINUX_KERNEL)"
	export onie_recovery_image="$(FILES_PATH)/$(ONIE_RECOVERY_IMAGE)"
	export kversion="$(KVERSION)"
	export image_type="$($*_IMAGE_TYPE)"
	export sonicadmin_user="$(USERNAME)"
	export sonic_asic_platform="$(CONFIGURED_PLATFORM)"
	export enable_organization_extensions="$(ENABLE_ORGANIZATION_EXTENSIONS)"
	export enable_dhcp_graph_service="$(ENABLE_DHCP_GRAPH_SERVICE)"
	export shutdown_bgp_on_start="$(SHUTDOWN_BGP_ON_START)"
	export enable_pfcwd_on_start="$(ENABLE_PFCWD_ON_START)"
	export installer_debs="$(addprefix $(STRETCH_DEBS_PATH)/,$($*_INSTALLS))"
	export lazy_installer_debs="$(foreach deb, $($*_LAZY_INSTALLS),$(foreach device, $($(deb)_PLATFORM),$(addprefix $(device)@, $(STRETCH_DEBS_PATH)/$(deb))))"
	export installer_images="$(addprefix $(TARGET_PATH)/,$($*_DOCKERS))"
	export config_engine_wheel_path="$(addprefix $(PYTHON_WHEELS_PATH)/,$(SONIC_CONFIG_ENGINE))"
	export swsssdk_py2_wheel_path="$(addprefix $(PYTHON_WHEELS_PATH)/,$(SWSSSDK_PY2))"
	export platform_common_py2_wheel_path="$(addprefix $(PYTHON_WHEELS_PATH)/,$(SONIC_PLATFORM_COMMON_PY2))"
	export redis_dump_load_py2_wheel_path="$(addprefix $(PYTHON_WHEELS_PATH)/,$(REDIS_DUMP_LOAD_PY2))"
	export install_debug_image="$(INSTALL_DEBUG_TOOLS)"

	$(foreach docker, $($*_DOCKERS),\
		export docker_image="$(docker)"
		export docker_image_name="$(basename $(docker))"
		export docker_container_name="$($(docker:-dbg.gz=.gz)_CONTAINER_NAME)"
		$(eval $(docker:-dbg.gz=.gz)_RUN_OPT += $($(docker:-dbg.gz=.gz)_$($*_IMAGE_TYPE)_RUN_OPT))
		export docker_image_run_opt="$($(docker:-dbg.gz=.gz)_RUN_OPT)"
		j2 files/build_templates/docker_image_ctl.j2 > $($(docker:-dbg.gz=.gz)_CONTAINER_NAME).sh
		if [ -f files/build_templates/$($(docker:-dbg.gz=.gz)_CONTAINER_NAME).service.j2 ]; then
			j2 files/build_templates/$($(docker:-dbg.gz=.gz)_CONTAINER_NAME).service.j2 > $($(docker:-dbg.gz=.gz)_CONTAINER_NAME).service
		fi
		chmod +x $($(docker:-dbg.gz=.gz)_CONTAINER_NAME).sh
	)

	export installer_start_scripts="$(foreach docker, $($*_DOCKERS),$(addsuffix .sh, $($(docker:-dbg.gz=.gz)_CONTAINER_NAME)))"
	export installer_services="$(foreach docker, $($*_DOCKERS),$(addsuffix .service, $($(docker:-dbg.gz=.gz)_CONTAINER_NAME)))"
	export installer_extra_files="$(foreach docker, $($*_DOCKERS), $(foreach file, $($(docker:-dbg.gz=.gz)_BASE_IMAGE_FILES), $($(docker:-dbg.gz=.gz)_PATH)/base_image_files/$(file)))"

	j2 -f env files/initramfs-tools/union-mount.j2 onie-image.conf > files/initramfs-tools/union-mount
	j2 -f env files/initramfs-tools/arista-convertfs.j2 onie-image.conf > files/initramfs-tools/arista-convertfs

	j2 files/build_templates/updategraph.service.j2 > updategraph.service

	$(if $($*_DOCKERS),
		j2 files/build_templates/sonic_debian_extension.j2 > sonic_debian_extension.sh
		chmod +x sonic_debian_extension.sh,
	)

	export debug_src_archive="$(DBG_SRC_ARCHIVE)"

	DEBUG_IMG="$(INSTALL_DEBUG_TOOLS)" \
	USERNAME="$(USERNAME)" \
	PASSWORD="$(PASSWORD)" \
		./build_debian.sh $(LOG)

	USERNAME="$(USERNAME)" \
	PASSWORD="$(PASSWORD)" \
	TARGET_MACHINE=$($*_MACHINE) \
	IMAGE_TYPE=$($*_IMAGE_TYPE) \
		./build_image.sh $(LOG)

	$(foreach docker, $($*_DOCKERS), \
		rm -f $($(docker:-dbg.gz=.gz)_CONTAINER_NAME).sh
		rm -f $($(docker:-dbg.gz=.gz)_CONTAINER_NAME).service
	)

	$(if $($*_DOCKERS),
		rm sonic_debian_extension.sh,
	)

	chmod a+x $@
	$(FOOTER)

SONIC_TARGET_LIST += $(addprefix $(TARGET_PATH)/, $(SONIC_INSTALLERS))

###############################################################################
## Clean targets
###############################################################################

SONIC_CLEAN_DEBS = $(addsuffix -clean,$(addprefix $(DEBS_PATH)/, \
		   $(SONIC_ONLINE_DEBS) \
		   $(SONIC_COPY_DEBS) \
		   $(SONIC_MAKE_DEBS) \
		   $(SONIC_DPKG_DEBS) \
		   $(SONIC_PYTHON_STDEB_DEBS) \
		   $(SONIC_DERIVED_DEBS) \
		   $(SONIC_EXTRA_DEBS)))

SONIC_CLEAN_FILES = $(addsuffix -clean,$(addprefix $(FILES_PATH)/, \
		   $(SONIC_ONLINE_FILES) \
		   $(SONIC_COPY_FILES) \
		   $(SONIC_MAKE_FILES)))

$(SONIC_CLEAN_DEBS) : $(DEBS_PATH)/%-clean : .platform $$(addsuffix -clean,$$(addprefix $(DEBS_PATH)/,$$($$*_MAIN_DEB)))
	@# remove derived or extra targets if main one is removed, because we treat them
	@# as part of one package
	@rm -f $(addprefix $(DEBS_PATH)/, $* $($*_DERIVED_DEBS) $($*_EXTRA_DEBS))

$(SONIC_CLEAN_FILES) : $(FILES_PATH)/%-clean : .platform
	@rm -f $(FILES_PATH)/$*

SONIC_CLEAN_TARGETS += $(addsuffix -clean,$(addprefix $(TARGET_PATH)/, \
		       $(SONIC_DOCKER_IMAGES) \
		       $(SONIC_DOCKER_DBG_IMAGES) \
		       $(SONIC_SIMPLE_DOCKER_IMAGES) \
		       $(SONIC_INSTALLERS)))
$(SONIC_CLEAN_TARGETS) : $(TARGET_PATH)/%-clean : .platform
	@rm -f $(TARGET_PATH)/$*

SONIC_CLEAN_WHEELS = $(addsuffix -clean,$(addprefix $(PYTHON_WHEELS_PATH)/, \
		     $(SONIC_PYTHON_WHEELS)))
$(SONIC_CLEAN_WHEELS) : $(PYTHON_WHEELS_PATH)/%-clean : .platform
	@rm -f $(PYTHON_WHEELS_PATH)/$*

clean-logs : .platform
	@rm -f $(TARGET_PATH)/*.log $(DEBS_PATH)/*.log $(FILES_PATH)/*.log $(PYTHON_WHEELS_PATH)/*.log

clean : .platform clean-logs $$(SONIC_CLEAN_DEBS) $$(SONIC_CLEAN_FILES) $$(SONIC_CLEAN_TARGETS) $$(SONIC_CLEAN_WHEELS)

###############################################################################
## all
###############################################################################

all : .platform $$(addprefix $(TARGET_PATH)/,$$(SONIC_ALL))

stretch : $$(addprefix $(DEBS_PATH)/,$$(SONIC_STRETCH_DEBS)) \
          $$(addprefix $(FILES_PATH)/,$$(SONIC_STRETCH_FILES)) \
          $$(addprefix $(TARGET_PATH)/,$$(SONIC_STRETCH_DOCKERS_FOR_INSTALLERS)) \
          $$(addprefix $(TARGET_PATH)/,$$(SONIC_STRETCH_DBG_DOCKERS_FOR_INSTALLERS))

jessie : $$(addprefix $(TARGET_PATH)/,$$(SONIC_JESSIE_DOCKERS_FOR_INSTALLERS))

###############################################################################
## Standard targets
###############################################################################

.PHONY : $(SONIC_CLEAN_DEBS) $(SONIC_CLEAN_FILES) $(SONIC_CLEAN_TARGETS) $(SONIC_CLEAN_WHEELS) $(SONIC_PHONY_TARGETS) clean distclean configure

.INTERMEDIATE : $(SONIC_INSTALL_TARGETS) $(SONIC_INSTALL_WHEELS) $(DOCKER_LOAD_TARGETS) docker-start .platform
