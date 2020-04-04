LIBNL_CFLAGS = -I/usr/include/libnl3 
LIBNL_LIBS = -lnl-cli-3 -lnl-genl-3 -lnl-nf-3 -lnl-route-3 -lnl-3 

CC = gcc
SOURCES = app_csm.c cmd_option.c iccp_cli.c iccp_cmd_show.c iccp_cmd.c \
iccp_csm.c iccp_ifm.c iccp_main.c logger.c \
port.c scheduler.c system.c iccp_consistency_check.c \
mlacp_link_handler.c \
mlacp_sync_prepare.c mlacp_sync_update.c\
mlacp_fsm.c \
iccp_netlink.c

OBJECTS = app_csm.o cmd_option.o iccp_cli.o iccp_cmd_show.o iccp_cmd.o \
iccp_csm.o iccp_ifm.o iccp_main.o logger.o \
port.o scheduler.o system.o  iccp_consistency_check.o\
mlacp_link_handler.o \
mlacp_sync_prepare.o mlacp_sync_update.o \
mlacp_fsm.o \
iccp_netlink.o

HEADERS = ../include/app_csm.h ../include/cmd_option.h ../include/iccp_cli.h \
../include/iccp_cmd_show.h \
../include/iccp_csm.h ../include/iccp_ifm.h \
../include/logger.h ../include/mlacp_fsm.h \
../include/mlacp_tlv.h ../include/msg_format.h ../include/port.h \
../include/scheduler.h ../include/system.h \
../include/iccp_consistency_check.h ../include/route_info.h  \
../include/iccp_netlink.h

//CFLAGS  = -g -O2 -fstack-protector-strong -Wformat -Werror=format-security  $(LIBNL_CFLAGS) -I../include/ 
CFLAGS  = -g -O2 -fstack-protector-strong -Wformat -Werror=format-security  -I../include/ $(LIBNL_CFLAGS) 
LDFLAGS = $(LIBNL_LIBS) -lpthread
LDADD   = $(LIBZEBRA_BIN) 

all: iccpd

%.o: %.c $(HEADERS)

iccpd: $(OBJECTS)
	$(CC) -o ../iccpd $(OBJECTS) $(LDFLAGS)

DEPS = $(patsubst %.o, %.d, $(OBJECTS))

-include $(DEPS)
%.d:%.c
	@set -e; rm -f $@; \
	gcc -MM $(CPPFLAGS) $< > $@.$$$$; \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	rm -f $@.$$$$



.PHONY: clean
clean:
	-rm -f $(OBJECTS) $(DEPS) ../iccpd
