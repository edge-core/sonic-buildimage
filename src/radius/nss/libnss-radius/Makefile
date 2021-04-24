#######################################################################
#
# Copyright 2019 Broadcom. All rights reserved.
# The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.
#
#######################################################################

#
# Makefile for libnss-radius
#

TARGETS = libnss_radius.so.2 cache_radius
COMMON_INCLUDE = nss_radius_common.h
COMMON_SOURCE = nss_radius_common.c
LIBNSS_SOURCE = nss_radius.c $(COMMON_SOURCE)
CACHE_SOURCE = cache_radius.c $(COMMON_SOURCE)

# For now place the multiarch flag here
# Eventually this needs to be move to the debian packaging
#moduledir = $(prefix)/lib/x86_64-linux-gnu
moduledir = $(prefix)/lib/$(DEB_HOST_MULTIARCH)


all: $(TARGETS)

libnss_radius.so.2: $(LIBNSS_SOURCE) $(COMMON_INCLUDE)
	$(CC) $(CFLAGS) $(LDFLAGS) -fPIC -Wall -shared -o libnss_radius.so.2 \
		-Wl,-soname,libnss_radius.so.2 -Wl,--version-script=libnss_radius_vs.txt $(LIBNSS_SOURCE)

cache_radius: $(CACHE_SOURCE) $(COMMON_INCLUDE)
	$(CC) $(CFLAGS) $(LDFLAGS) -o cache_radius $(CACHE_SOURCE)

clean:
	-rm -f $(TARGETS)
	-rm -f test_nss_radius test_cache_radius

install: libnss_radius.so.2 cache_radius
	install -m 0644 -D libnss_radius.so.2 \
		$(DESTDIR)$(moduledir)/libnss_radius.so.2
	install -m 0755 -D cache_radius \
		$(DESTDIR)$(prefix)/usr/sbin/cache_radius
	install -m 0755 -d $(DESTDIR)$(prefix)/etc/pam_radius_auth.d/

distclean: clean

uninstall:
	-rm -f $(DESTDIR)$(moduledir)/libnss_radius.so.2
	-rm -f $(DESTDIR)$(prefix)/usr/sbin/cache_radius

test: test_nss_radius.c $(LIBNSS_SOURCE) $(CACHE_SOURCE) \
		$(COMMON_SOURCE) $(COMMON_INCLUDE)
	$(CC) $(CFLAGS) $(LDFLAGS) -g -DTEST_RADIUS_NSS -o test_nss_radius \
		$(LIBNSS_SOURCE) test_nss_radius.c
	$(CC) $(CFLAGS) $(LDFLAGS) -g -DTEST_RADIUS_NSS -o test_cache_radius \
		$(CACHE_SOURCE)
	

.PHONY: all install clean distclean uninstall test

