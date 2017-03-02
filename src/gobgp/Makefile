export GOPATH=/tmp/go

INSTALL := /usr/bin/install

all: gobgp gobgpd

gobgpd:
	go get -v github.com/osrg/gobgp/gobgpd

gobgp:
	go get -v github.com/osrg/gobgp/gobgp

install:
	$(INSTALL) -D ${GOPATH}/bin/gobgp $(DESTDIR)/usr/bin/gobgp
	$(INSTALL) -D ${GOPATH}/bin/gobgpd $(DESTDIR)/usr/sbin/gobgpd
	$(INSTALL) -D gobgpd.conf.sample $(DESTDIR)/etc/gobgp/gobgpd.conf.sample

deinstall:
	rm $(DESTDIR)/usr/bin/gobgp
	rm $(DESTDIR)/usr/sbin/gobgpd

clean:
	rm -fr ${GOPATH}
