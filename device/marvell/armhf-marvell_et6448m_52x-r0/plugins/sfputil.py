#!/usr/bin/env python

try:
    import os
    import time
    import re
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")

smbus_present = 1

try:
    import smbus
except ImportError, e:
    smbus_present = 0

class SfpUtil(SfpUtilBase):
    """Platform specific sfputil class"""

    _port_start = 49
    _port_end = 52
    ports_in_block = 4

    _port_to_eeprom_mapping = {}
    port_to_i2c_mapping = {
         49 : 0,
         50 : 0,
         51 : 0,
         52 : 0
    }

    _qsfp_ports = range(_port_start, ports_in_block + 1)

    def __init__(self):
        # Override port_to_eeprom_mapping for class initialization
    	if not os.path.exists("/sys/class/gpio/gpio50/") :
            os.system("echo 50 >  /sys/class/gpio/gpiochip32/subsystem/export")
    	if not os.path.exists("/sys/class/gpio/gpio52/") :
            os.system("echo 52 >  /sys/class/gpio/gpiochip32/subsystem/export")
    	os.system("echo out > /sys/class/gpio/gpio50/direction")
    	os.system("echo out > /sys/class/gpio/gpio52/direction ")

        if not os.path.exists("/sys/bus/i2c/devices/0-0050") :
            os.system("echo optoe2 0x50 > /sys/bus/i2c/devices/i2c-0/new_device")

        eeprom_path = '/sys/bus/i2c/devices/0-0050/eeprom'
        for x in range(self.port_start, self.port_end + 1):
            port_eeprom_path = eeprom_path.format(self.port_to_i2c_mapping[x])
            self.port_to_eeprom_mapping[x] = port_eeprom_path
        # Enable optical SFP Tx
        if smbus_present == 0 :
            os.system("i2cset -y -m 0x0f 0 0x41 0x5 0x00")
        else :
            bus = smbus.SMBus(0)
            DEVICE_ADDRESS = 0x41
            DEVICEREG = 0x5 
            OPTIC_E =  bus.read_byte_data(DEVICE_ADDRESS, DEVICEREG)
            OPTIC_E = OPTIC_E & 0xf0
            bus.write_byte_data(DEVICE_ADDRESS, DEVICEREG, OPTIC_E) 
        SfpUtilBase.__init__(self)

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = "/sys/bus/i2c/devices/{0}-0050/sfp_port_reset"
        port_ps = path.format(self.port_to_i2c_mapping[port_num+1])
          
        try:
            reg_file = open(port_ps, 'w')
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return False

        #toggle reset
        reg_file.seek(0)
        reg_file.write('1')
        time.sleep(1)
        reg_file.seek(0)
        reg_file.write('0')
        reg_file.close()
        return True

    def set_low_power_mode(self, port_nuM, lpmode):
        raise NotImplementedError

    def get_low_power_mode(self, port_num):
        raise NotImplementedError
      
    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False
    	prt = port_num % 49
    	prt = "{0:02b}".format(prt)
    	p = prt[0]
    	q = prt[1]
    	cmd1 = "echo " + q + " > /sys/class/gpio/gpio50/value"
    	cmd2 = "echo " + p + " > /sys/class/gpio/gpio52/value"
    	os.system(cmd1)
    	os.system(cmd2)

        '''if port_num == 49 :
       	os.system("echo 0 > /sys/class/gpio/gpio50/value")
       	os.system("echo 0 > /sys/class/gpio/gpio52/value")
       if port_num == 50 :                         
                   os.system("echo 0 > /sys/class/gpio/gpio50/value")
                   os.system("echo 0 > /sys/class/gpio/gpio52/value")
       if port_num == 51 :                         
                   os.system("echo 0 > /sys/class/gpio/gpio50/value")
                   os.system("echo 0 > /sys/class/gpio/gpio52/value")
       if port_num == 52:                         
                   os.system("echo 0 > /sys/class/gpio/gpio50/value")
                   os.system("echo 0 > /sys/class/gpio/gpio52/value")'''
        path = "/sys/bus/i2c/devices/0-0050/eeprom"
        #port_ps = path.format(self.port_to_i2c_mapping[port_num+1])

        try:
            reg_file = open(path)
            reg_file.seek(01)
            reg_file.read(02)
        except IOError as e:
            #print "Error: unable to open file: %s" % str(e)
	    
            return False

        #reg_value = reg_file.readline().rstrip()
        #if reg_value == '1':
        #    return True

        return True

    def read_porttab_mappings(self, porttabfile):
        logical = []
        logical_to_bcm = {}
        logical_to_physical = {}
        physical_to_logical = {}
        last_fp_port_index = 0
        last_portname = ""
        first = 1
        port_pos_in_file = 0
        parse_fmt_port_config_ini = False

        try:
            f = open(porttabfile)
        except:
            raise

        parse_fmt_port_config_ini = (os.path.basename(porttabfile) == "port_config.ini")

        # Read the porttab file and generate dicts
        # with mapping for future reference.
        #
        # TODO: Refactor this to use the portconfig.py module that now
        # exists as part of the sonic-config-engine package.
        title = []
        for line in f:
            line.strip()
            if re.search("^#", line) is not None:
                # The current format is: # name lanes alias index speed
                # Where the ordering of the columns can vary
                title = line.split()[1:]
                continue

            # Parsing logic for 'port_config.ini' file
            if (parse_fmt_port_config_ini):
                # bcm_port is not explicitly listed in port_config.ini format
                # Currently we assume ports are listed in numerical order according to bcm_port
                # so we use the port's position in the file (zero-based) as bcm_port
                portname = line.split()[0]

                bcm_port = str(port_pos_in_file)
		#print("portname " + portname)

                if "index" in title:
                    fp_port_index = int(line.split()[title.index("index")])
                # Leave the old code for backward compatibility
                elif len(line.split()) >= 4:
                    fp_port_index = int(line.split()[3])
                else:
                    fp_port_index = portname.split("Ethernet").pop()
                    fp_port_index = int(fp_port_index.split("s").pop(0))+1
		    #print(fp_port_index)
            else:  # Parsing logic for older 'portmap.ini' file
                (portname, bcm_port) = line.split("=")[1].split(",")[:2]

                fp_port_index = portname.split("Ethernet").pop()
                fp_port_index = int(fp_port_index.split("s").pop(0))+1

            if ((len(self.sfp_ports) > 0) and (fp_port_index not in self.sfp_ports)):
                continue

            if first == 1:
                # Initialize last_[physical|logical]_port
                # to the first valid port
                last_fp_port_index = fp_port_index
                last_portname = portname
                first = 0

            logical.append(portname)

            logical_to_bcm[portname] = "xe" + bcm_port
            logical_to_physical[portname] = [fp_port_index]
            if physical_to_logical.get(fp_port_index) is None:
                physical_to_logical[fp_port_index] = [portname]
            else:
                physical_to_logical[fp_port_index].append(
                    portname)

            if (fp_port_index - last_fp_port_index) > 1:
                # last port was a gang port
                for p in range(last_fp_port_index+1, fp_port_index):
                    logical_to_physical[last_portname].append(p)
                    if physical_to_logical.get(p) is None:
                        physical_to_logical[p] = [last_portname]
                    else:
                        physical_to_logical[p].append(last_portname)

            last_fp_port_index = fp_port_index
            last_portname = portname

            port_pos_in_file += 1

        self.logical = logical
        self.logical_to_bcm = logical_to_bcm
        self.logical_to_physical = logical_to_physical
        self.physical_to_logical = physical_to_logical

       
        #print(self.logical_to_physical)
	'''print("logical: " + self.logical)
        print("logical to bcm: " + self.logical_to_bcm)
        print("logical to physical: " + self.logical_to_physical)
        print("physical to logical: " + self.physical_to_logical)'''
       


    @property
    def port_start(self):
        return self._port_start

    @property
    def port_end(self):
        return self._port_end
	
    @property
    def qsfp_ports(self):
        return self._qsfp_ports

    @property 
    def port_to_eeprom_mapping(self):
         return self._port_to_eeprom_mapping
    
    @property
    def get_transceiver_change_event(self):
        raise NotImplementedError 
