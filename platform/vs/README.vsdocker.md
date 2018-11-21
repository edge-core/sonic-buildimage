HOWTO Use Virtual Switch (Docker)


1. Create a docker with 32 front panel port

```
$ docker run -id --name sw debian bash
$ sudo ./create_vnet.sh sw
$ ip netns list
sw-srv31 (id: 37)
sw-srv30 (id: 35)
sw-srv29 (id: 34)
sw-srv28 (id: 33)
sw-srv27 (id: 32)
sw-srv26 (id: 31)
sw-srv25 (id: 30)
sw-srv24 (id: 29)
sw-srv23 (id: 28)
sw-srv22 (id: 27)
sw-srv21 (id: 26)
sw-srv20 (id: 25)
sw-srv19 (id: 24)
sw-srv18 (id: 23)
sw-srv17 (id: 22)
sw-srv16 (id: 21)
sw-srv15 (id: 20)
sw-srv14 (id: 19)
sw-srv13 (id: 18)
sw-srv12 (id: 17)
sw-srv11 (id: 16)
sw-srv10 (id: 15)
sw-srv9 (id: 14)
sw-srv8 (id: 13)
sw-srv7 (id: 12)
sw-srv6 (id: 11)
sw-srv5 (id: 10)
sw-srv4 (id: 9)
sw-srv3 (id: 8)
sw-srv2 (id: 7)
sw-srv1 (id: 6)
sw-srv0 (id: 5)
```

2. Start sonic virtual switch docker

```
$ docker run --privileged --network container:sw --name vs -d docker-sonic-vs
```

3. Setup IP in the virtual switch docker

```
$ docker exec -it vs bash
root@2e9b5c2dc2a2:/# ifconfig Ethernet0 10.0.0.0/31 up
root@2e9b5c2dc2a2:/# ifconfig Ethernet4 10.0.0.2/31 up
```

4. Setup IP in the server network namespace

```
$ sudo ip netns exec sw-srv0 ifconfig eth0 10.0.0.1/31
$ sudo ip netns exec sw-srv0 ip route add default via 10.0.0.0
$ sudo ip netns exec sw-srv1 ifconfig eth0 10.0.0.3/31
$ sudo ip netns exec sw-srv1 ip route add default via 10.0.0.2
```

5. Ping from sw-srv0 to sw-srv1

```
$ sudo ip netns exec sw-srv0 ping  10.0.0.3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=63 time=0.137 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=63 time=0.148 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=63 time=0.149 ms
```
