#python 3

import csv
import struct
import json
import sys
import socket
import re

"""

	ip/location app

	app  [-h] [-p] [-n] [-v] [infile] [outfile]

	-h : help
	-p : (csv output) format: country_name, percentage
		-n : normalized by IANA blocks
	-v : use fill country names instead of abreviation
	
	---------------------------------------------------------------------------------------------------------------
	method:
				 country ranges fast lookup
				(ipv4 address to country name)

	-finds gcd of all country range enpoints
	-use unit step function of size gcd to compute table (table contains y value of unit step function and assosiated country block)
	-loads table values into ram and uses unit step function to compute assosiated country of given ip
	---------------------------------------------------------------------------------------------------------------


"""

#resources
COUNTRY_RANGES_FNAME = "iana_ip_ranges/ipv4_country_masks.csv"

#settings
DEFAULT_VALUE = "Other"
DEFAULT_PIE_CAP = 11

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

#strip country name of comma
def strip_country_name(country_name):
	try: return country_name.split(',')[0]
	except: return country_name

#find all country block range for a given country
def country_blocks(country):
	global all_blocks
	
	country_blocks = []
	for b in all_blocks:
		if b['country_name'] == country or b['country_abr'] == country:
			country_blocks.append(b)
	return country_blocks

#find total ips registerd for a country
def country_spaces(country):
	global all_blocks

	blocks = {}
	#total/specific country
	if country == "total": blocks = all_blocks
	else: blocks = country_blocks(country)

	spaces = 0
	for b in blocks:
		spaces += b['term_2'] - b['term_1']
	return spaces

#return ratio of country ipspace to total ip space for normalizing
def country_ratio(country):
	return country_spaces(country)/float(country_spaces("total"))

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
			block['country_abr'] = row[2]
			block['country_name'] = row[3]

			if (block['country_abr'] == '-' or block['country_name'] == '-'):
				block['country_abr'] = DEFAULT_VALUE
				block['country_name'] = DEFAULT_VALUE

			all_blocks.append(block)
	return all_blocks

#set global GCD and global lookup table
def create_global_lookup_table(fullname=False):
	global GCD
	global lookup_table
	global all_blocks

	all_blocks = iana_country_blocks()
	terminals_1 = [b['term_1'] for b in all_blocks]
	terminals_2 = [b['term_2'] for b in all_blocks]

	GCD = gcd_list(terminals_1)

	#build, constant time, memory hog, lookup table
	lookup_table = [DEFAULT_VALUE] * ( int(terminals_2[-1]/GCD) + 1 )
	if fullname == False:
		for block in all_blocks:
			lookup_table[int(block['term_1']/GCD)] = block['country_abr']

			low = int(block['term_1']//GCD)
			high = int( -(-block['term_2'])//GCD) + 1

			#fill slots between terminals
			n = high - low
			for i in range(n):
				lookup_table[low+(i)] = block['country_abr']
	else:
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

def iplist_to_countrylist(infile,outfile,fullname=False):
	#load lookup table into ram
	if fullname == False:	create_global_lookup_table()
	else: create_global_lookup_table(True)

	#load ip list
	ips = read_ip_list(infile)

	#look up start
	countries = [ip_to_country(ip) for ip in ips]

	#write ip list
	with open(outfile, mode='w+') as f:
		for i in range(0, len(ips)):
			f.write("%s,%s\n" % (countries[i], ips[i]))

def iplist_to_piecsv(infile,outfile,fullname=False, normalized=False, cap=DEFAULT_PIE_CAP):
	if cap == None: cap = DEFAULT_PIE_CAP

	#load lookup table into ram
	if fullname == False:	create_global_lookup_table()
	else: create_global_lookup_table(True)

	#load ip list
	ips = read_ip_list(infile)

	#country name breakdown

	countries_all_occurences = [ip_to_country(ip) for ip in ips]
	countries = set(countries_all_occurences)

	# count 
	countries_data = []
	for c in countries:
		country_data = {}
		country_data['country'] = c
		country_data['count'] = 0
		country_data['percentage'] = 0
		for x in countries_all_occurences:
			if x == c:
				country_data['count'] = country_data['count'] + 1
		countries_data.append(country_data)

	# perecentage
	for c in countries_data:
		if normalized == False:	c['percentage'] = c['count']/float(len(ips))
		else: c['percentage'] = c['count'] * country_ratio(c['country'])

		#tmp
		print ("c: country: %s count: %d, per: %f" % (c['country'], c['count'], c['percentage']))

	#sort by frequency (count/percentage)
	if normalized == False: countries_data = sorted(countries_data, key=lambda k: k['count'], reverse=True)
	else: countries_data = sorted(countries_data, key=lambda k: k['percentage'], reverse=True)

	# ( c['count'] * country_ratio(c['country']) ) 


	#
	#	Display
	#

	#number of elements to display
	num_elements = min(cap + 1, len(countries_data))

	#remaining = 1 - (sum of percentages in chart)
	sum = 0
	remaining = 0
	if normalized == False:
		sum = 0
		for i in range(num_elements):
			sum += countries_data[i]['percentage']
		remaining = 1-sum
	else:
		for i in range(num_elements,len(countries_data)):
			remaining += countries_data[i]['percentage']

	remaining_obj = {"country":"remaining", "percentage":remaining}
	countries_data.insert(0,remaining_obj)

	#export countries into pie_csv format for R script
	with open(outfile, mode='w+') as f:
		f.write("country,ratio")
		for i in range(num_elements):
			c = countries_data[i]
			f.write("\n%s,%f" % (strip_country_name(c['country']), c['percentage']))

#global for constant time speed up
lookup_table = []
GCD = -1
all_blocks = []

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

