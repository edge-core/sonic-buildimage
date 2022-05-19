from .manager import Manager
from .log import log_err, log_debug

ROUTE_MAPS = ["FROM_SDN_SLB_ROUTES"]


class RouteMapMgr(Manager):
    """This class add route-map when BGP_PROFILE_TABLE in APPL_DB is updated"""

    def __init__(self, common_objs, db, table):
        """
        Initialize the object
        :param common_objs: common object dictionary
        :param db: name of the db
        :param table: name of the table in the db
        """
        super(RouteMapMgr, self).__init__(
            common_objs,
            [],
            db,
            table,
        )

    def set_handler(self, key, data):
        log_debug("BGPRouteMapMgr:: set handler")
        """Only need a name as the key, and community id as the data"""
        if not self.__set_handler_validate(key, data):
            return True

        self.__update_rm(key, data)
        return True

    def del_handler(self, key):
        log_debug("BGPRouteMapMgr:: del handler")
        if not self.__del_handler_validate(key):
            return
        self.__remove_rm(key)

    def __remove_rm(self, rm):
        cmds = ["no route-map %s permit 100" % ("%s_RM" % rm)]
        log_debug("BGPRouteMapMgr:: remove route-map %s" % ("%s_RM" % rm))
        self.cfg_mgr.push_list(cmds)
        log_debug("BGPRouteMapMgr::Done")

    def __set_handler_validate(self, key, data):
        if key not in ROUTE_MAPS:
            log_err("BGPRouteMapMgr:: Invalid key for route-map %s" % key)
            return False

        if not data:
            log_err("BGPRouteMapMgr:: data is None")
            return False
        community_ids = data["community_id"].split(":")
        try:
            if (
                len(community_ids) != 2
                or int(community_ids[0]) not in range(0, 65536)
                or int(community_ids[1]) not in range(0, 65536)
            ):
                log_err("BGPRouteMapMgr:: data %s doesn't include valid community id %s" % (data, community_ids))
                return False
        except ValueError:
            log_err("BGPRouteMapMgr:: data %s includes illegal input" % (data))
            return False

        return True

    def __del_handler_validate(self, key):
        if key not in ROUTE_MAPS:
            log_err("BGPRouteMapMgr:: Invalid key for route-map %s" % key)
            return False
        return True

    def __update_rm(self, rm, data):
        cmds = ["route-map %s permit 100" % ("%s_RM" % rm), " set community %s" % data["community_id"]]
        log_debug("BGPRouteMapMgr:: update route-map %s community %s" % ("%s_RM" % rm, data["community_id"]))
        self.cfg_mgr.push_list(cmds)
        log_debug("BGPRouteMapMgr::Done")
