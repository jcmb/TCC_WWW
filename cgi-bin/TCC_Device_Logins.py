#! /usr/bin/env python
import json
import time
import calendar
from collections import defaultdict
from pprint import pprint
import urllib2
from cookielib import CookieJar
import sys
from datetime import datetime, timedelta, date
import cgi
import cgitb; cgitb.enable() # Optional; for debugging only


current_time=datetime.now()

f=sys.stdout
print "content-type: text/html"
print ""

f.write ("<!DOCTYPE html>\n")

"""
if (len(sys.argv)<>4 and len(sys.argv)<>5):
   sys.stderr.write("TCC_Device_Logins.py User Org Password [Active Time]\n")
   sys.stderr.write("\n")
   sys.stderr.write("Active Time is How long ago did the device login to be active\n")
   sys.stderr.write("   5min\n")
   sys.stderr.write("   Hour\n")
   sys.stderr.write("   Today\n")
   sys.stderr.write("   MTD\n")
   sys.stderr.write("   30Days\n")
   sys.stderr.write("   YTD\n")
   sys.stderr.write("   All (Default)\n")
   sys.stderr.write("\n")
   quit(1)

User=sys.argv[1]
Org=sys.argv[2].title()
Password=sys.argv[3]

if len(sys.argv) == 4 :
   Report_Type = "All"
else:
    Report_Type=sys.argv[4]
"""
arguments = cgi.FieldStorage()

User=arguments["USER"].value
Org=arguments["USER_ORG"].value.title()
Password=arguments["PASS"].value
Report_Type=arguments["ACTIVE"].value

if Report_Type == "5min":
    time_cutoff=current_time-timedelta(minutes=6) #Allow for the reporting time
elif Report_Type == "Hour":
    time_cutoff=current_time-timedelta(minutes=61) #Allow for the reporting time
elif Report_Type == "Today":
    time_cutoff=current_time.replace(hour=1,minute=0)
elif Report_Type == "24Hour":
    time_cutoff=current_time-timedelta(minutes=60*24+1) #Allow for the reporting time
elif  Report_Type == "MTD":
    time_cutoff=current_time.replace(day=1)
elif Report_Type == "30Day":
    time_cutoff=current_time-timedelta(days=30)
elif Report_Type == "YTD":
    time_cutoff=current_time.replace(day=1,month=1)
elif Report_Type == "All":
    time_cutoff=datetime(2010,1,1,0,0)
else:
    f.write("Error: Unknown Active Type: {0}\n".format(Report_Type))
    quit(1)


f.write ("<html><head><title>{0} devices</title>\n".format(Org))
f.write ('<meta http-equiv="refresh" content="60">')
f.write("""<link rel="stylesheet" type="text/css" href="/css/tcui-styles.css">
</head>
<body class="page">
<div class="container clearfix">
  <div style="padding: 10px 10px 10px 0 ;"> <a href="http://construction.trimble.com/">
        <img src="/images/trimble-logo.jpg" alt="Trimble Logo" id="logo"> </a>
      </div>
  <!-- end #logo-area -->
</div>
<div id="top-header-trim"></div>
<div id="content-area">
<div id="content">
<div id="main-content" class="clearfix">
""")

f.write ('<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>'+"\n")
f.write ('<script src="/jquery.tablesorter.min.js"></script>'+"\n")
f.write ('<link rel="stylesheet" type="text/css" href="/css/style.css"></link>'+"\n")
f.write ('<script>'+"\n")
f.write ('$(document).ready(function()'+"\n")
f.write ('{'+"\n")
f.write ('    $("#Devices").tablesorter({sortList:[[4,1]],dateFormat:"yyyy-mm-dd hh:mm:ss"});'+"\n")
f.write ('    }'+"\n")
f.write (');'+"\n")
f.write ('</script>'+"\n")



#success=True
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#print "Logging In"
try:
   data=opener.open("https://www.myconnectedsite.com/tcc/login\?username="+User+"&orgname="+Org+"&password="+Password+"&applicationkey=grk_user_login")
except:
    f.write("Error: Could not login, check password\n".format(Report_Type))
    quit(2)

#print (data.read())
json_login = json.load(data)
success=json_login["success"]

if success:
#   print "Logged in"
   pass
else :
   print "Failed to log in"
   quit(1)

#print "Getting device information"
data=opener.open("https://www.myconnectedsite.com/tcc/getdevices")
#print data.read()
json_total = json.load(data)

success=json_total["success"]
devices=json_total["devices"]

if not success:
   print "Failed to get  devices"

#print "Organizations: {}, Member Count: {}".format(totalorganizationcount,totalmembercount)
#print "Total Device Count: {0}".format(len(devices))

Devices_Never_Active=defaultdict(int)
Devices_Active=defaultdict(int)
Devices_Inactive=defaultdict(int)
DevicesInOrg=defaultdict(int)


#f=open("{}.{}.html".format("Devices",Org),"w")

f.write ('<TABLE BORDER=1  id="Devices" class="tablesorter">')
f.write ("<caption><b>{0}</b></caption><thead><tr><th>Device</th><th>Description</th><th>Status</th><th>Login Method</th><th>Login Time</th></tr></thead>\n".format(Org))
f.write ("<tbody>\n")

for device in devices:
    orgName=device["orgName"].title()
    if orgName== Org:
        deviceName=device["shortname"].upper()
        description=device["description"]
        DevicesInOrg[deviceName]+=1
#        pprint (device)
        if device["lastLoginMethod"]==None :
           Devices_Never_Active[deviceName]+=1
           f.write ("<tr><TD>{0}</TD><TD>{1}</TD><TD>{2}</TD><TD>{3}</TD><TD>{4}</TD></tr>\n".format(deviceName,description,"Never Active","",""))
        else :
           Login_Time=datetime.strptime(device["lastLoginTime"],"%Y-%m-%d %H:%M:%S.%f")
           Login=device["lastLoginMethod"].upper()

           if Login_Time >= time_cutoff:
               Devices_Active[deviceName]+=1
               f.write ("<tr><TD>{0}</TD><TD>{1}</TD><TD>{2}</TD><TD>{3}</TD><TD>{4}</TD></tr>\n".format(deviceName,description,"Active",Login,Login_Time.strftime("%Y-%m-%d %H:%M:%S")))
           else :
               Devices_Inactive[deviceName]+=1
               f.write ("<tr><TD>{0}</TD><TD>{1}</TD><TD>{2}</TD><TD>{3}</TD><TD>{4}</TD></tr>\n".format(deviceName,description,"Inactive",Login,Login_Time.strftime("%Y-%m-%d %H:%M:%S")))

f.write ("</tbody>\n")
f.write ("</table>\n")
f.write ("<p/>\n")

#print "Organization Device Count: {}".format(len(DevicesInOrg))


f.write ("<table border=\"1\"><caption><b>{0}</b></caption><tr><th>Item</th><th>Count</th></tr>\n".format(Org))
f.write ("<tr><td>{0}</td><td>{1}</td></tr>\n".format("Total",len(DevicesInOrg)))
f.write ("<tr><td>{0}</td><td>{1}</td></tr>\n".format("Active",len(Devices_Active)))
f.write ("<tr><td>{0}</td><td>{1}</td></tr>\n".format("Inactive ("+Report_Type+")" ,len(Devices_Inactive)))
f.write ("<tr><td>{0}</td><td>{1}</td></tr>\n".format("Never",len(Devices_Never_Active)))
f.write ("</table>\n")
f.write ("<p/>\n")
f.write ("Generated at: {0}\n".format(current_time.strftime("%Y-%m-%d %H:%M:%S")))
f.write ("</body>\n")
f.close
