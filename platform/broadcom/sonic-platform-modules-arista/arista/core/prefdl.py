#!/usr/bin/env python
#
# Copyright (C) 2016 Arista Networks, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import struct
import sys
import zlib

def showMac( m ):
   return ":".join([m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:12]])

typeMap = {
   "END" : ( "00", None, None, None, False ),
   "SKU" : ( "03", None, None, None, False ),
   "MAC" : ( "05", None, showMac, None, False ),
   "SerialNumber" : ( "0E", None, None, None, False ),
}

idToNameMap = {}
for k, v in typeMap.items():
   idToNameMap[ v[0] ] = k

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

   def data( self ):
      res = {}
      for f in self.requiredFields + self.tlvFields.values():
         for d in f.data:
            dStr = d if f.show is None else f.show( d )
            res[f.name] = dStr
      return res

   def show( self ):
      for k, v in self.data().items():
         print("%s: %s" % (k, v))

   def writeToFile(self, f):
      with open(f, 'w+') as fp:
         for k, v in self.data().items():
            fp.write("%s: %s\n" % (k, v))

   def getField( self, name ):
      return self.data().get( name, None )

   def getCrc( self ):
      return self.crc

class PreFdlFromFile():
   def __init__(self, fp):
      self._data = {}
      for line in fp:
         key, val = line.strip().split(': ', 1)
         self._data[key] = val
      self.crc = self._data.pop('Crc', -1)

   def data(self):
      return self._data

   def show(self):
      for key, val in self._data.items():
         print("%s: %s" % (key, val))

   def getField(self, name):
      return self._data[name]

   def getCrc(self):
      return self.crc

def decode( fp ):
   data = fp.read( 4 )
   data = data.strip()
   # For format 0002 and more recent fdls use the new Prefdl class
   if data not in ( "0002", "0003" ):
      raise ValueError
   return PreFdl( fp, data, data )

def main():
   output = sys.argv[1]

   if output == "-":
      fp = sys.stdin
   else:
      fp = file( output, "r" )

   decode( fp ).show()

if __name__ == "__main__":
   main()
