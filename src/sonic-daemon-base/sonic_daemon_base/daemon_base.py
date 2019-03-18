#!/usr/bin/env python2

try:
    import imp
    import signal
    import subprocess
    import sys
    import syslog
    from swsscommon import swsscommon
except ImportError, e:
    raise ImportError (str(e) + " - required module not found")

#============================= Constants =============================

# Platform root directory inside docker
PLATFORM_ROOT_DOCKER = "/usr/share/sonic/platform"
SONIC_CFGGEN_PATH = '/usr/local/bin/sonic-cfggen'
HWSKU_KEY = 'DEVICE_METADATA.localhost.hwsku'
PLATFORM_KEY = 'DEVICE_METADATA.localhost.platform'

EEPROM_MODULE_NAME = 'eeprom'
EEPROM_CLASS_NAME = 'board'

class DaemonBase(object):
    # Redis DB information
    redis_hostname = "localhost"
    redis_port = 6379
    redis_timeout_msecs = 0

    def __init__(self):
        self.log_info("Starting up...")
        # Register our signal handlers
        signal.signal(signal.SIGHUP, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def __del__(self):
        self.log_error("Return from daemon, exiting...")

    def run(self):
        raise NotImplementedError()

    # ========================== Connect to DB ============================
    def db_connect(self, db):
        return swsscommon.DBConnector(db,
                                      self.redis_hostname,
                                      self.redis_port,
                                      self.redis_timeout_msecs)

    # ========================== Syslog wrappers ==========================
    def log_info(self, msg):
        syslog.openlog()
        syslog.syslog(syslog.LOG_INFO, msg)
        syslog.closelog()

    def log_warning(self, msg):
        syslog.openlog()
        syslog.syslog(syslog.LOG_WARNING, msg)
        syslog.closelog()

    def log_error(self, msg):
        syslog.openlog()
        syslog.syslog(syslog.LOG_ERR, msg)
        syslog.closelog()

    #========================== Signal Handling ==========================
    def signal_handler(self, sig, frame):
        if sig == signal.SIGHUP:
            self.log_info("Caught SIGHUP - ignoring...")
            return
        elif sig == signal.SIGINT:
            self.log_info("Caught SIGINT - exiting...")
            sys.exit(128 + sig)
        elif sig == signal.SIGTERM:
            self.log_info("Caught SIGTERM - exiting...")
            sys.exit(128 + sig)
        else:
            self.log_warning("Caught unhandled signal '" + sig + "'")
            return

    #============ Functions to load platform-specific classes ============
    # Returns platform and HW SKU
    def get_platform_and_hwsku(self):
        try:
            proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-H', '-v', PLATFORM_KEY],
                                    stdout=subprocess.PIPE,
                                    shell=False,
                                    stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            platform = stdout.rstrip('\n')

            proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-d', '-v', HWSKU_KEY],
                                    stdout=subprocess.PIPE,
                                    shell=False,
                                    stderr=subprocess.STDOUT)
            stdout = proc.communicate()[0]
            proc.wait()
            hwsku = stdout.rstrip('\n')
        except OSError, e:
            self.log_error("Cannot to detect platform")
            raise OSError("Cannot detect platform")

        return (platform, hwsku)

    # Returns path to hwsku
    def get_path_to_platform_and_hwsku(self):
        # Get platform and hwsku
        (platform, hwsku) = self.get_platform_and_hwsku()

        # Load platform module from source
        platform_path = PLATFORM_ROOT_DOCKER
        hwsku_path = "/".join([platform_path, hwsku])

        return (platform_path, hwsku_path)

    # Loads platform specific psuutil module from source
    def load_platform_util(self, module_name, class_name):
        platform_util = None

        # Get path to platform and hwsku
        (platform_path, hwsku_path) = self.get_path_to_platform_and_hwsku()

        try:
            module_file = "/".join([platform_path, "plugins", module_name + ".py"])
            module = imp.load_source(module_name, module_file)
        except IOError, e:
            self.log_error("Failed to load platform module '%s': %s" % (module_name, str(e)))
            return None

        try:
            platform_util_class = getattr(module, class_name)
            # board class of eeprom requires 4 paramerters, need special treatment here.
            if module_name == EEPROM_MODULE_NAME and class_name == EEPROM_CLASS_NAME:
                platform_util = platform_util_class('','','','')
            else:
                platform_util = platform_util_class()
        except AttributeError, e:
            self.log_error("Failed to instantiate '%s' class: %s" % (class_name, str(e)))
            return None

        return platform_util

