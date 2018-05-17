from swsscommon import swsscommon
import time
import re
import json

def test_PortChannel(dvs):

    dvs.copy_file("/etc/teamd/", "teamd/files/po01.conf")
    dvs.runcmd("teamd -f /etc/teamd/po01.conf -d")
    dvs.runcmd("ifconfig PortChannel0001 up")

    time.sleep(1)

    # test lag table in app db
    appdb = swsscommon.DBConnector(0, dvs.redis_sock, 0)

    tbl = swsscommon.Table(appdb, "LAG_TABLE")

    (status, fvs) = tbl.get("PortChannel0001")

    assert status == True

    # test lag member table in app db
    tbl = swsscommon.Table(appdb, "LAG_MEMBER_TABLE")

    (status, fvs) = tbl.get("PortChannel0001:Ethernet112")

    assert status == True

    # test lag table in state db
    confdb = swsscommon.DBConnector(6, dvs.redis_sock, 0)

    tbl = swsscommon.Table(confdb, "LAG_TABLE")

    (status, fvs) = tbl.get("PortChannel0001")

    assert status == True
