#!/bin/bash
export DELL_TOOLS_DIR="platform/broadcom/sonic-platform-modules-dell/tools"

cd $DELL_TOOLS_DIR
rm -rf $DELL_TOOLS_DIR/flashrom
git clone https://github.com/flashrom/flashrom.git
cd flashrom
git checkout tags/0.9.7
git apply ../0002-Flashrom-support-for-Intel-Rangeley-and-Denverton-CP.patch
make
