#!/usr/bin/env python
import sys, getopt, json, urllib
import ip_location_data as iploc
"""
  cmdl use:
  ip/location app

  app  [-h] [-v] [-p] [-n] [infile] [outfile]

  -h : help
  -p : (csv output) format: country_name, percentage
  -n : (csv output) format: country_name, percentage (normalized by IANA blocks)
  -v : use fill country names instead of abreviation
"""

#set program name
program_name = sys.argv[0]

def main(argv):

  #command line options

  #flags
  VERBOSE = False
  NORM = False
  PIE = False

  #params
  infile = None
  outfile = None
  cap = None

  #correct usage msg
  correct_usage_str = "usage:\t" + program_name + " [-h] [-v] [-p] [-n] [infile] [outfile] [opt:cap]\n\t-h:help,\t-v:use full country name,\t-p:export as pie percentage,\t-p: normilized pie on IANA country blocks\t-[cap]:number exported to pie csv) "

  #try retrieve arguments
  try:
     opts, args = getopt.getopt(argv,"hvpnc",["help", "verbose", "pie", "norm", "infile=", "outfile="])

     if not (len(args) == 2 or len(args) == 3):
        print ("ERROR" + correct_usage_str)
        sys.exit(2)

     infile = args[0]
     outfile = args[1]

     if len(args) == 3:
      cap = int(args[2])

  except getopt.GetoptError:
     print ("ERROR" + correct_usage_str)
     sys.exit(2)

  for opt, arg in opts:
     if opt == '-h':
        print ("Help -- \n" + correct_usage_str)
        sys.exit()

     elif opt in ("-v", "--verbose") and infile is not None and outfile is not None:
        #print ("--verbose: full country name" % (infile, outfile))
        VERBOSE = True

     elif opt in ("-n", "--pie norm") and infile is not None and outfile is not None:
        #print ("iplist: %s --> countrylist: %s (pie chart csv normalized)" % (infile, outfile))
        PIE = True
        NORM = True

     elif opt in ("-p", "--pie") and infile is not None and outfile is not None:
        #print ("iplist: %s --> countrylist: %s (pie chart csv)" % (infile, outfile))
        PIE = True
     else:
        print ("ERROR" + correct_usage_str)
        sys.exit() 

  #run program
  if PIE == False:
    print ("iplist: %s --> countrylist: %s \nverbose set to %s" % (infile, outfile, VERBOSE))
    iploc.iplist_to_countrylist(infile, outfile, VERBOSE)
  else: 
    print ("iplist: %s --> countrylist: %s \n(pie chart csv)\nverbose set to %s\nnormalize set to %s, cap is set to %s" % (infile, outfile, VERBOSE, NORM, cap))
    iploc.iplist_to_piecsv(infile,outfile, VERBOSE, NORM, cap)



#runs main method when the document is loaded
#passes all command line args neglecting 0th (name of file)
if __name__ == "__main__":
   main(sys.argv[1:])
