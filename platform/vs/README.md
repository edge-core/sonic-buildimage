HOWTO Use Virtual Switch


1. Create a docker with 32 front panel port

```
docker run -id --name sw debian bash
sudo ./create_vnet.sh sw
```

2. Create sonic virtual switch docker

```
docker run --privileged --network container:sw -d docker-sonic-vs
```

3. Run test in virtual switch docker (TBD)
