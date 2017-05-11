#python 3

"""
	IP address library
"""

#
#	[todo]: speed up dipv4_to_pipv4
#

#
# conversions between ip formats 
#
#		formats: (decimal "d-", hexidecimal "x-", binary "b-", standard dotted-quad string (a in socket library, ipv4)  "s-", byte string ip (32-bit packed binary format, as a string four characters in length) "p-"), (ipv4 "-v4", ipv6 "-v6")
#

import socket
import struct

#other
import csv
import binascii
import os
import random

#resources
COUNTRY_RANGES_FNAME = "iana_ip_ranges/ipv4_country_masks.csv"
BINARY_RANGE_FNAME = "binary_range_map_v3.bin"

#constants
BYTES_IN_IP = 4

#
#	struct.pack(fmt, v1, v2, ...) Return a string containing the values v1, v2, ... packed according to the given format.
#
#	struct.unpack(fmt, string) Unpack the string according to the given format. The result is a tuple
#
# '!' is byte order, network standard (big endian)
# 'L' is long (4 bytes for ipv4 address) (size of string)
# 		presumably 'q' long long for 8 byte ipv6 address


#	
#	socket.inet_ntoa(packed_ip) Convert a 32-bit packed IPv4 address (a string four characters in length) to its standard dotted-quad string representation
#
#	socket.inet_aton(ip_string) Convert an IPv4 address from dotted-quad string format (for example, ‘123.45.67.89’) to 32-bit packed binary format, as a string four characters in length.
#

#
# 32-bit packed binary format packed ip conversions "pip"
#
def pipv4_2_sipv4(pipv4):
	return socket.inet_ntoa(pipv4)

def pipv4_2_dipv4(pipv4):
	return struct.unpack("!L", pipv4)[0]

#
# standard dotted-quad string ip conversions "sip"
#
def sipv4_2_pipv4(sipv4):
	return socket.inet_aton(sipv4)

def sipv4_2_dipv4(sipv4): 
	return struct.unpack("!L", sipv4_2_pipv4(sipv4))[0]

#
# decimal int format ip conversions "dip"
#
def dipv4_2_pipv4(dipv4):
	return socket.inet_aton(dipv4_2_sipv4(dipv4))

def dipv4_2_sipv4(dipv4): 
	return socket.inet_ntoa(struct.pack('!L', dipv4))


def create_binary_range_file():

	#read in IANA terminals to bytestring
	bfile_contents = bytearray(b'')
	with open(COUNTRY_RANGES_FNAME, mode='r') as f:
		reader = csv.reader(f)
		for row in reader:									#row 0, row 1 = term1, term2
			bfile_contents += bytearray( dipv4_2_pipv4(int(row[0])) + dipv4_2_pipv4(int(row[1])) )

	#write byte array (bfile contents) to binary file
	with open(BINARY_RANGE_FNAME, "wb") as f:
		f.write(bfile_contents)

def random_ipv4str():

	#random location
	fsize_bytes = os.path.getsize(BINARY_RANGE_FNAME)
	num_terminal_pairs = fsize_bytes / ( BYTES_IN_IP * 2 )
	byte_index = random.randrange(0, num_terminal_pairs + 2, 2)

	#read binary file at chose byte location
	with open(BINARY_RANGE_FNAME, 'rb') as f:
		f.seek( byte_index * BYTES_IN_IP, 1 )						#skip to chosen location in file
		
		#read in selected terminals (dipv4)
		terminal_1_dipv4 = pipv4_2_dipv4(f.read( BYTES_IN_IP ))
		terminal_2_dipv4 = pipv4_2_dipv4(f.read( BYTES_IN_IP ))

		return dipv4_2_sipv4(random.randrange(terminal_1_dipv4, terminal_2_dipv4))


#test distribution of randomly generated ips, tmp***
#create_binary_range_file()
for i in range (10000):
	random_ipv4str()


