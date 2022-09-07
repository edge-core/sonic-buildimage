import typing
from natsort import natsorted
import datetime
import pickle
import os
import copy

import click
from tabulate import tabulate

import utilities_common.multi_asic as multi_asic_util
from swsscommon.swsscommon import CounterTable, MacsecCounter
from utilities_common.cli import UserCache

CACHE_MANAGER = UserCache(app_name="macsec")
CACHE_FILE = os.path.join(CACHE_MANAGER.get_directory(), "macsecstats{}")

DB_CONNECTOR = None
COUNTER_TABLE = None


class MACsecAppMeta(object):
    def __init__(self, *args) -> None:
        SEPARATOR = DB_CONNECTOR.get_db_separator(DB_CONNECTOR.APPL_DB)
        self.key = self.__class__.get_appl_table_name() + SEPARATOR + \
            SEPARATOR.join(args)
        self.meta = DB_CONNECTOR.get_all(
            DB_CONNECTOR.APPL_DB, self.key)
        if len(self.meta) == 0:
            raise ValueError("No such MACsecAppMeta: {}".format(self.key))
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

    def dump_str(self, cache = None) -> str:
        buffer = self.get_header()
        meta = sorted(self.meta.items(), key=lambda x: x[0])
        counters = copy.deepcopy(self.counters)
        if cache:
            for k, v in counters.items():
                if k in cache.counters:
                    counters[k] = int(counters[k]) - int(cache.counters[k])
        counters = sorted(counters.items(), key=lambda x: x[0])
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

    def dump_str(self, cache = None) -> str:
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

    def dump_str(self, cache = None) -> str:
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

    def dump_str(self, cache = None) -> str:
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


def cache_find(cache: dict, target: MACsecAppMeta) -> MACsecAppMeta:
    if not cache or not cache["objs"]:
        return None
    for obj in cache["objs"]:
        if type(obj) == type(target) and obj.key == target.key:
            # MACsec SA may be refreshed by a cycle that use the same key
            # So, use the SA as the identifier
            if isinstance(obj, MACsecSA) and obj.sak != target.sak:
                continue
            return obj
    return None


@click.command()
@click.argument('interface_name', required=False)
@click.option('--dump-file', is_flag=True, required=False, default=False)
@multi_asic_util.multi_asic_click_options
def macsec(interface_name, dump_file, namespace, display):
    MacsecContext(namespace, display).show(interface_name, dump_file)

class MacsecContext(object):

    def __init__(self, namespace_option, display_option):
        self.db = None
        self.multi_asic = multi_asic_util.MultiAsic(
            display_option, namespace_option)

    @multi_asic_util.run_on_multi_asic
    def show(self, interface_name, dump_file):
        global DB_CONNECTOR
        global COUNTER_TABLE
        DB_CONNECTOR = self.db
        COUNTER_TABLE = CounterTable(self.db.get_redis_client(self.db.COUNTERS_DB))

        interface_names = [name.split(":")[1] for name in self.db.keys(self.db.APPL_DB, "MACSEC_PORT*")]
        if interface_name is not None:
            if interface_name not in interface_names:
                return
            interface_names = [interface_name]
        objs = []

        for interface_name in natsorted(interface_names):
            objs += create_macsec_objs(interface_name)

        cache = {}
        if os.path.isfile(CACHE_FILE.format(self.multi_asic.current_namespace)):
            cache = pickle.load(open(CACHE_FILE.format(self.multi_asic.current_namespace), "rb"))

        if not dump_file:
            if cache and cache["time"] and objs:
                print("Last cached time was {}".format(cache["time"]))
            for obj in objs:
                cache_obj = cache_find(cache, obj)
                print(obj.dump_str(cache_obj))
        else:
            dump_obj = {
                "time": datetime.datetime.now(),
                "objs": objs
            }
            with open(CACHE_FILE.format(self.multi_asic.current_namespace), 'wb') as dump_file:
                pickle.dump(dump_obj, dump_file)
                dump_file.flush()

def register(cli):
    cli.add_command(macsec)


if __name__ == '__main__':
    macsec(None)
