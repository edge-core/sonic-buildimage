#!/usr/bin/env python2

try:
    import imp
    import signal
    import subprocess
    import os
    import sys
    import syslog
except ImportError, e:
    raise ImportError (str(e) + " - required module not found")

#
# Constants ====================================================================
#
REDIS_TIMEOUT_MSECS = 0

# Platform root directory inside docker
PLATFORM_ROOT_DOCKER = '/usr/share/sonic/platform'
SONIC_CFGGEN_PATH = '/usr/local/bin/sonic-cfggen'
SONIC_ENV_FILE = '/etc/sonic/sonic-environment'
PLATFORM_ENVVAR = 'PLATFORM'
HWSKU_ENVVAR = 'HWSKU'
HWSKU_KEY = 'DEVICE_METADATA.localhost.hwsku'
PLATFORM_KEY = 'DEVICE_METADATA.localhost.platform'

# Port config information
PORT_CONFIG = 'port_config.ini'
PLATFORM_JSON = 'platform.json'

EEPROM_MODULE_NAME = 'eeprom'
EEPROM_CLASS_NAME = 'board'

#
# Helper functions =============================================================
#

def db_connect(db_name):
    from swsscommon import swsscommon
    return swsscommon.DBConnector(db_name,
                                  REDIS_TIMEOUT_MSECS,
                                  True)

#
# Helper classes ===============================================================
#

class Logger(object):
    def __init__(self, syslog_identifier = None):
        self.syslog = syslog
        if syslog_identifier is None:
            self.syslog.openlog()
        else:
            self.syslog.openlog(ident=syslog_identifier, logoption=self.syslog.LOG_NDELAY, facility=self.syslog.LOG_DAEMON)

    def __del__(self):
        self.syslog.closelog()

    def log_error(self, msg, also_print_to_console=False):
        self.syslog.syslog(self.syslog.LOG_ERR, msg)

        if also_print_to_console:
            print msg

    def log_warning(self, msg, also_print_to_console=False):
        self.syslog.syslog(self.syslog.LOG_WARNING, msg)

        if also_print_to_console:
            print msg

    def log_notice(self, msg, also_print_to_console=False):
        self.syslog.syslog(self.syslog.LOG_NOTICE, msg)

        if also_print_to_console:
            print msg

    def log_info(self, msg, also_print_to_console=False):
        self.syslog.syslog(self.syslog.LOG_INFO, msg)

        if also_print_to_console:
            print msg

    def log_debug(self, msg, also_print_to_console=False):
        self.syslog.syslog(self.syslog.LOG_DEBUG, msg)

        if also_print_to_console:
            print msg

#
# Daemon =======================================================================
#

class DaemonBase(object):
    def __init__(self):
        # Register our signal handlers
        '''all daemons inherit from daemon_base class, and for
        signal handling functionality they register the signal_handler() by
        overriding the siganl_handler() in daemon_base by their own
        implmentation.
        But some sonic_platform instances also can invoke the daemon_base
        constructor while trying to instantiate the common utilities
        for example
        platform_chassis = sonic_platform.platform.Platform().get_chassis()
        This will cause the re registration of signal_handler which will
        cause base class signal_handler() to be invoked when the daemon
        gets a signal, whereas the derived class signal_handler should have
        been invoked. The if checks will not allow the re registration
        of signal handler '''
        if not signal.getsignal(signal.SIGHUP):
            signal.signal(signal.SIGHUP, self.signal_handler)
        if not signal.getsignal(signal.SIGINT):
            signal.signal(signal.SIGINT, self.signal_handler)
        if not signal.getsignal(signal.SIGTERM):
            signal.signal(signal.SIGTERM, self.signal_handler)

    # Signal handler
    def signal_handler(self, sig, frame):
        if sig == signal.SIGHUP:
            syslog.syslog(syslog.LOG_INFO, "Caught SIGHUP - ignoring...")
        elif sig == signal.SIGINT:
            syslog.syslog(syslog.LOG_INFO, "Caught SIGINT - exiting...")
            sys.exit(128 + sig)
        elif sig == signal.SIGTERM:
            syslog.syslog(syslog.LOG_INFO, "Caught SIGTERM - exiting...")
            sys.exit(128 + sig)
        else:
            syslog.syslog(syslog.LOG_WARNING, "Caught unhandled signal '" + sig + "'")

    # Returns platform and hwsku
    def get_platform_and_hwsku(self):
        try:
            platform = hwsku = None
            if os.path.exists(SONIC_ENV_FILE):
                with open(SONIC_ENV_FILE, "r") as env_file:
                    for line in env_file:
                        if PLATFORM_ENVVAR in line:
                            platform = line.split('=')[1]
                        if HWSKU_ENVVAR in line:
                            hwsku = line.split('=')[1]

            if not platform: 
                proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-H', '-v', PLATFORM_KEY],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        shell=False)
                stdout, stderr = proc.communicate()
                assert not stderr and not proc.returncode, "Failed to detect platform: %s, rc: %s" % (stderr, proc.returncode)
                platform = stdout.rstrip('\n')

            if not hwsku:
                proc = subprocess.Popen([SONIC_CFGGEN_PATH, '-d', '-v', HWSKU_KEY],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        shell=False)
                stdout, stderr = proc.communicate()
                assert not stderr and not proc.returncode, "Failed to detect hwsku: %s, rc: %s" % (stderr, proc.returncode)
                hwsku = stdout.rstrip('\n')
        except OSError, e:
            raise OSError("Failed to detect platform: %s" % (str(e)))

        return (platform, hwsku)

    # Returns path to platform and hwsku
    def get_path_to_platform_and_hwsku(self):
        # Get platform and hwsku
        (platform, hwsku) = self.get_platform_and_hwsku()

        # Load platform module from source
        platform_path = PLATFORM_ROOT_DOCKER
        hwsku_path = "/".join([platform_path, hwsku])

        return (platform_path, hwsku_path)

    # Returns path to port config file
    def get_path_to_port_config_file(self):
        # Get platform and hwsku path
        (platform_path, hwsku_path) = self.get_path_to_platform_and_hwsku()

        # First check for the presence of the new 'platform.json' file
        port_config_file_path = "/".join([platform_path, PLATFORM_JSON])
        if not os.path.isfile(port_config_file_path):

            # platform.json doesn't exist. Try loading the legacy 'port_config.ini' file
            port_config_file_path = "/".join([hwsku_path, PORT_CONFIG])
            if not os.path.isfile(port_config_file_path):
                raise IOError("Failed to detect port config file: %s" % (port_config_file_path))

        return port_config_file_path

    # Loads platform specific psuutil module from source
    def load_platform_util(self, module_name, class_name):
        platform_util = None

        # Get path to platform and hwsku
        (platform_path, hwsku_path) = self.get_path_to_platform_and_hwsku()

        try:
            module_file = "/".join([platform_path, "plugins", module_name + ".py"])
            module = imp.load_source(module_name, module_file)
        except IOError, e:
            raise IOError("Failed to load platform module '%s': %s" % (module_name, str(e)))

        try:
            platform_util_class = getattr(module, class_name)
            # board class of eeprom requires 4 paramerters, need special treatment here.
            if module_name == EEPROM_MODULE_NAME and class_name == EEPROM_CLASS_NAME:
                platform_util = platform_util_class('','','','')
            else:
                platform_util = platform_util_class()
        except AttributeError, e:
            raise AttributeError("Failed to instantiate '%s' class: %s" % (class_name, str(e)))

        return platform_util

    # Runs daemon
    def run(self):
        raise NotImplementedError()
