#!/usr/bin/python

import sys
import getopt
from datetime import datetime, timedelta

opts, args = getopt.getopt(sys.argv[1:], 'l:z')

for opt, arg in opts:
	if opt == '-l':
		print "lunch time : 30 min"
		
mon = float(sys.argv[1])
tue = float(sys.argv[2])
wed = float(sys.argv[3])
thu = float(sys.argv[4])
st_h = int(sys.argv[5])
st_m = int(sys.argv[6])

exit_time = 40 - (mon + tue + wed + thu)

ex_h = (exit_time // 1)
ex_m = (exit_time % 1)

print "%s is remain time" % exit_time
print "%d:%d is the time that you would be able to exit office" % (ex_h,ex_m)

