import click
import utilities_common.cli as clicommon

@click.group(cls=clicommon.AbbreviationGroup, name='dhcp_relay')
def vlan_dhcp_relay():
    pass

@vlan_dhcp_relay.command('add')
@click.argument('vid', metavar='<vid>', required=True, type=int)
@click.argument('dhcp_relay_destination_ip', metavar='<dhcp_relay_destination_ip>', required=True)
@clicommon.pass_db
def add_vlan_dhcp_relay_destination(db, vid, dhcp_relay_destination_ip):
    """ Add a destination IP address to the VLAN's DHCP relay """

    ctx = click.get_current_context()

    if not clicommon.is_ipaddress(dhcp_relay_destination_ip):
        ctx.fail('{} is invalid IP address'.format(dhcp_relay_destination_ip))

    vlan_name = 'Vlan{}'.format(vid)
    vlan = db.cfgdb.get_entry('VLAN', vlan_name)
    if len(vlan) == 0:
        ctx.fail("{} doesn't exist".format(vlan_name))

    dhcp_relay_dests = vlan.get('dhcp_servers', [])
    if dhcp_relay_destination_ip in dhcp_relay_dests:
        click.echo("{} is already a DHCP relay destination for {}".format(dhcp_relay_destination_ip, vlan_name))
        return

    dhcp_relay_dests.append(dhcp_relay_destination_ip)
    vlan['dhcp_servers'] = dhcp_relay_dests
    db.cfgdb.set_entry('VLAN', vlan_name, vlan)
    click.echo("Added DHCP relay destination address {} to {}".format(dhcp_relay_destination_ip, vlan_name))
    try:
        click.echo("Restarting DHCP relay service...")
        clicommon.run_command("systemctl stop dhcp_relay", display_cmd=False)
        clicommon.run_command("systemctl reset-failed dhcp_relay", display_cmd=False)
        clicommon.run_command("systemctl start dhcp_relay", display_cmd=False)
    except SystemExit as e:
        ctx.fail("Restart service dhcp_relay failed with error {}".format(e))

@vlan_dhcp_relay.command('del')
@click.argument('vid', metavar='<vid>', required=True, type=int)
@click.argument('dhcp_relay_destination_ip', metavar='<dhcp_relay_destination_ip>', required=True)
@clicommon.pass_db
def del_vlan_dhcp_relay_destination(db, vid, dhcp_relay_destination_ip):
    """ Remove a destination IP address from the VLAN's DHCP relay """

    ctx = click.get_current_context()

    if not clicommon.is_ipaddress(dhcp_relay_destination_ip):
        ctx.fail('{} is invalid IP address'.format(dhcp_relay_destination_ip))

    vlan_name = 'Vlan{}'.format(vid)
    vlan = db.cfgdb.get_entry('VLAN', vlan_name)
    if len(vlan) == 0:
        ctx.fail("{} doesn't exist".format(vlan_name))

    dhcp_relay_dests = vlan.get('dhcp_servers', [])
    if not dhcp_relay_destination_ip in dhcp_relay_dests:
        ctx.fail("{} is not a DHCP relay destination for {}".format(dhcp_relay_destination_ip, vlan_name))

    dhcp_relay_dests.remove(dhcp_relay_destination_ip)
    if len(dhcp_relay_dests) == 0:
        del vlan['dhcp_servers']
    else:
        vlan['dhcp_servers'] = dhcp_relay_dests
    db.cfgdb.set_entry('VLAN', vlan_name, vlan)
    click.echo("Removed DHCP relay destination address {} from {}".format(dhcp_relay_destination_ip, vlan_name))
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
