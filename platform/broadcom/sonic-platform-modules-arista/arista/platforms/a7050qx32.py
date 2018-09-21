from ..core.platform import registerPlatform, Platform
from ..core.driver import KernelDriver
from ..core.utils import incrange
from ..core.types import PciAddr, I2cAddr, Gpio, NamedGpio, ResetGpio
from ..core.component import Priority

from ..components.common import SwitchChip, I2cKernelComponent
from ..components.scd import Scd
from ..components.ds460 import Ds460

@registerPlatform('DCS-7050QX-32')
class Cloverdale(Platform):
   def __init__(self):
      super(Cloverdale, self).__init__()

      self.fanCount = 4
      self.qsfp40gAutoRange = incrange(1, 24)
      self.qsfp40gOnlyRange = incrange(25, 32)
      self.allQsfps = sorted(self.qsfp40gAutoRange + self.qsfp40gOnlyRange)
      self.sfpRange = []

      self.inventory.addPorts(qsfps=self.allQsfps)

      self.addDriver(KernelDriver, 'raven-fan-driver', '/sys/class/hwmon/hwmon1')

      switchChip = SwitchChip(PciAddr(bus=0x02))
      self.addComponent(switchChip)

      scd = Scd(PciAddr(bus=0x04))
      self.addComponent(scd)

      scd.addComponents([
         I2cKernelComponent(I2cAddr(2, 0x4c), 'max6658', '/sys/class/hwmon/hwmon2'),
         I2cKernelComponent(I2cAddr(3, 0x48), 'lm73', '/sys/class/hwmon/hwmon3'),
         Ds460(I2cAddr(5, 0x58), priority=Priority.BACKGROUND),
         Ds460(I2cAddr(6, 0x58), priority=Priority.BACKGROUND),

         # Due to a risk of an unrecoverable firmware corruption when a pmbus
         # transaction is done at the same moment of the poweroff, the handling of
         # the DPM is disabled. If you want rail information use it at your own risk
         #I2cKernelComponent(I2cAddr(3, 0x4e), 'pmbus'), # ucd90120A
         #I2cKernelComponent(I2cAddr(7, 0x4e), 'pmbus'), # ucd90120A
      ])

      scd.addSmbusMasterRange(0x8000, 5)

      scd.addLeds([
         (0x6050, 'status'),
         (0x6060, 'fan_status'),
         (0x6070, 'psu1'),
         (0x6080, 'psu2'),
         (0x6090, 'beacon'),
      ])
      self.inventory.addStatusLeds(['status', 'fan_status', 'psu1',
         'psu2'])

      scd.addResets([
         ResetGpio(0x4000, 0, False, 'switch_chip_reset'),
         ResetGpio(0x4000, 2, False, 'phy1_reset'),
         ResetGpio(0x4000, 3, False, 'phy2_reset'),
         ResetGpio(0x4000, 4, False, 'phy3_reset'),
         ResetGpio(0x4000, 5, False, 'phy4_reset'),
      ])

      scd.addGpios([
         NamedGpio(0x5000, 0, True, False, "psu1_present"),
         NamedGpio(0x5000, 1, True, False, "psu2_present"),
      ])
      self.inventory.addPsus([scd.createPsu(1, False), scd.createPsu(2, False)])

      addr = 0x6100
      for xcvrId in self.qsfp40gAutoRange:
         for laneId in incrange(1, 4):
            name = "qsfp%d_%d" % (xcvrId, laneId)
            scd.addLed(addr, name)
            self.inventory.addXcvrLed(xcvrId, name)
            addr += 0x10

      addr = 0x6720
      for xcvrId in self.qsfp40gOnlyRange:
         name = "qsfp%d" % xcvrId
         scd.addLed(addr, name)
         self.inventory.addXcvrLed(xcvrId, name)
         addr += 0x30 if xcvrId % 2 else 0x50

      addr = 0x5010
      bus = 10
      for xcvrId in self.allQsfps:
         xcvr = scd.addQsfp(addr, xcvrId, bus)
         scd.addComponent(I2cKernelComponent(
            I2cAddr(bus, xcvr.eepromAddr), 'sff8436'))
         self.inventory.addXcvr(xcvr)
         addr += 0x10
         bus += 1
