from swsscommon import swsscommon
from sonic_py_common import daemon_base, multi_asic
from i2c_device_entity import I2CDeviceEntity
from i2c_isolation_list_updater import I2CIsolationListUpdater
import subprocess
import logging


platform_chassis = None
SELECT_TIMEOUT_MSECS = 1000
MAX_I2C_CHECK_COUNT = 3


def _wrapper_platform_api_importer():
    """
    Load new platform api class
    """
    global platform_chassis
    try:
        import sonic_platform.platform
        platform_chassis = sonic_platform.platform.Platform().get_chassis()
    except Exception as e:
        self.log_warning("Failed to load chassis due to {}".format(repr(e)))


def _wrapper_i2c_region_list():
    region_list_dict = {}
    if platform_chassis:
        try:
            rdict = platform_chassis.get_all_i2c_region_list()
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
        except:
            pass
    return region_list_dict


def _wrapper_reset_i2c_mux():
    if platform_chassis:
        try:
            platform_chassis.reset_i2c_mux()
        except:
            pass
    return

def _wrapper_i2c_bus_lock_status():
    """
    TODO: Call the real function here.
    """
    return False

def _wrapper_set_i2c_faulty_device(bus, device_addr, faulty):
    """
    bus: I2C bus id
    device_addr: I2C device address
    device_enabled: True if this is a faulty device else False
    """
    if platform_chassis:
        try:
            platform_chassis.set_i2c_faulty_device(bus, device_addr, faulty)
        except:
            pass
    return


def execute_os_cmd(cmd):
    try:
        ret = subprocess.check_output(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        # I2C function timeout return non-zero value, trigger CalledProcessError
        return False


class I2CDevicesScanner():
    """
    1. Allocate faulty I2C devices and record them to the isolation list
    2. Release the I2C devices from isolation list when they are removed
    """
    def __init__(self, logger):
        self.logger = logger
        _wrapper_platform_api_importer()
        self.device_locked_list_dict = {}
        self.i2c_region_list_dict = _wrapper_i2c_region_list()
        self.updater = I2CIsolationListUpdater()
        return

    def i2c_faulty_device_checker(self, entity):
        """
        Check whether the given I2C entity is a faulty device. If the bus becoms lock after
        accessing the entity, the entity is a fulty device.
        Params:
        : entity: I2C device entity
        Return: 
        : False if i2cget function return False in 3 times, otherwise True
        """
        is_faulty_device = False
        bus = entity.get_bus()
        device_addr = entity.get_device_addr()
        register_addr = entity.get_register_addr()
        cmd = "sudo i2cget -f -y {} {} {}".format(bus, device_addr, register_addr)

        """
        Issue the command to access the device in the isolated region. Will retry at most
        MAX_I2C_CHECK_COUNT times to do the best effort to reach the region.
        As long as the command is executed successfully, it is confirmed that the region
        is reached and then we can check whether the bus becomes locked to know whether
        the faulty device exists.
        """
        for _ in range(MAX_I2C_CHECK_COUNT):
            ret = execute_os_cmd(cmd)
            if ret == True:
              break

        if _wrapper_i2c_bus_lock_status() == True:
            is_faulty_device = True
            _wrapper_reset_i2c_mux() # reset i2c mux devices to recover the bus lock status

        return is_faulty_device

    def insert_i2c_region_to_isolation_list(self, i2c_region):
        """
        Insert the i2c region information to isolation list.
        Params:
        : i2c_region: I2C region ID
        """
        self.updater.add_device_into_isolation_list(i2c_region, self.i2c_region_list_dict[i2c_region])

    def remove_i2c_region_from_isolation_list(self, i2c_region):
        """
        Remove the i2c region information from isolation list.
        Params:
        : i2c_region: I2C region ID
        """
        self.updater.remove_device_from_isolation_list(i2c_region, self.i2c_region_list_dict[i2c_region])

    def subscribe_device_removal_event(self):
        """
        Subscribe to STATE_DB to get state tables changes
        """
        db_list = ['STATE_DB']
        device_tbl_map = ['TRANSCEIVER_INFO', "PSU_INFO", "FAN_INFO"]

        sel = swsscommon.Select()
        asic_context = {}
        namespaces = multi_asic.get_front_end_namespaces()
        for db_name in db_list:
            for tbl_name in device_tbl_map:
                for namespace in namespaces:
                    db = daemon_base.db_connect(db_name, namespace=namespace)
                    asic_id = multi_asic.get_asic_index_from_namespace(namespace)
                    device_tbl = swsscommon.SubscriberStateTable(db, tbl_name)
                    device_tbl.db_name = db_name
                    device_tbl.table_name = tbl_name
                    asic_context[device_tbl] = asic_id
                    sel.addSelectable(device_tbl)
        return sel, asic_context

    def handle_device_removal_event(self, sel, asic_context, stop_event):
        """
        Select device removal events, notify the observers upon a device removal in STATE_DB
        """
        device_locked_list = {v.get_name():[k,v] for k, v in self.device_locked_list_dict.items()}
        if not stop_event.is_set():
            (state, _) = sel.select(SELECT_TIMEOUT_MSECS)
            if state == swsscommon.Select.TIMEOUT:
                return
            if state != swsscommon.Select.OBJECT:
                self.logger.warning('sel.select() did not return swsscommon.Select.OBJECT')
                return

            for device_tbl in asic_context.keys():
                reset_devices = []
                while True:
                    (key, op, fvp) = device_tbl.pop()
                    if not key:
                        break
                    fvp = dict(fvp) if fvp is not None else {}
                    if op == swsscommon.SET_COMMAND:
                        if device_tbl.table_name in ['PSU_INFO', 'FAN_INFO']:
                            if key in device_locked_list:
                                if fvp["presence"].lower() == "false":
                                    if key not in reset_devices:
                                        reset_devices.append(key)
                    elif op == swsscommon.DEL_COMMAND:
                        if device_tbl.table_name == 'TRANSCEIVER_INFO':
                            if key in device_locked_list:
                                if key not in reset_devices:
                                    reset_devices.append(key)

                for key in reset_devices:
                    self.reset_i2c_device_state(device_locked_list[key])

    def reset_i2c_device_state(self, device):
        i2c_region = device[0]
        name = device[1].get_name()
        bus = device[1].get_bus()
        device_addr = device[1].get_device_addr()
        i2c_address_path = device[1].get_i2c_address_path()

        self.logger.info('Detect the removal of the device {}({}:{})'.format(name, i2c_region, i2c_address_path))
        del self.device_locked_list_dict[i2c_region]
        self.remove_i2c_region_from_isolation_list(i2c_region)
        _wrapper_set_i2c_faulty_device(bus, device_addr, False)
        self.logger.info("Remove {}({}:{}) from the isolation list.".format(name, i2c_region, i2c_address_path))

    def i2c_faulty_devices_scan(self):
        """
        Allocating which I2C device caused the I2C bus locked
        """
        self.logger.info("Start scanning for i2c faulty devices.")
        for i2c_region, i2c_devices in self.i2c_region_list_dict.items():
            if i2c_region in self.device_locked_list_dict:
                # skip checking the i2c region because it is known locked i2c region.
                continue

            for i2c_dev in i2c_devices:
                if self.i2c_faulty_device_checker(i2c_dev) == True:
                    # The i2c device causes the i2c bus locked. Record it to isolation list
                    self.insert_i2c_region_to_isolation_list(i2c_region)
                    self.device_locked_list_dict.setdefault(i2c_region, i2c_dev)
                    _wrapper_set_i2c_faulty_device(i2c_dev.get_bus(), i2c_dev.get_device_addr(), True)
                    self.logger.info("Isolate i2c devices: {}({}:{})".format(i2c_dev.get_name(), i2c_region, i2c_dev.get_i2c_address_path()))
                    break

        self.logger.info("Finish scanning for i2c faulty devices.The isolation list is updated.")
        return