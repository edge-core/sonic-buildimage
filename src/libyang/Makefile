.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(LIBYANG)
DERIVED_TARGETS = $(LIBYANG_DEV) $(LIBYANG_DBG) $(LIBYANG_PY2) $(LIBYANG_PY3) $(LIBYANG_CPP)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
        # Obtaining the libyang
	rm -fr ./libyang-$(LIBYANG_VERSION)
	git clone https://github.com/CESNET/libyang.git libyang-$(LIBYANG_VERSION)
	pushd libyang-$(LIBYANG_VERSION)
	git checkout tags/v1.0-r4 -b libyang
	# Apply patch series
	stg init
	stg import -s ../patch/series

	mkdir build
	pushd build
	cmake ..
	make build-deb

	pushd debs
	mv $* $(DEST)/
	mv $(DERIVED_TARGETS) $(DEST)/
	popd

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
