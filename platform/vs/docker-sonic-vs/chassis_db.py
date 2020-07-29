#!/usr/bin/env python

import swsssdk
import json
chassisdb = swsssdk.SonicV2Connector(host='10.0.0.200', port='6380')
chassisdb.connect(chassisdb.CHASSIS_DB)
fname='/usr/share/sonic/virtual_chassis/chassis_db.json'
with open(fname) as f:
   js = json.load(f)
   client=chassisdb.get_redis_client(chassisdb.CHASSIS_DB)
   for h, table in js.items():
      for k, v in table.items():
         client.hset(h, k, v)
