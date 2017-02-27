#!/usr/bin/env python

#############################################################################
# Arista 7050-QX32
#
# Platform and model specific eeprom subclass, inherits from the base class,
# and provides the followings:
# - the eeprom format definition
# - specific encoder/decoder if there is special need
#############################################################################

try:
    import exceptions
    import binascii
    import time
    import optparse
    import warnings
    import os
    import sys
    import subprocess
    import re
    import struct
    import zlib
    import StringIO
    from sonic_eeprom import eeprom_base
    from sonic_eeprom import eeprom_tlvinfo
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")

def showMac( m ):
   return ":".join([m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:12]])

typeMap = {
   "END" : ( "00", None, None, None, False ),
   "SKU" : ( "03", None, None, None, False ),
   "MAC" : ( "05", None, showMac, None, False ),
   "SerialNumber" : ( "0E", None, None, None, False ),
   }

idToNameMap = {}
for k, v in typeMap.iteritems():
   idToNameMap[ v[0] ] = k

class board(eeprom_tlvinfo.TlvInfoDecoder):
    _TLV_INFO_MAX_LEN = 256 
    _TLV_HDR_ENABLED = 0

    pFdl = None

    def __init__(self, name, path, cpld_root, ro):
        self.eeprom_path = "/sys/bus/i2c/drivers/eeprom/1-0052/eeprom"
        super(board, self).__init__(self.eeprom_path, 0, '', True)

    def _decode_eeprom(self, e):
        # For format 0002 and more recent fdls use the new Prefdl class
        data = e[0:4]
        if data in ("0002", "0003"):
            fp = StringIO.StringIO(e[4:])
            self.pFdl = PreFdl( fp, data, data )

    def decode_eeprom(self, e):
        self._decode_eeprom(e)
        return self.pFdl.show()

    def is_checksum_valid(self, e):
        self._decode_eeprom(e)
        return (True, self.pFdl.get_crc())

    def serial_number_str(self, e):
        self._decode_eeprom(e)
        return self.pFdl.get_field('SerialNumber')

    def mgmtaddrstr(self,e):
        self._decode_eeprom(e)
        return self.pFdl.get_field('MAC')

def crc32( data ):
   return struct.unpack("I",struct.pack("i",zlib.crc32( data )))[0]

def validSerial( x ):
   x = x.replace( " ", "" )
   x = x.replace( "-", "" )
   # All serial numbers are upper case
   x = x.upper()
   if re.compile( "[A-Z]{3}\d{4}[A-Z0-9]{4}$" ).match( x ):
      return x
   return None

class PreFdlField( ):
   def __init__( self, name, valid, show, optionName, data=None, append=False ):
      self.name = name
      if valid:
         self.valid = valid
      else:
         self.valid = lambda x: x
      self.show = show
      self.optionName = optionName
      self.data = []
      self.append = append
      if data:
         self.dataIs( data )

   def dataIs( self, data ):
      vd = self.valid( data )
      if not vd:
         raise InvalidPrefdlData( "Invalid %s: %s" % ( self.name, data ) )
      if self.append:
         self.data.append( vd )
      else:
         self.data = [ vd ]

class TlvField( PreFdlField ):
   def __init__( self, name ):
      args = typeMap.get( name )
      valid = None
      show = None
      optionName = None
      append = False
      if args:
         self.id, valid, show, optionName, append = args
      PreFdlField.__init__( self, name, valid, show, optionName, append=append )


class PreFdl():
   def __init__( self, fp=None, preFdlStr=None, version="0002" ):
      # populate the required fields
      self.requiredFields = []
      self.mac = None
      self.serial = None

      if version == "0002":
         preFdlStr, offset = self.initPreFdl2( fp, preFdlStr )
      elif version == "0003":
         preFdlStr, offset = self.initPreFdl3( fp, preFdlStr )
      else:
         raise NotImplementedError(
            "Only Prefdl data format version 0002 or 0003 are supported" )

      # populate the tlv fileds
      self.tlvFields = {}
      for k in typeMap.keys():
         self.tlvFields[ k ] = TlvField( k )

      # create the map option to field
      self.optionMap = {}
      for f in self.requiredFields + self.tlvFields.values():
         # Do not add the option from TLV if already added by required fields
         if f.optionName and f.optionName not in self.optionMap:
            self.optionMap[ f.optionName ] = f

      # save the current tlv fields
      if fp:
         while True:
            tlv = fp.read( 6 )
            ( id, lengthStr ) = ( tlv[0:2], tlv[2:6] )
            length = int( lengthStr, base=16 )
            bytes = fp.read( length )
            what = None if id not in idToNameMap.keys() else idToNameMap[ id ]
            if what and what != "END":
               self.tlvFields[ what ].dataIs( bytes )
            preFdlStr += tlv + bytes
            offset += 6 + length
            if what == "END":
               # End of the tlv list
               break
         self.crc = fp.read( 8 )
         # Check the CRC
         computed = crc32( preFdlStr )
         if int( self.crc, 16 ) != computed:
            raise Exception( "Invalid CRC -- saw %s expected %8X" %
                             ( self.crc, computed ) )

   # Initialize and parse fixed section for prefdl version 2.  Return the offset
   # to where the TLV section starts.
   def initPreFdl2( self, fp, preFdlStr ):
      # if we start with an existing file
      if fp:
         # if no preFdlStr is specified, read the fixed section, 30 bytes.
         # Otherwise, only the 4 byte data version section was written and
         # read the remaining 26 bytes from the fixed section.
         if not preFdlStr:
            preFdlStr = fp.read( 30 ).strip()
         elif preFdlStr == "0002":
            preFdlStr += fp.read( 26 ).strip()
         else:
            raise ValueError( "preFdlStr arg has invalid data format" )
         if len( preFdlStr ) < 12:
            fatal( "prefdl is too short exiting" )
      data = None if not preFdlStr else preFdlStr[ 16:16 + 11 ]
      self.requiredFields.append(
         PreFdlField( "SerialNumber", validSerial, None, None, data ) )
      return preFdlStr, 30

   # Initialize and parse fixed section for prefdl version 3.  Return the offset
   # to where the TLV section starts.
   def initPreFdl3( self, fp, preFdlStr ):
      # if we start with an existing file
      currPtr = 0
      if fp and not preFdlStr:
         preFdlStr = fp.read( 4 ).strip()
         if len( preFdlStr ) < 4:
            fatal( "prefdl is too short exiting" )
      return preFdlStr, 4

   def show( self ):
      for f in self.requiredFields + self.tlvFields.values():
         for d in f.data:
            dStr = d if f.show is None else f.show( d )
            print "%s: %s" % ( f.name, dStr )

   def get_field( self, name ):
      for f in self.requiredFields + self.tlvFields.values():
         for d in f.data:
            if f.name == name:
               dStr = d if f.show is None else f.show( d )
               return dStr

   def get_crc( self ):
      return self.crc

