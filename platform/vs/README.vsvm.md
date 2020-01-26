HOWTO Use Virtual Switch (VM)

1. Install libvirt, kvm, qemu

```
sudo apt-get install libvirt-clients qemu-kvm libvirt-bin
```

2. Create SONiC VM for single ASIC HWSKU

```
$ sudo virsh
Welcome to virsh, the virtualization interactive terminal.

Type:  'help' for help with commands
       'quit' to quit

virsh # 
virsh # create sonic.xml
Domain sonic created from sonic.xml

virsh # 
```

2. Create SONiC VM for multi-ASIC HWSKU
Update sonic_multiasic.xml with the external interfaces 
required for HWSKU.

```
$ sudo virsh
Welcome to virsh, the virtualization interactive terminal.

Type:  'help' for help with commands
       'quit' to quit

virsh #
virsh # create sonic_multiasic.xml 
Domain sonic created from sonic.xml

virsh #

Once booted up, create a file "asic.conf" with the content:
NUM_ASIC=<Number of asics>
under /usr/share/sonic/device/x86_64-kvm_x86_64-r0/
Also, create a "topology.sh" file which will simulate the internal
asic connectivity of the hardware under
/usr/share/sonic/device/x86_64-kvm_x86_64-r0/<HWSKU>
The HWSKU directory will have the required files like port_config.ini
for each ASIC.

Having done this, a new service "topology.service" will be started
during bootup which will invoke topology.sh script.

3. Access virtual switch:

    1. Connect SONiC VM via console
    ```
    $ telnet 127.0.0.1 7000
    ```
    
    OR

    2. Connect SONiC VM via SSH
        
        1. Connect via console (see 3.1 above)

        2. Request a new DHCP address
        ```
        sudo dhclient -v
        ```
        
        3. Connect via SSH
        ```
        $ ssh -p 3040 admin@127.0.0.1
        ```
