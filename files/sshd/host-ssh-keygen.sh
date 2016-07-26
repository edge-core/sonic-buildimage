#!/bin/bash

[ -r /etc/ssh/ssh_host_key ] || {
    rm -f /etc/ssh/ssh_host_*_key*
    /usr/bin/ssh-keygen -t rsa -N '' -f /etc/ssh/ssh_host_rsa_key
    /usr/bin/ssh-keygen -t dsa -N '' -f /etc/ssh/ssh_host_dsa_key
    /usr/bin/ssh-keygen -t rsa1 -N '' -f /etc/ssh/ssh_host_key
    /usr/bin/ssh-keygen -t ecdsa -N '' -f /etc/ssh/ssh_host_ecdsa_key
    /usr/bin/ssh-keygen -t ed25519 -N '' -f /etc/ssh/ssh_host_ed25519_key
}
