#!/usr/bin/env python3

import argparse
import pexpect
import sys
import time


def main():

    parser = argparse.ArgumentParser(description='test_login cmdline parser')
    parser.add_argument('-u', default="admin", help='login user name')
    parser.add_argument('-P', default="YourPaSsWoRd", help='login password')
    parser.add_argument('-p', type=int, default=9000, help='local port')

    args = parser.parse_args()

    login_prompt = 'sonic login:'
    passwd_prompt = 'Password:'
    cmd_prompt = "{}@sonic:~\$ $".format(args.u)
    grub_selection = "The highlighted entry will be executed"
    firsttime_prompt = 'firsttime_exit'

    i = 0
    while True:
        try:
            p = pexpect.spawn("telnet 127.0.0.1 {}".format(args.p), timeout=600, logfile=sys.stdout, encoding='utf-8')
            break
        except Exception as e:
            print(str(e))
            i += 1
            if i == 10:
                raise
            time.sleep(1)

    # select default SONiC Image
    p.expect(grub_selection)
    p.sendline()

    # bootup sonic image
    while True:
        i = p.expect([login_prompt, passwd_prompt, firsttime_prompt, cmd_prompt])
        if i == 0:
            # send user name
            p.sendline(args.u)
        elif i == 1:
            # send password
            p.sendline(args.P)
        elif i == 2:
            # fix a login timeout issue, caused by the login_prompt message mixed with the output message of the rc.local
            time.sleep(1)
            p.sendline()
        else:
            break

    # check version
    time.sleep(5)
    p.sendline('uptime')
    p.expect([cmd_prompt])
    p.sendline('show version')
    p.expect([cmd_prompt])
    p.sendline('show ip bgp sum')
    p.expect([cmd_prompt])
    p.sendline('sync')
    p.expect([cmd_prompt])


if __name__ == '__main__':
    main()
