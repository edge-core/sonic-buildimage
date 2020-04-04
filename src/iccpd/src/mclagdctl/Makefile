

C = gcc
SOURCES = \
mclagdctl.c

OBJECTS = \
mclagdctl.o

HEADERS = \
mclagdctl.h

CFLAGS  = -g -O2 -fstack-protector-strong -Wformat -Werror=format-security 
LDFLAGS =
LDADD   =

all: mclagdctl

%.o: %.c $(HEADERS)

mclagdctl: $(OBJECTS)
	$(CC) -o ./mclagdctl $(OBJECTS) $(LDFLAGS)

.PHONY: clean
clean:
	-rm -f $(OBJECTS) ./mclagdctl


