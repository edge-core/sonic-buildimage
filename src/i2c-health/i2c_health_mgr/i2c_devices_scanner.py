from swsscommon import swsscommon
from sonic_py_common import daemon_base, multi_asic
from i2c_health_mgr.i2c_device_entity import I2CDeviceEntity
from i2c_health_mgr import i2c_isolation_list_updater
from i2c_health_mgr.i2c_health_msgs import get_i2c_health_msg
import subprocess
import re

SELECT_TIMEOUT_MSECS = 1000
MAX_I2C_CHECK_COUNT = 3
MAX_FLUSH_STATUS_RECORDS_COUNTER = 10
STATE_DB = 'STATE_DB'
SUBSCRIBE_DEVICE_TABLES = ['TRANSCEIVER_STATUS']
QUERY_DEVICE_TABLES = ["PSU_INFO", "FAN_INFO"]


def execute_os_cmd(cmd):
    try:
        ret = subprocess.check_output(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        # I2C function timeout return non-zero value, trigger CalledProcessError
        return False


class I2CDevicesScanner:
    """
    1. Allocate faulty I2C devices and record them to the isolation list
    2. Release the I2C devices from isolation list when they are removed
    """
    def __init__(self, logger, i2c_bus_checker, i2c_platform_api):
        self.logger = logger
        self.platform_api = i2c_platform_api
        self.updater = i2c_isolation_list_updater.I2CIsolationListUpdater(logger)

        self.device_locked_list = []
        self.i2c_region_list_dict = self.get_all_i2c_region_list()
        self.i2c_bus_checker = i2c_bus_checker

        self.state_db_connector = {}
        self.sel = None
        self.asic_context = {}
        self.cached_data = {}
        return

    def reset_psu_name(self, psu_db_name):
        """
        The PSU name in the PSU_INFO table is differ with the platform API.
        Rename the received PSU name from the STATE_DB update message to match
        the name in the platform API.
        """
        return "PSU-{}".format(re.split(r'[\s-]+', psu_db_name)[1])

    def get_all_i2c_region_list(self):
        rdict = self.platform_api.get_all_i2c_region_list()
        if rdict == None:
            return {}

        region_list_dict = {}
        for region_id, i2c_devices in rdict.items():
            region_list_dict.setdefault(region_id, [])
            for i2v_dev in i2c_devices:
                region_list_dict[region_id].append(
                    I2CDeviceEntity(
                        i2v_dev['name'],
                        i2v_dev['bus'],
                        i2v_dev['device_addr'],
                        i2v_dev['register_addr']
                    )
                )
        return region_list_dict

    def i2c_faulty_device_checker(self, entity):
        """
        Check whether the given I2C entity is a faulty device. If the bus becoms lock after
        accessing the entity, the entity is a faulty device.
        Params:
        : entity: I2C device entity
        Return:
        : True if the given entity is a faulty device
        """
        is_faulty_device = False
        bus = entity.get_bus()
        device_addr = entity.get_device_addr()
        register_addr = entity.get_register_addr()
        cmd = "sudo i2cget -f -y {} {} {}".format(bus, device_addr, register_addr)

        """
        Issue the command to access the device in the isolated region.
        To make the best effort to reach the region, retry at most MAX_I2C_CHECK_COUNT times.
        As long as the command is executed successfully, it is confirmed that the region is reached.
        Otherwise, the device may be a faulty device, or the device is absent.
        We can check whether the bus becomes locked to determine whether the faulty device exists.
        """
        for _ in range(MAX_I2C_CHECK_COUNT):
            ret = execute_os_cmd(cmd)
            if ret == True:
              break

        if ret == False and self.i2c_bus_checker.is_bus_lock():
            is_faulty_device = True
            self.platform_api.reset_all_mux() # reset i2c mux devices to recover the bus lock status

        return is_faulty_device

    def insert_i2c_region_to_isolation_list(self, i2c_region):
        """
        Insert the i2c region information to isolation list.
        Params:
        : i2c_region: I2C region ID
        """
        msg = get_i2c_health_msg(3) # 003: device name, region id, device addr.
        for entity in self.i2c_region_list_dict[i2c_region]:
            self.logger.log_notice(msg.format(entity.get_name(), i2c_region, entity.get_i2c_address_path()))

        self.updater.add_device_into_isolation_list(i2c_region, self.i2c_region_list_dict[i2c_region])

    def remove_i2c_region_from_isolation_list(self, i2c_region):
        """
        Remove the i2c region information from isolation list.
        Params:
        : i2c_region: I2C region ID
        """
        msg = get_i2c_health_msg(4) # 004: device name, region id, device addr.
        for entity in self.i2c_region_list_dict[i2c_region]:
            self.logger.log_notice(msg.format(entity.get_name(), i2c_region, entity.get_i2c_address_path()))

        self.updater.remove_device_from_isolation_list(i2c_region, self.i2c_region_list_dict[i2c_region])

    def reset_i2c_region(self, region_id):
        self.device_locked_list.remove(region_id)
        self.remove_i2c_region_from_isolation_list(region_id)
        for faulty_device in self.i2c_region_list_dict[region_id]:
            self.platform_api.set_i2c_faulty_device(faulty_device.get_bus(), faulty_device.get_device_addr(), False)

    def subscribe_device_removal_event(self):
        """
        Subscribe to STATE_DB to get state tables changes
        """
        self.sel = swsscommon.Select()
        for namespace in multi_asic.get_front_end_namespaces():
            asic_id = multi_asic.get_asic_index_from_namespace(namespace)
            db = daemon_base.db_connect(STATE_DB, namespace=namespace)
            self.state_db_connector.setdefault(asic_id, db)
            for tbl_name in SUBSCRIBE_DEVICE_TABLES:
                device_tbl = swsscommon.SubscriberStateTable(db, tbl_name)
                device_tbl.db_name = STATE_DB
                device_tbl.table_name = tbl_name
                self.asic_context[device_tbl] = asic_id
                self.sel.addSelectable(device_tbl)
        return

    def handle_device_removal_event(self, stop_event, interval):
        """
        Select device removal events, notify the observers upon a device removed in STATE_DB
        """
        device_locked_list = {}
        for region_id in self.device_locked_list:
            for i2c_dev in self.i2c_region_list_dict[region_id]:
                device_locked_list.setdefault(i2c_dev.get_name(), region_id)

        if not stop_event.is_set():
            reset_regions = []
            # Get the transceivers' present state from STATE_DB
            (state, _) = self.sel.select(interval * SELECT_TIMEOUT_MSECS)
            if state == swsscommon.Select.OBJECT:
                for device_tbl in self.asic_context.keys():
                    while True:
                        (key, op, fvp) = device_tbl.pop()
                        if not key:
                            break
                        fvp = dict(fvp) if fvp is not None else {}
                        if op == swsscommon.SET_COMMAND:
                            if key in device_locked_list:
                                region_id = device_locked_list[key]
                                if region_id not in reset_regions:
                                    reset_regions.append(region_id)

            # Actively query the PSU/FAN present state from STATE_DB
            for table_name in QUERY_DEVICE_TABLES:
                for asic_id, db in self.state_db_connector.items():
                    table = swsscommon.Table(db, table_name)
                    for key in table.getKeys():
                        ret, fvp = table.get(key)
                        if ret:
                            fvp = dict(fvp)
                            if table_name == "PSU_INFO":
                                key = self.reset_psu_name(key)
                            if key in device_locked_list:
                                if fvp['presence'].lower() == "false":
                                    region_id = device_locked_list[key]
                                    if region_id not in reset_regions:
                                        reset_regions.append(region_id)

            for region_id in reset_regions:
                self.reset_i2c_region(region_id)

    def cache_state_db_records(self):
        """
        Backup the STATE_DB tables in the list SUBSCRIBE_DEVICE_TABLES
        """
        for table_name in SUBSCRIBE_DEVICE_TABLES:
            self.cached_data.setdefault(table_name, {})
            for asic_id, db in self.state_db_connector.items():
                self.cached_data[table_name].setdefault(asic_id, {})
                table = swsscommon.Table(db, table_name)
                for key in table.getKeys():
                    self.cached_data[table_name][asic_id].setdefault(key, table.get(key)[1])
        return

    def restore_state_db_records(self, stop_event):
        """
        Restoring the STATE_DB tables in the list SUBSCRIBE_DEVICE_TABLES
        """
        for table_name, per_asic_id_data in self.cached_data.items():
            for asic_id, data in per_asic_id_data.items():
                table = swsscommon.Table(self.state_db_connector[asic_id], table_name)
                for key, records in data.items():
                    table.set(key, records)

        """ Flush the restored DB update records """
        flush_status_records_counter = MAX_FLUSH_STATUS_RECORDS_COUNTER
        while self.cached_data and flush_status_records_counter > 0:
            flush_status_records_counter -= 1
            if not stop_event.is_set():
                (state, _) = self.sel.select(SELECT_TIMEOUT_MSECS)
                if state == swsscommon.Select.TIMEOUT:
                    continue
                if state != swsscommon.Select.OBJECT:
                    continue
                for device_tbl in self.asic_context.keys():
                    while True:
                        (key, op, fvp) = device_tbl.pop()
                        if not key:
                            break
                        if op == swsscommon.SET_COMMAND:
                            asic_id = self.asic_context[device_tbl]
                            if device_tbl.table_name in self.cached_data and asic_id in self.cached_data[device_tbl.table_name]:
                                if key in self.cached_data[device_tbl.table_name][asic_id]:
                                    del self.cached_data[device_tbl.table_name][asic_id][key]
                                if not self.cached_data[device_tbl.table_name][asic_id]:
                                    del self.cached_data[device_tbl.table_name][asic_id]
                                if not self.cached_data[device_tbl.table_name]:
                                    del self.cached_data[device_tbl.table_name]

        if self.cached_data:
            """ Clear the cached STATE_DB records if the cached_data is not empty. """
            msg = get_i2c_health_msg(25)
            self.logger.log_warning(msg)
            msg = get_i2c_health_msg(26)
            unfinish_restore_devices = []
            for tbl in self.cached_data:
                for asic_id in self.cached_data[tbl]:
                    for device in self.cached_data[tbl][asic_id].keys():
                        unfinish_restore_devices.append(device)
            self.logger.log_notice(msg.format(str(unfinish_restore_devices)))
            self.cached_data = {}

        return

    def i2c_faulty_devices_scan(self):
        """
        Allocating which I2C device caused the I2C bus locked
        """
        for i2c_region, i2c_devices in self.i2c_region_list_dict.items():
            if i2c_region in self.device_locked_list:
                # skip checking the i2c region because it is known locked i2c region.
                continue

            if self.i2c_faulty_device_checker(i2c_devices[0]) == True:
                # The i2c device causes the i2c bus locked. Record it to isolation list
                self.insert_i2c_region_to_isolation_list(i2c_region)
                self.device_locked_list.append(i2c_region)
                for faulty_device in i2c_devices:
                    self.platform_api.set_i2c_faulty_device(faulty_device.get_bus(), faulty_device.get_device_addr(), True)
        return


