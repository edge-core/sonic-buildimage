from collections import namedtuple

Register = namedtuple("Register", ["addr", "ro"])
NamedRegister = namedtuple("NamedRegister", Register._fields + ("name", ))

Gpio = namedtuple("Gpio", ["bit", "ro", "activeLow"])
NamedGpio = namedtuple("NamedGpio", ("addr",) + Gpio._fields + ("name",))

ResetGpio = namedtuple("ResetGpio", ["addr", "bit", "activeLow", "name"])

class I2cAddr(object):
   def __init__(self, bus, address):
      self.bus = bus
      self.address = address

   def __str__(self):
      return '%d-00%02x' % (self.bus, self.address)

class PciAddr(object):
   def __init__(self, domain=0, bus=0, device=0, func=0):
      self.domain = domain
      self.bus = bus
      self.device = device
      self.func = func

   def __str__(self):
      return '%04x:%02x:%02x.%d' % (self.domain, self.bus, self.device, self.func)


