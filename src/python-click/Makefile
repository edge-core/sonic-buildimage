.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = python-click_$(PYTHON_CLICK_VERSION)_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./python-click

	# Clone python-click Debian repo
	git clone https://salsa.debian.org/debian/python-click

	pushd ./python-click

	# Reset HEAD to the commit of the proper tag
	# NOTE: Using "git checkout <tag_name>" here detaches our HEAD,
	# which stg doesn't like, so we use this method instead
	git reset --hard debian/$(PYTHON_CLICK_VERSION)

	# Build source and Debian packages
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	# Move the newly-built .deb package to the destination directory
	mv $* $(DEST)/
