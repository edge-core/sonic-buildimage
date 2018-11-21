HOWTO Use Virtual Switch (VM)

1. Install libvirt, kvm, qemu

```
sudo apt-get install libvirt-clients qemu-kvm libvirt-bin
```

2. Create SONiC VM

```
$ virsh
Welcome to virsh, the virtualization interactive terminal.

Type:  'help' for help with commands
       'quit' to quit

virsh # 
virsh # create sonic.xml
Domain sonic created from sonic.xml

virsh # 
```

2. Connect SONiC VM via console

```
$ telnet 127.0.0.1 7000
```

3. Connect SONiC VM via SSH

```
$ ssh -p 3040 admin@127.0.0.1
```
