import traceback
from .log import log_crit, log_err, log_debug
from .manager import Manager
from .template import TemplateFabric
import socket

class StaticRouteMgr(Manager):
    """ This class updates static routes when STATIC_ROUTE table is updated """
    def __init__(self, common_objs, db, table):
        """
        Initialize the object
        :param common_objs: common object dictionary
        :param db: name of the db
        :param table: name of the table in the db
        """
        super(StaticRouteMgr, self).__init__(
            common_objs,
            [],
            db,
            table,
        )

        self.static_routes = {}

    OP_DELETE = 'DELETE'
    OP_ADD = 'ADD'

    def set_handler(self, key, data):
        vrf, ip_prefix = self.split_key(key)
        is_ipv6 = TemplateFabric.is_ipv6(ip_prefix)

        arg_list    = lambda v: v.split(',') if len(v.strip()) != 0 else None
        bkh_list    = arg_list(data['blackhole']) if 'blackhole' in data else None
        nh_list     = arg_list(data['nexthop']) if 'nexthop' in data else None
        intf_list   = arg_list(data['ifname']) if 'ifname' in data else None
        dist_list   = arg_list(data['distance']) if 'distance' in data else None
        nh_vrf_list = arg_list(data['nexthop-vrf']) if 'nexthop-vrf' in data else None

        try:
            ip_nh_set = IpNextHopSet(is_ipv6, bkh_list, nh_list, intf_list, dist_list, nh_vrf_list)
            cur_nh_set = self.static_routes.get(vrf, {}).get(ip_prefix, IpNextHopSet(is_ipv6))
            cmd_list = self.static_route_commands(ip_nh_set, cur_nh_set, ip_prefix, vrf)
        except Exception as exc:
            log_crit("Got an exception %s: Traceback: %s" % (str(exc), traceback.format_exc()))
            return False

        if cmd_list:
            self.cfg_mgr.push_list(cmd_list)
            log_debug("Static route {} is scheduled for updates".format(key))
        else:
            log_debug("Nothing to update for static route {}".format(key))

        self.static_routes.setdefault(vrf, {})[ip_prefix] = ip_nh_set

        return True


    def del_handler(self, key):
        vrf, ip_prefix = self.split_key(key)
        is_ipv6 = TemplateFabric.is_ipv6(ip_prefix)

        ip_nh_set = IpNextHopSet(is_ipv6)
        cur_nh_set = self.static_routes.get(vrf, {}).get(ip_prefix, IpNextHopSet(is_ipv6))
        cmd_list = self.static_route_commands(ip_nh_set, cur_nh_set, ip_prefix, vrf)

        if cmd_list:
            self.cfg_mgr.push_list(cmd_list)
            log_debug("Static route {} is scheduled for updates".format(key))
        else:
            log_debug("Nothing to update for static route {}".format(key))

        self.static_routes.setdefault(vrf, {}).pop(ip_prefix, None)

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

    def static_route_commands(self, ip_nh_set, cur_nh_set, ip_prefix, vrf):
        diff_set = ip_nh_set.symmetric_difference(cur_nh_set)

        op_cmd_list = {}
        for ip_nh in diff_set:
            if ip_nh in cur_nh_set:
                op = self.OP_DELETE
            else:
                op = self.OP_ADD

            op_cmds = op_cmd_list.setdefault(op, [])
            op_cmds.append(self.generate_command(op, ip_nh, ip_prefix, vrf))

        cmd_list = op_cmd_list.get(self.OP_DELETE, [])
        cmd_list += op_cmd_list.get(self.OP_ADD, [])

        return cmd_list

    def generate_command(self, op, ip_nh, ip_prefix, vrf):
        return '{}{} route {}{}{}'.format(
            'no ' if op == self.OP_DELETE else '',
            'ipv6' if ip_nh.af == socket.AF_INET6 else 'ip',
            ip_prefix,
            ip_nh,
            ' vrf {}'.format(vrf) if vrf != 'default' else ''
        )

class IpNextHop:
    def __init__(self, af_id, blackhole, dst_ip, if_name, dist, vrf):
        zero_ip = lambda af: '0.0.0.0' if af == socket.AF_INET else '::'
        self.af = af_id
        self.blackhole = 'false' if blackhole is None or blackhole == '' else blackhole
        self.distance = 0 if dist is None else int(dist)
        if self.blackhole == 'true':
            dst_ip = if_name = vrf = None
        self.ip = zero_ip(af_id) if dst_ip is None or dst_ip == '' else dst_ip
        self.interface = '' if if_name is None else if_name
        self.nh_vrf = '' if vrf is None else vrf
        if self.blackhole != 'true' and self.is_zero_ip() and len(self.interface.strip()) == 0:
            log_err('Mandatory attribute not found for nexthop')
            raise ValueError
    def __eq__(self, other):
        return (self.af == other.af and self.blackhole == other.blackhole and
                self.ip == other.ip and self.interface == other.interface and
                self.distance == other.distance and self.nh_vrf == other.nh_vrf)
    def __ne__(self, other):
        return (self.af != other.af or self.blackhole != other.blackhole or
                self.ip != other.ip or self.interface != other.interface or
                self.distance != other.distance or self.nh_vrf != other.nh_vrf)
    def __hash__(self):
        return hash((self.af, self.blackhole, self.ip, self.interface, self.distance, self.nh_vrf))
    def is_zero_ip(self):
        return sum([x for x in socket.inet_pton(self.af, self.ip)]) == 0
    def __format__(self, format):
        ret_val = ''
        if self.blackhole == 'true':
            ret_val += ' blackhole'
        if not (self.ip is None or self.is_zero_ip()):
            ret_val += ' %s' % self.ip
        if not (self.interface is None or self.interface == ''):
            ret_val += ' %s' % self.interface
        if not (self.distance is None or self.distance == 0):
            ret_val += ' %d' % self.distance
        if not (self.nh_vrf is None or self.nh_vrf == ''):
            ret_val += ' nexthop-vrf %s' % self.nh_vrf
        return ret_val

class IpNextHopSet(set):
    def __init__(self, is_ipv6, bkh_list = None, ip_list = None, intf_list = None, dist_list = None, vrf_list = None):
        super(IpNextHopSet, self).__init__()
        af = socket.AF_INET6 if is_ipv6 else socket.AF_INET
        if bkh_list is None and ip_list is None and intf_list is None:
            # empty set, for delete case
            return
        nums = {len(x) for x in [bkh_list, ip_list, intf_list, dist_list, vrf_list] if x is not None}
        if len(nums) != 1:
            log_err("Lists of next-hop attribute have different sizes: %s" % nums)
            for x in [bkh_list, ip_list, intf_list, dist_list, vrf_list]:
                log_debug("List: %s" % x)
            raise ValueError
        nh_cnt = nums.pop()
        item = lambda lst, i: lst[i] if lst is not None else None
        for idx in range(nh_cnt):
            try:
                self.add(IpNextHop(af, item(bkh_list, idx), item(ip_list, idx), item(intf_list, idx),
                                   item(dist_list, idx), item(vrf_list, idx), ))
            except ValueError:
                continue
