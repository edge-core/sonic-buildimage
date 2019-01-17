.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = issu-version

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	sx_sdk --version | egrep -o 'ISSU [0-9]+' > $(DEST)/$(MAIN_TARGET) || {
		echo "ISSU version is undefined: $(sx_sdk --version)"
		rm $(DEST)/$(MAIN_TARGET)
		exit 1
	}
