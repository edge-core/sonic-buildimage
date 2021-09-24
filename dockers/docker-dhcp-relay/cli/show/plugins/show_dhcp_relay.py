import click
from natsort import natsorted
from tabulate import tabulate
import show.vlan as vlan
import utilities_common.cli as clicommon

from swsscommon.swsscommon import ConfigDBConnector
from swsscommon.swsscommon import SonicV2Connector


# STATE_DB Table
DHCPv6_COUNTER_TABLE = 'DHCPv6_COUNTER_TABLE'

# DHCPv6 Counter Messages
messages = ["Solicit", "Advertise", "Request", "Confirm", "Renew", "Rebind", "Reply", "Release", "Decline", "Relay-Forward", "Relay-Reply"]

# DHCP_RELAY Config Table
DHCP_RELAY = 'DHCP_RELAY'
config_db = ConfigDBConnector()

def get_dhcp_helper_address(ctx, vlan):
    cfg, _ = ctx
    vlan_dhcp_helper_data, _, _ = cfg
    vlan_config = vlan_dhcp_helper_data.get(vlan)
    if not vlan_config:
        return ""

    dhcp_helpers = vlan_config.get('dhcp_servers', [])
    dhcpv6_helpers = vlan_config.get('dhcpv6_servers', [])

    return '\n'.join(natsorted(dhcp_helpers) + natsorted(dhcpv6_helpers))


vlan.VlanBrief.register_column('DHCP Helper Address', get_dhcp_helper_address)


class DHCPv6_Counter(object):
    def __init__(self):
        self.db = SonicV2Connector(use_unix_socket_path=False)
        self.db.connect(self.db.STATE_DB)
        self.table_name = DHCPv6_COUNTER_TABLE + self.db.get_db_separator(self.db.STATE_DB)


    def get_interface(self):
        """ Get all names of all interfaces in DHCPv6_COUNTER_TABLE """
        vlans = []
        for key in self.db.keys(self.db.STATE_DB):
            if DHCPv6_COUNTER_TABLE in key:
                vlans.append(key[21:])
        return vlans
        

    def get_dhcp6relay_msg_count(self, interface, msg):
        """ Get count of a dhcp6relay message """
        count = self.db.get(self.db.STATE_DB, self.table_name + str(interface), str(msg))
        data = [str(msg), count]
        return data

    
    def clear_table(self, interface):
        """ Reset all message counts to 0 """
        for msg in messages:
            self.db.set(self.db.STATE_DB, self.table_name + str(interface), str(msg), '0') 

def print_count(counter, intf):
    """Print count of each message"""
    data = []
    for i in messages:
        data.append(counter.get_dhcp6relay_msg_count(intf, i))
    print(tabulate(data, headers = ["Message Type", intf], tablefmt='simple', stralign='right') + "\n")


#
# 'dhcp6relay_counters' group ###
#


@click.group(cls=clicommon.AliasedGroup, name="dhcp6relay_counters")
def dhcp6relay_counters():
    """Show DHCPv6 counter"""
    pass


# 'counts' subcommand ("show dhcp6relay_counters counts")
@dhcp6relay_counters.command('counts')
@click.option('-i', '--interface', required=False)
@click.option('--verbose', is_flag=True, help="Enable verbose output")
def counts(interface, verbose):
    """Show dhcp6relay message counts"""

    counter = DHCPv6_Counter()
    counter_intf = counter.get_interface()

    if interface:
        print_count(counter, interface)
    else:
        for intf in counter_intf:
                print_count(counter, intf)



@click.group(cls=clicommon.AliasedGroup, name="dhcprelay_helper")
def dhcp_relay_helper():
    """Show DHCP_Relay helper information"""
    pass

@dhcp_relay_helper.command('ipv6')
def get_dhcpv6_helper_address():
    """Parse through DHCP_RELAY table for each interface in config_db.json and print dhcpv6 helpers in table format"""
    if config_db is not None:
        config_db.connect()
        table_data = config_db.get_table(DHCP_RELAY)
        if table_data is not None:
            vlans = config_db.get_keys(DHCP_RELAY)
            for vlan in vlans: 
                output = get_data(table_data, vlan)
                print(output)
            

def get_data(table_data, vlan):
    vlan_data = table_data.get(vlan)
    helpers_data = vlan_data.get('dhcpv6_servers')
    if helpers_data is not None:
        addr = {vlan:[]}
        for ip in helpers_data:
            addr[vlan].append(ip)
    output = tabulate({'Interface':[vlan], vlan:addr.get(vlan)}, tablefmt='simple', stralign='right') + '\n'
    return output

def register(cli):
    cli.add_command(dhcp6relay_counters)
    cli.add_command(dhcp_relay_helper)
