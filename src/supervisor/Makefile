.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = python-supervisor_$(SUPERVISOR_VERSION)-1_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./supervisor

	# Clone supervisor repo
	git clone https://github.com/Supervisor/supervisor.git
	pushd ./supervisor

	# Reset HEAD to the commit of the proper tag
	# NOTE: Using "git checkout <tag_name>" here detaches our HEAD,
	# which stg doesn't like, so we use this method instead
	git reset --hard $(SUPERVISOR_VERSION)

	# Apply patches
	stg init
	stg import -s ../patch/series

ifneq (,$(filter $(CONFIGURED_ARCH), armhf arm64))
	stg import -s ../patch/series-armhf
endif

	# Build Python and Debian package
	python setup.py --command-packages=stdeb.command bdist_deb
	popd

	# Move the newly-built .deb packages to the destination directory
	mv ./supervisor/deb_dist/$* $(DEST)/
