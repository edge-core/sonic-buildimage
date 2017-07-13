.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = python-supervisor_3.3.2-1_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./supervisor

	# Clone isc-dhcp repo
	git clone git://github.com/Supervisor/supervisor.git
	pushd ./supervisor
	git checkout -f 3.3.2

	# Build Python and Debian package
	python setup.py --command-packages=stdeb.command bdist_deb
	popd

	# Move the newly-built .deb packages to the destination directory
	mv ./supervisor/deb_dist/$* $(DEST)/
