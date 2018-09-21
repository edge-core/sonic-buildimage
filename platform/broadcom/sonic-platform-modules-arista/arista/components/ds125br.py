import logging
import copy

from ..core.utils import SMBus
from .common import I2cComponent

class Ds125Br(I2cComponent):
   def __init__(self, addr, **kwargs):
      super(Ds125Br, self).__init__(addr, channels=8, **kwargs)

   def qsfpPortConfig(self, amplitude):
      disableCrc = 0x18
      squelchMode = 0x40
      outputAmplitude = amplitude
      assert len(outputAmplitude) == self.channels
      txDeEmphasis = [0x00] * self.channels
      rxEqualization = [0x00] * self.channels
      inputTermination = [0x0c] * self.channels
      squelch = [0x02] * self.channels
      return [disableCrc, squelchMode, outputAmplitude, txDeEmphasis,
              rxEqualization, inputTermination, squelch]

   def qsfpPortGroupConfig(self):
      portConfig = self.qsfpPortConfig([None, 0xac, None, 0xac,
                                        0xab, 0xab, 0xab, 0xac])
      txDeEmphasis = portConfig[3]
      txDeEmphasis[0] = None
      txDeEmphasis[2] = None
      portConfig[3] = txDeEmphasis
      return portConfig

   def getPortConfigs(self):
      qsfp35 = (
         0x59,
         self.qsfpPortConfig([0xaa, 0xaa, 0xaa, 0xaa, 0xa8, 0xa9, 0xa8, 0xa9])
      )
      qsfp36 = (
         0x58,
         self.qsfpPortConfig([0xaa, 0xaa, 0xaa, 0xaa, 0xa9, 0xa9, 0xa9, 0xaa])
      )
      sfp1_2 = (
         0x5a,
         self.qsfpPortGroupConfig()
      )
      sfp3_4 = (
         0x5b,
         self.qsfpPortGroupConfig()
      )
      return [qsfp35, qsfp36, sfp1_2, sfp3_4]

   def setupPort(self, bus, addr, config):
      disableCrc, squelchMode, outputAmplitude, txDeEmphasis, \
                  rxEqualization, inputTermination, squelch = config

      bus.write_byte_data(addr, 0x06,  disableCrc)
      bus.write_byte_data(addr, 0x28, squelchMode)

      baseAddr = 0x0d
      for channel in range(0, self.channels):
         offset = channel * 7
         if (baseAddr + offset) > 0x27:
            offset += 1
         regs = [
            (baseAddr + offset + 0, squelch[channel]),
            (baseAddr + offset + 1, inputTermination[channel]),
            (baseAddr + offset + 2, rxEqualization[channel]),
            (baseAddr + offset + 3, outputAmplitude[channel]),
            (baseAddr + offset + 4, txDeEmphasis[channel]),
         ]
         for reg, data in regs:
            if data is not None:
               logging.debug('i2c-write %#02x %#02x %#02x', addr, reg, data)
               bus.write_byte_data(addr, reg, data)

   def setup(self):
      logging.debug('setting up ds125br repeaters')

      bus = SMBus(self.addr.bus)
      for addr, config in self.getPortConfigs():
         self.setupPort(bus, addr, config)

   def clean(self):
      pass

