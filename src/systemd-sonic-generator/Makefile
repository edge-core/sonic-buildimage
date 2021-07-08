CC=gcc
CFLAGS=-std=gnu99 -D_GNU_SOURCE

CPP=g++
CPPFLAGS=-std=c++11 -D_GNU_SOURCE
LFLAGS=-lpthread -lboost_filesystem -lboost_system -lgtest

BINARY = systemd-sonic-generator
MAIN_TARGET = $(BINARY)_1.0.0_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	mv ../$(MAIN_TARGET) $(DEST)/
	rm ../$(BINARY)-* ../$(BINARY)_*

$(BINARY): systemd-sonic-generator.c
	rm -f ./systemd-sonic-generator

	$(CC) $(CFLAGS) -o $@ $^

install: $(BINARY)
	mkdir -p $(DESTDIR)
	mkdir -p $(DESTDIR)/lib
	mkdir -p $(DESTDIR)/lib/systemd
	mkdir -p $(DESTDIR)/lib/systemd/system-generators
	cp ./systemd-sonic-generator $(DESTDIR)/lib/systemd/system-generators

.PHONY: test
test: ssg_test
	./ssg_test

ssg_test: ssg-test.cc systemd-sonic-generator.o
	$(CPP) $(CPPFLAGS) -o $@ $^ $(LFLAGS)

systemd-sonic-generator.o: systemd-sonic-generator.c
	$(CC) $(CFLAGS) -D_SSG_UNITTEST -o $@ -c $^

clean:
	rm -f ./systemd-sonic-generator
	rm -f ./systemd-sonic-generator.o
	rm -f ./ssg_test
