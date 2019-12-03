#!/usr/bin/env python

import pexpect
import argparse
import sys
import time

def main():

    parser = argparse.ArgumentParser(description='test_login cmdline parser')
    parser.add_argument('-u', default="admin", help='login user name')
    parser.add_argument('-P', default="YourPaSsWoRd", help='login password')
    parser.add_argument('-p', type=int, default=9000, help='local port')

    args = parser.parse_args()

    KEY_UP = '\x1b[A'
    KEY_DOWN = '\x1b[B'
    KEY_RIGHT = '\x1b[C'
    KEY_LEFT = '\x1b[D'

    login_prompt = 'sonic login:'
    passwd_prompt = 'Password:'
    cmd_prompt = "%s@sonic:~\$ $" % args.u
    grub_selection = "The highlighted entry will be executed"

    i = 0
    while True:
        try:
            p = pexpect.spawn("telnet 127.0.0.1 %s" % args.p, timeout=600, logfile=sys.stdout)
            break
        except Exception as e:
            print str(e)
            i += 1
            if i == 10:
                raise
            time.sleep(1)

    # select ONIE embed
    p.expect(grub_selection)
    p.sendline(KEY_DOWN)

    # install sonic image
    while True:
        i = p.expect([login_prompt, passwd_prompt, grub_selection, cmd_prompt])
        if i == 0:
            # send user name
            p.sendline(args.u)
        elif i == 1:
            # send password
            p.sendline(args.P)
        elif i == 2:
            # select onie install
            p.sendline()
        else:
            break

    # check version
    time.sleep(5)
    p.sendline('show version')
    p.expect([cmd_prompt])
    p.sendline('show ip bgp sum')
    p.expect([cmd_prompt])
    p.sendline('sync')
    p.expect([cmd_prompt])

if __name__ == '__main__':
    main()
