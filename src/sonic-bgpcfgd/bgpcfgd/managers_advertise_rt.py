from .manager import Manager
from .template import TemplateFabric
from swsscommon import swsscommon


class AdvertiseRouteMgr(Manager):
    """ This class Advertises routes when ADVERTISE_NETWORK_TABLE in STATE_DB is updated """
    def __init__(self, common_objs, db, table):
        """
        Initialize the object
        :param common_objs: common object dictionary
        :param db: name of the db
        :param table: name of the table in the db
        """
        super(AdvertiseRouteMgr, self).__init__(
            common_objs,
            [],
            db,
            table,
        )
        
        self.directory.subscribe([("CONFIG_DB", swsscommon.CFG_DEVICE_METADATA_TABLE_NAME, "localhost/bgp_asn"),], self.on_bgp_asn_change)
        self.advertised_routes = dict()


    OP_DELETE = 'DELETE'
    OP_ADD = 'ADD'


    def set_handler(self, key, data):
        vrf, ip_prefix = self.split_key(key)
        self.add_route_advertisement(vrf, ip_prefix)

        return True


    def del_handler(self, key):
        vrf, ip_prefix = self.split_key(key)
        self.remove_route_advertisement(vrf, ip_prefix)


    def add_route_advertisement(self, vrf, ip_prefix):
        if self.directory.path_exist("CONFIG_DB", swsscommon.CFG_DEVICE_METADATA_TABLE_NAME, "localhost/bgp_asn"):
            if not self.advertised_routes.get(vrf, set()):
                self.bgp_network_import_check_commands(vrf, self.OP_ADD)
            self.advertise_route_commands(ip_prefix, vrf, self.OP_ADD)

        self.advertised_routes.setdefault(vrf, set()).add(ip_prefix)


    def remove_route_advertisement(self, vrf, ip_prefix):
        self.advertised_routes.setdefault(vrf, set()).discard(ip_prefix)
        if not self.advertised_routes.get(vrf, set()):
            self.advertised_routes.pop(vrf, None)

        if self.directory.path_exist("CONFIG_DB", swsscommon.CFG_DEVICE_METADATA_TABLE_NAME, "localhost/bgp_asn"):
            if not self.advertised_routes.get(vrf, set()):
                self.bgp_network_import_check_commands(vrf, self.OP_DELETE)
            self.advertise_route_commands(ip_prefix, vrf, self.OP_DELETE)


    def advertise_route_commands(self, ip_prefix, vrf, op):
        is_ipv6 = TemplateFabric.is_ipv6(ip_prefix)
        bgp_asn = self.directory.get_slot("CONFIG_DB", swsscommon.CFG_DEVICE_METADATA_TABLE_NAME)["localhost"]["bgp_asn"]

        cmd_list = []
        if vrf == 'default':
            cmd_list.append("router bgp %s" % bgp_asn)
        else:
            cmd_list.append("router bgp %s vrf %s" % (bgp_asn, vrf))

        cmd_list.append(" address-family %s unicast" % ("ipv6" if is_ipv6 else "ipv4"))
        cmd_list.append("  %snetwork %s" % ('no ' if op == self.OP_DELETE else '', ip_prefix))

        self.cfg_mgr.push_list(cmd_list)


    def bgp_network_import_check_commands(self, vrf, op):
        bgp_asn = self.directory.get_slot("CONFIG_DB", swsscommon.CFG_DEVICE_METADATA_TABLE_NAME)["localhost"]["bgp_asn"]
        cmd_list = []
        if vrf == 'default':
            cmd_list.append("router bgp %s" % bgp_asn)
        else:
            cmd_list.append("router bgp %s vrf %s" % (bgp_asn, vrf))
        cmd_list.append(" %sbgp network import-check" % ('' if op == self.OP_DELETE else 'no '))

        self.cfg_mgr.push_list(cmd_list)


    def on_bgp_asn_change(self):
        if self.directory.path_exist("CONFIG_DB", swsscommon.CFG_DEVICE_METADATA_TABLE_NAME, "localhost/bgp_asn"):
            for vrf, ip_prefixes in self.advertised_routes.items():
                self.bgp_network_import_check_commands(vrf, self.OP_ADD)
                for ip_prefix in ip_prefixes:
                    self.add_route_advertisement(vrf, ip_prefix)


    @staticmethod
    def split_key(key):
        """
        Split key into vrf name and prefix.
        :param key: key to split
        :return: vrf name extracted from the key, ip prefix extracted from the key
        """
        if '|' not in key:
            return 'default', key
        else:
            return tuple(key.split('|', 1))
