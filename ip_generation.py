#python 3
"""
	fast random ip generation within IANA ranges

	 (byte offset ip generation for fast ip generation within range)
	#range terminals are all that are needed and they are const size (binary file)
	[term1][term2]
"""
#import sys
import binascii
import os
import random
import csv
#for decimal ip to ipv4 standard conversion
import socket
import struct


#resources
COUNTRY_RANGES_FNAME = "iana_ip_ranges/ipv4_country_masks.csv"
BINARY_RANGE_FNAME = "binary_range_map.bin"
#BINARY_RANGE_FPATH = os.path.abspath(__file__) + '/' + BINARY_RANGE_FNAME

#consts
BYTES_IN_IP = 4

def dec_ip_2_ip(dec_ip):
	return socket.inet_ntoa(struct.pack('!L', dec_ip))

def int10_2_hexstr(dec,size_bytes): 
	# cp855 encoding : \x00\x00
	#(decimal number, number of bytes)
	#binary = binascii.unhexlify('{:0{}x}'.format(0, int(8)))
	#return binascii.unhexlify('{:0{}x}'.format(dec, int(size_bytes)))
	#(1024).to_bytes(2, byteorder='big')
	size_hex_digits = size_bytes*2
	return '{:0{}x}'.format(dec, int(size_hex_digits))

def hexstr_2_int10(hexstr):
	return int.from_bytes(hexstr, byteorder='big')

def create_binary_terminal_file():

	#read in terminal ip array
	iplist_decimal = []
	with open(COUNTRY_RANGES_FNAME, mode='r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			iplist_decimal.append(int(row[0]))	#term1
			iplist_decimal.append(int(row[1]))	#term2


	#create byte array from dec terminal ip list
	bytestring = ""
	for ip in iplist_decimal:
		bytestring += int10_2_hexstr(ip,BYTES_IN_IP)
	bfile_contents = bytearray(binascii.unhexlify(bytestring)) #convert string to bytes object, then to byte array

	#write byte array (bfile contents) to binary file
	with open(BINARY_RANGE_FNAME, "wb") as f:
		f.write(bfile_contents)

def random_ipv4str():
	#random location
	fsize_bytes = os.path.getsize(BINARY_RANGE_FNAME)
	num_terminal_pairs = fsize_bytes//(BYTES_IN_IP*2)
	location_byte_number = random.randrange(0, num_terminal_pairs + 2, 2)

	#read binary file at chose byte location
	with open(BINARY_RANGE_FNAME, 'rb') as f:
		f.seek( location_byte_number * BYTES_IN_IP, 1 )						#skip to chosen location in file
		#print (f.read( BYTES_IN_IP * 2 )) 									#read in two terminals
		term1_hexstr = f.read( BYTES_IN_IP )
		term2_hexstr = f.read( BYTES_IN_IP )


		#turn hex raw strings to original decimal values. randrange value between them then convert to ipv4 format
		term1_int10 = hexstr_2_int10(term1_hexstr)
		term2_int10 = hexstr_2_int10(term2_hexstr)
		rand_ip_int10 = random.randrange(term1_int10, term2_int10)
		return dec_ip_2_ip(rand_ip_int10)
