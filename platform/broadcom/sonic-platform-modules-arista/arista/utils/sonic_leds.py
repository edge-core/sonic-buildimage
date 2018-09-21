import re
from collections import namedtuple, defaultdict

from ..core import platform
import arista.platforms

try:
   from sonic_led import led_control_base
except ImportError as e:
   raise ImportError ('%s - required module not found' % str(e))

Port = namedtuple('Port', ['portNum', 'lanes', 'offset', 'singular'])

def parsePortConfig(portConfigPath):
   '''
   Returns a dictionary mapping port name ("Ethernet48") to a named tuple of port
   number, # of lanes, the offset (0 to 3 from the first lane in qsfp) and the
   singularity of the lane (if it is in 100G/40G mode)
   '''
   portMapping = {}

   with open(portConfigPath) as fp:
      for line in fp:
         line = line.strip()
         if not line or line[0] == '#':
            continue

         fields = line.split()
         # "portNum" is determined from the fourth column (port), or the first number
         # in the third column (alias).
         # "lanes" is determined from the number of lanes in the second column.
         # "offset" is determined from the second number in the third column (alias).
         # "singular" is determined by if the alias has a '/' character or not.
         if len(fields) < 3:
            continue
         name = fields[0]
         lanes = len(fields[1].split(','))
         alias = fields[2]
         aliasRe = re.findall(r'\d+', alias)
         try:
            portNum = int(fields[3])
         except IndexError:
            portNum = int(aliasRe[0])
         if len(aliasRe) < 2:
            offset = 0
            singular = True
         else:
            offset = int(aliasRe[1]) - 1
            singular = False

         portMapping[name] = Port(portNum, lanes, offset, singular)

   return portMapping

class LedControl(led_control_base.LedControlBase):
   PORT_CONFIG_PATH = '/usr/share/sonic/hwsku/port_config.ini'
   LED_SYSFS_PATH = '/sys/class/leds/{0}/brightness'

   LED_COLOR_OFF = 0
   LED_COLOR_GREEN = 1
   LED_COLOR_YELLOW = 2

   def __init__(self):
      self.portMapping = parsePortConfig(self.PORT_CONFIG_PATH)
      self.portSysfsMapping = defaultdict(list)

      inventory = platform.getPlatform().getInventory()
      for port, names in inventory.xcvrLeds.items():
         for name in names:
            self.portSysfsMapping[port].append(self.LED_SYSFS_PATH.format(name))

      # Set status leds to green initially (Rook led driver does this automatically)
      for statusLed in inventory.statusLeds:
         with open(self.LED_SYSFS_PATH.format(statusLed), 'w') as fp:
            fp.write('%d' % self.LED_COLOR_GREEN)

   def port_link_state_change(self, port, state):
      '''
      Looks up the port in the port mapping to determine the front number and how
      many subsequent LEDs should be affected (hardcoded by the port_config)
      '''
      p = self.portMapping.get(port)
      if not p:
         return
      for idx in range(p.lanes):
         path = self.portSysfsMapping[p.portNum][p.offset + idx]
         with open(path, 'w') as fp:
            if state == 'up':
               if idx == 0:
                  fp.write('%d' % self.LED_COLOR_GREEN)
               else:
                  fp.write('%d' % self.LED_COLOR_YELLOW)
            elif state == 'down':
               fp.write('%d' % self.LED_COLOR_OFF)
         if p.singular:
            return

def getLedControl():
   return LedControl
