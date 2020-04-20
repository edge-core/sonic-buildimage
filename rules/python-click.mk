# python-click package
#
# Python Click versions < 6.7 have a bug which causes bash completion
# functionality to stop working after two sublevels. sonic-utilities depends
# on this package, and the most recent version provided by Debian Jessie and
# Stretch is v6.6. We build version 6.7 from source in order to fix this bug.
# TODO: If we upgrade to a distro which provides a version >= 6.7 we will no
# longer need to build this.

PYTHON_CLICK_VERSION = 7.0-1

export PYTHON_CLICK_VERSION

PYTHON_CLICK = python-click_$(PYTHON_CLICK_VERSION)_all.deb
$(PYTHON_CLICK)_SRC_PATH = $(SRC_PATH)/python-click
SONIC_MAKE_DEBS += $(PYTHON_CLICK)
