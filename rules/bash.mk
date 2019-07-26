# bash package
#
# Created to patch memory-leak issue in the bash-package included in Debian-8 (Jessie)
# release. This rule file, and the associated building-infra created to solve this
# bug (src/bash/), should be eliminated once the migration to Debian-9 (Stretch) is
# completed.

# Bash major release-number corresponding to Debian-8 (Jessie)
BASH_VERSION_MAJOR = 4.3
# Bash complete release-number. This image contains all 4.3 fixes  up to patch '42'.
BASH_VERSION_FULL = $(BASH_VERSION_MAJOR)-14

export BASH_VERSION_MAJOR BASH_VERSION_FULL

BASH = bash_$(BASH_VERSION_FULL)_$(CONFIGURED_ARCH).deb
$(BASH)_SRC_PATH = $(SRC_PATH)/bash
SONIC_MAKE_DEBS += $(BASH)
