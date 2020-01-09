export GOPATH=/tmp/go

INSTALL := /usr/bin/install

all: telemetry

telemetry:
	mkdir -p ${GOPATH}/src/github.com/Azure/
	cp -a sonic-telemetry ${GOPATH}/src/github.com/Azure/
	/usr/local/go/bin/go get -v github.com/Azure/sonic-telemetry/telemetry
	/usr/local/go/bin/go get -v github.com/Azure/sonic-telemetry/dialout/dialout_client_cli

install:
	$(INSTALL) -D ${GOPATH}/bin/telemetry $(DESTDIR)/usr/sbin/telemetry
	$(INSTALL) -D ${GOPATH}/bin/dialout_client_cli $(DESTDIR)/usr/sbin/dialout_client_cli

deinstall:
	rm $(DESTDIR)/usr/sbin/telemetry
	rm $(DESTDIR)/usr/sbin/dialout_client_cli

clean:
	rm -fr ${GOPATH}
