.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

test:
	# Execute Broadcom config file test
	pushd ../tests/
	for f in $$(find ../../../device -name "*.config.bcm"); do
		./config_checker $$f
	done
	popd
