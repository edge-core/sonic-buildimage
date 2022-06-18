import typing
from natsort import natsorted

import click
from tabulate import tabulate

from swsscommon.swsscommon import SonicV2Connector
from swsscommon.swsscommon import CounterTable, MacsecCounter


DB_CONNECTOR = SonicV2Connector(use_unix_socket_path=False)
DB_CONNECTOR.connect(DB_CONNECTOR.APPL_DB)
DB_CONNECTOR.connect(DB_CONNECTOR.COUNTERS_DB)
COUNTER_TABLE = CounterTable(DB_CONNECTOR.get_redis_client(DB_CONNECTOR.COUNTERS_DB))


class MACsecAppMeta(object):
    SEPARATOR = DB_CONNECTOR.get_db_separator(DB_CONNECTOR.APPL_DB)

    def __init__(self, *args) -> None:
        key = self.__class__.get_appl_table_name() + MACsecAppMeta.SEPARATOR + \
            MACsecAppMeta.SEPARATOR.join(args)
        self.meta = DB_CONNECTOR.get_all(
            DB_CONNECTOR.APPL_DB, key)
        if len(self.meta) == 0:
            raise ValueError("No such MACsecAppMeta: {}".format(key))
        for k, v in self.meta.items():
            setattr(self, k, v)


class MACsecCounters(object):
    def __init__(self, *args) -> None:
        _, fvs = COUNTER_TABLE.get(MacsecCounter(), ":".join(args))
        self.counters = dict(fvs)


class MACsecSA(MACsecAppMeta, MACsecCounters):
    def __init__(self, port_name: str, sci: str, an: str) -> None:
        self.port_name = port_name
        self.sci = sci
        self.an = an
        MACsecAppMeta.__init__(self, port_name, sci, an)
        MACsecCounters.__init__(self, port_name, sci, an)

    def dump_str(self) -> str:
        buffer = self.get_header()
        meta = sorted(self.meta.items(), key=lambda x: x[0])
        counters = sorted(self.counters.items(), key=lambda x: x[0])
        buffer += tabulate(meta + counters)
        buffer = "\n".join(["\t\t" + line for line in buffer.splitlines()])
        return buffer


class MACsecIngressSA(MACsecSA):
    def __init__(self, port_name: str, sci: str, an: str) -> None:
        super(MACsecIngressSA, self).__init__(port_name, sci, an)

    @classmethod
    def get_appl_table_name(cls) -> str:
        return "MACSEC_INGRESS_SA_TABLE"

    def get_header(self):
        return "MACsec Ingress SA ({})\n".format(self.an)


class MACsecEgressSA(MACsecSA):
    def __init__(self, port_name: str, sci: str, an: str) -> None:
        super(MACsecEgressSA, self).__init__(port_name, sci, an)

    @classmethod
    def get_appl_table_name(cls) -> str:
        return "MACSEC_EGRESS_SA_TABLE"

    def get_header(self):
        return "MACsec Egress SA ({})\n".format(self.an)


class MACsecSC(MACsecAppMeta):
    def __init__(self, port_name: str, sci: str) -> None:
        self.port_name = port_name
        self.sci = sci
        super(MACsecSC, self).__init__(port_name, sci)


class MACsecIngressSC(MACsecSC):
    def __init__(self, port_name: str, sci: str) -> None:
        super(MACsecIngressSC, self).__init__(port_name, sci)

    @classmethod
    def get_appl_table_name(cls) -> str:
        return "MACSEC_INGRESS_SC_TABLE"

    def dump_str(self) -> str:
        buffer = self.get_header()
        buffer = "\n".join(["\t" + line for line in buffer.splitlines()])
        return buffer

    def get_header(self):
        return "MACsec Ingress SC ({})\n".format(self.sci)


class MACsecEgressSC(MACsecSC):
    def __init__(self, port_name: str, sci: str) -> None:
        super(MACsecEgressSC, self).__init__(port_name, sci)

    @classmethod
    def get_appl_table_name(cls) -> str:
        return "MACSEC_EGRESS_SC_TABLE"

    def dump_str(self) -> str:
        buffer = self.get_header()
        buffer += tabulate(sorted(self.meta.items(), key=lambda x: x[0]))
        buffer = "\n".join(["\t" + line for line in buffer.splitlines()])
        return buffer

    def get_header(self):
        return "MACsec Egress SC ({})\n".format(self.sci)


class MACsecPort(MACsecAppMeta):
    def __init__(self,  port_name: str) -> None:
        self.port_name = port_name
        super(MACsecPort, self).__init__(port_name)

    @classmethod
    def get_appl_table_name(cls) -> str:
        return "MACSEC_PORT_TABLE"

    def dump_str(self) -> str:
        buffer = self.get_header()
        buffer += tabulate(sorted(self.meta.items(), key=lambda x: x[0]))
        return buffer

    def get_header(self) -> str:
        return "MACsec port({})\n".format(self.port_name)


def create_macsec_obj(key: str) -> MACsecAppMeta:
    attr = key.split(":")
    try:
        if attr[0] == MACsecPort.get_appl_table_name():
            return MACsecPort(attr[1])
        elif attr[0] == MACsecIngressSC.get_appl_table_name():
            return MACsecIngressSC(attr[1], attr[2])
        elif attr[0] == MACsecEgressSC.get_appl_table_name():
            return MACsecEgressSC(attr[1], attr[2])
        elif attr[0] == MACsecIngressSA.get_appl_table_name():
            return MACsecIngressSA(attr[1], attr[2], attr[3])
        elif attr[0] == MACsecEgressSA.get_appl_table_name():
            return MACsecEgressSA(attr[1], attr[2], attr[3])
        raise TypeError("Unknown MACsec object type")
    except ValueError as e:
        return None

def create_macsec_objs(interface_name: str) -> typing.List[MACsecAppMeta]:
    objs = []
    objs.append(create_macsec_obj(MACsecPort.get_appl_table_name() + ":" + interface_name))
    egress_scs = DB_CONNECTOR.keys(DB_CONNECTOR.APPL_DB, MACsecEgressSC.get_appl_table_name() + ":" + interface_name + ":*")
    for sc_name in natsorted(egress_scs):
        sc = create_macsec_obj(sc_name)
        if sc is None:
            continue
        objs.append(sc)
        egress_sas = DB_CONNECTOR.keys(DB_CONNECTOR.APPL_DB, MACsecEgressSA.get_appl_table_name() + ":" + ":".join(sc_name.split(":")[1:]) + ":*")
        for sa_name in natsorted(egress_sas):
            sa = create_macsec_obj(sa_name)
            if sa is None:
                continue
            objs.append(sa)
    ingress_scs = DB_CONNECTOR.keys(DB_CONNECTOR.APPL_DB, MACsecIngressSC.get_appl_table_name() + ":" + interface_name + ":*")
    for sc_name in natsorted(ingress_scs):
        sc = create_macsec_obj(sc_name)
        if sc is None:
            continue
        objs.append(sc)
        ingress_sas = DB_CONNECTOR.keys(DB_CONNECTOR.APPL_DB, MACsecIngressSA.get_appl_table_name() + ":" + ":".join(sc_name.split(":")[1:]) + ":*")
        for sa_name in natsorted(ingress_sas):
            sa = create_macsec_obj(sa_name)
            if sa is None:
                continue
            objs.append(sa)
    return objs


@click.command()
@click.argument('interface_name', required=False)
def macsec(interface_name):
    ctx = click.get_current_context()
    objs = []
    interface_names = [name.split(":")[1] for name in DB_CONNECTOR.keys(DB_CONNECTOR.APPL_DB, "MACSEC_PORT*")]
    if interface_name is not None:
        if interface_name not in interface_names:
            ctx.fail("Cannot find the port {} in MACsec port lists {}".format(interface_name, interface_names))
        else:
            interface_names = [interface_name]
    for interface_name in natsorted(interface_names):
        objs += create_macsec_objs(interface_name)
    for obj in objs:
        print(obj.dump_str())


def register(cli):
    cli.add_command(macsec)


if __name__ == '__main__':
    macsec(None)
