import click
import utilities_common.cli as clicommon
import ipaddress

@click.group(cls=clicommon.AbbreviationGroup, name='dhcp_relay')
def vlan_dhcp_relay():
    pass

@vlan_dhcp_relay.command('add')
@click.argument('vid', metavar='<vid>', required=True, type=int)
@click.argument('dhcp_relay_destination_ips', nargs=-1, required=True)
@clicommon.pass_db
def add_vlan_dhcp_relay_destination(db, vid, dhcp_relay_destination_ips):
    """ Add a destination IP address to the VLAN's DHCP relay """

    ctx = click.get_current_context()
    added_servers = []

    # Verify vlan is valid
    vlan_name = 'Vlan{}'.format(vid)
    vlan = db.cfgdb.get_entry('VLAN', vlan_name)
    if len(vlan) == 0:
        ctx.fail("{} doesn't exist".format(vlan_name))

    # Verify all ip addresses are valid and not exist in DB
    dhcp_servers = vlan.get('dhcp_servers', [])
    dhcpv6_servers = vlan.get('dhcpv6_servers', [])

    for ip_addr in dhcp_relay_destination_ips:
        try:
            ipaddress.ip_address(ip_addr)
            if (ip_addr in dhcp_servers) or (ip_addr in dhcpv6_servers):
                    click.echo("{} is already a DHCP relay destination for {}".format(ip_addr, vlan_name))
                    continue
            if clicommon.ipaddress_type(ip_addr) == 4:
                dhcp_servers.append(ip_addr)
            else:
                dhcpv6_servers.append(ip_addr)
            added_servers.append(ip_addr)
        except Exception:
            ctx.fail('{} is invalid IP address'.format(ip_addr))

    # Append new dhcp servers to config DB
    if len(dhcp_servers):
        vlan['dhcp_servers'] = dhcp_servers
    if len(dhcpv6_servers):
        vlan['dhcpv6_servers'] = dhcpv6_servers

    db.cfgdb.set_entry('VLAN', vlan_name, vlan)

    if len(added_servers):
        click.echo("Added DHCP relay destination addresses {} to {}".format(added_servers, vlan_name))
        try:
            click.echo("Restarting DHCP relay service...")
            clicommon.run_command("systemctl stop dhcp_relay", display_cmd=False)
            clicommon.run_command("systemctl reset-failed dhcp_relay", display_cmd=False)
            clicommon.run_command("systemctl start dhcp_relay", display_cmd=False)
        except SystemExit as e:
            ctx.fail("Restart service dhcp_relay failed with error {}".format(e))

@vlan_dhcp_relay.command('del')
@click.argument('vid', metavar='<vid>', required=True, type=int)
@click.argument('dhcp_relay_destination_ips', nargs=-1, required=True)
@clicommon.pass_db
def del_vlan_dhcp_relay_destination(db, vid, dhcp_relay_destination_ips):
    """ Remove a destination IP address from the VLAN's DHCP relay """

    ctx = click.get_current_context()

    # Verify vlan is valid
    vlan_name = 'Vlan{}'.format(vid)
    vlan = db.cfgdb.get_entry('VLAN', vlan_name)
    if len(vlan) == 0:
        ctx.fail("{} doesn't exist".format(vlan_name))

    # Remove dhcp servers if they exist in the DB
    dhcp_servers = vlan.get('dhcp_servers', [])
    dhcpv6_servers = vlan.get('dhcpv6_servers', [])

    for ip_addr in dhcp_relay_destination_ips:
        if (ip_addr not in dhcp_servers) and (ip_addr not in dhcpv6_servers):
                ctx.fail("{} is not a DHCP relay destination for {}".format(ip_addr, vlan_name))
        if clicommon.ipaddress_type(ip_addr) == 4:
            dhcp_servers.remove(ip_addr)   
        else:
            dhcpv6_servers.remove(ip_addr)

    # Update dhcp servers to config DB
    if len(dhcp_servers):
        vlan['dhcp_servers'] = dhcp_servers
    else:
        if 'dhcp_servers' in vlan.keys():
            del vlan['dhcp_servers']

    if len(dhcpv6_servers):
        vlan['dhcpv6_servers'] = dhcpv6_servers
    else:
        if 'dhcpv6_servers' in vlan.keys():
            del vlan['dhcpv6_servers']

    db.cfgdb.set_entry('VLAN', vlan_name, vlan)
    click.echo("Removed DHCP relay destination addresses {} from {}".format(dhcp_relay_destination_ips, vlan_name))
    try:
        click.echo("Restarting DHCP relay service...")
        clicommon.run_command("systemctl stop dhcp_relay", display_cmd=False)
        clicommon.run_command("systemctl reset-failed dhcp_relay", display_cmd=False)
        clicommon.run_command("systemctl start dhcp_relay", display_cmd=False)
    except SystemExit as e:
        ctx.fail("Restart service dhcp_relay failed with error {}".format(e))


def register(cli):
    cli.commands['vlan'].add_command(vlan_dhcp_relay)


if __name__ == '__main__':
    vlan_dhcp_relay()
