#python 3

import csv
import struct
import json
import sys
import socket
import re

"""
	
				 country ranges fast lookup
				(ipv4 address to country name)

	-finds gcd of all country range enpoints
	-use unit step function of size gcd to compute table (table contains y value of unit step function and assosiated country block)
	-loads table values into ram and uses unit step function to compute assosiated country of given ip
"""

#resources
COUNTRY_RANGES_FNAME = "iana_ip_ranges/ipv4_country_masks.csv"

#settings
DEFAULT_VALUE = "Other"

#return greatest common denominator of two numbers
def gcd (a,b):
    if (b == 0):
        return a
    else:
         return gcd (b, a % b)

#return greatest common denominator of a list of numbers
def gcd_list(list):
	res = list[0]
	for c in list[1::]:
	    res = gcd(res , c)
	return res

#converts ipv4to decimal number
def ip_2_dec(ip):
	packedIP = socket.inet_aton(ip)
	return struct.unpack("!L", packedIP)[0]


# read in ips from file and return array
def read_ip_list(ip_list_fname):
	try:
		with open(ip_list_fname) as f: ips = f.readlines()

		#regex expression for extracting IPv4 from line
		ip_extract_re = re.compile(r'\D*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
		return [ip_extract_re.match(l).group(1) for l in ips if (ip_extract_re.match(l) is not None)]

	except Exception as e:	
		print (e)
		sys.exit("error opening file")

#extract all iana country blocks {term_1:, term_2:, country_name:}
def iana_country_blocks():
	all_blocks = []
	with open(COUNTRY_RANGES_FNAME, mode='r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			block = {}
			block['term_1'] = int(row[0])
			block['term_2'] = int(row[1])
			block['country_name'] = row[3]
			all_blocks.append(block)
	return all_blocks

#set global GCD and global lookup table
def create_global_lookup_table():
	global GCD
	global lookup_table

	all_blocks = iana_country_blocks()
	terminals_1 = [b['term_1'] for b in all_blocks]
	terminals_2 = [b['term_2'] for b in all_blocks]

	GCD = gcd_list(terminals_1)

	#build, constant time, memory hog, lookup table
	lookup_table = [DEFAULT_VALUE] * ( int(terminals_2[-1]/GCD) + 1 )
	for block in all_blocks:
		lookup_table[int(block['term_1']/GCD)] = block['country_name']

		low = int(block['term_1']//GCD)
		high = int( -(-block['term_2'])//GCD) + 1

		#fill slots between terminals
		n = high - low
		for i in range(n):
			lookup_table[low+(i)] = block['country_name']

def ip_to_country(ip_string):
	global lookup_table
	global GCD

	dec_ip = ip_2_dec(ip_string)
	return lookup_table[dec_ip//GCD]

#global for constant time speed up
lookup_table = []
GCD = -1

def main(args=None):

	if (len(sys.argv) != 3):	sys.exit()
	infile = sys.argv[1]
	outfile = sys.argv[2]

	#load lookup table into ram
	create_global_lookup_table()

	#load ip list
	ips = read_ip_list(infile)

	#look up start
	countries = [ip_to_country(ip) for ip in ips]

	#write ip list
	with open(outfile, mode='w+') as f:
		for i in range(0, len(ips)):
			f.write("%s,%s\n" % (countries[i], ips[i]))
#
#	run program
#

if __name__ == "__main__":
	main()

