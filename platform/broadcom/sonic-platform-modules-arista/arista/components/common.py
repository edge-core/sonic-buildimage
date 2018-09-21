
import logging
import os
import time

from ..core.component import Component, DEFAULT_WAIT_TIMEOUT, ASIC_YIELD_TIME
from ..core.driver import KernelDriver
from ..core.utils import klog, inSimulation
from ..core.types import PciAddr, I2cAddr

class PciComponent(Component):
   def __init__(self, addr, **kwargs):
      assert isinstance(addr, PciAddr)
      super(PciComponent, self).__init__(addr=addr, **kwargs)

class I2cComponent(Component):
   def __init__(self, addr, **kwargs):
      assert isinstance(addr, I2cAddr)
      super(I2cComponent, self).__init__(addr=addr, **kwargs)

class I2cKernelComponent(I2cComponent):
   def __init__(self, addr, name, waitFile=None, **kwargs):
      super(I2cKernelComponent, self).__init__(addr, **kwargs)
      self.addDriver(I2cKernelDriver, name, waitFile)

class PciKernelDriver(KernelDriver):
   def __init__(self, component, name, args=None):
      assert isinstance(component, PciComponent)
      super(PciKernelDriver, self).__init__(component, name, args)

   def getSysfsPath(self):
      return os.path.join('/sys/bus/pci/devices', str(self.component.addr))

class I2cKernelDriver(KernelDriver):
   def __init__(self, component, name, waitFile=None):
      assert isinstance(component, I2cComponent)
      super(I2cKernelDriver, self).__init__(component, None, waitFile)
      self.name = name

   def getSysfsPath(self):
      return os.path.join('/sys/bus/i2c/devices', str(self.component.addr))

   def getSysfsBusPath(self):
      return '/sys/bus/i2c/devices/i2c-%d' % self.component.addr.bus

   def setup(self):
      addr = self.component.addr
      devicePath = self.getSysfsPath()
      path = os.path.join(self.getSysfsBusPath(), 'new_device')
      logging.debug('creating i2c device %s on bus %d at 0x%02x',
                    self.name, addr.bus, addr.address)
      if inSimulation():
         return
      if os.path.exists(devicePath):
         logging.debug('i2c device %s already exists', devicePath)
      else:
         with open(path, 'w') as f:
            f.write('%s 0x%02x' % (self.name, self.component.addr.address))
         self.waitFileReady()

   def clean(self):
      # i2c kernel devices are automatically cleaned when the module is removed
      if inSimulation():
         return
      path = os.path.join(self.getSysfsBusPath(), 'delete_device')
      addr = self.component.addr
      if os.path.exists(self.getSysfsPath()):
         logging.debug('removing i2c device %s from bus %d' % (self.name, addr.bus))
         with open(path, 'w') as f:
            f.write('0x%02x' % addr.address)

   def __str__(self):
      return '%s(%s)' % (self.__class__.__name__, self.name)

class SwitchChip(PciComponent):
   def pciRescan(self):
      logging.info('triggering kernel pci rescan')
      with open('/sys/bus/pci/rescan', 'w') as f:
         f.write('1\n')

   def waitForIt(self, timeout=DEFAULT_WAIT_TIMEOUT):
      begin = time.time()
      end = begin + timeout
      rescanTime = begin + (timeout / 2)
      devPath = os.path.join('/sys/bus/pci/devices/', str(self.addr))

      logging.debug('waiting for switch chip %s', devPath)
      if inSimulation():
         return True

      klog('waiting for switch chip')
      while True:
         now = time.time()
         if now > end:
            break
         if os.path.exists(devPath):
            logging.debug('switch chip is ready')
            klog('switch chip is ready')
            time.sleep(ASIC_YIELD_TIME)
            klog('yielding...')
            return True
         if now > rescanTime:
            self.pciRescan()
            rescanTime = end
         time.sleep(0.1)

      logging.error('timed out waiting for the switch chip %s', devPath)
      return False

