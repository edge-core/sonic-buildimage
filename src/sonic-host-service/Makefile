################################################################################
#                                                                              #
#  Copyright 2020 Dell Inc.                                                    #
#                                                                              #
#  Licensed under the Apache License, Version 2.0 (the "License");             #
#  you may not use this file except in compliance with the License.            #
#  You may obtain a copy of the License at                                     #
#                                                                              #
#     http://www.apache.org/licenses/LICENSE-2.0                               #
#                                                                              #
#  Unless required by applicable law or agreed to in writing, software         #
#  distributed under the License is distributed on an "AS IS" BASIS,           #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
#  See the License for the specific language governing permissions and         #
#  limitations under the License.                                              #
#                                                                              #
################################################################################

TOPDIR := $(abspath .)
MAIN_TARGET = sonic-host-service_1.0.0_all.deb
INSTALL := /usr/bin/install

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	dpkg-buildpackage -us -uc -b
	mv ../$(MAIN_TARGET) $(DEST)/

SOURCES := $(wildcard '*.*') $(wildcard 'host_modules/*.py')
install: $(SOURCES)
	# Scripts for host service
	$(INSTALL) -d $(DESTDIR)/usr/lib/sonic_host_service/host_modules
	$(INSTALL) -D $(TOPDIR)/sonic_host_server.py $(DESTDIR)/usr/lib/sonic_host_service
	$(INSTALL) -D $(TOPDIR)/host_modules/*.py $(DESTDIR)/usr/lib/sonic_host_service/host_modules

	# D-Bus permissions configuration
	$(INSTALL) -d $(DESTDIR)/etc/dbus-1/system.d
	$(INSTALL) -D $(TOPDIR)/org.sonic.hostservice.conf $(DESTDIR)/etc/dbus-1/system.d

	# systemd unit
	$(INSTALL) -d $(DESTDIR)/lib/systemd/system
	$(INSTALL) -D $(TOPDIR)/sonic-hostservice.service $(DESTDIR)/lib/systemd/system

