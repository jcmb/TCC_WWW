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
import cgitb; 

cgitb.enable() # Optional; for debugging only


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


#Type_Name is set only if we allow this for a delete of old devices

Never_Logged_In=False

#Never_Logged_In is True if we should delete the devices that have Never_Logged_In

if Report_Type == "5min":
    time_cutoff=current_time-timedelta(minutes=6) #Allow for the reporting time
    Type_Name=""
elif Report_Type == "Hour":
    time_cutoff=current_time-timedelta(minutes=61) #Allow for the reporting time
    Type_Name=""
elif Report_Type == "Today":
    time_cutoff=current_time.replace(hour=1,minute=0)
    Type_Name=""
elif Report_Type == "24Hour":
    time_cutoff=current_time-timedelta(minutes=60*24+1) #Allow for the reporting time
    Type_Name=""
elif  Report_Type == "MTD":
    time_cutoff=current_time.replace(day=1)
    Type_Name=""
elif Report_Type == "30Day":
    time_cutoff=current_time-timedelta(days=30)
    Type_Name="30 days"
elif Report_Type == "YTD":
    time_cutoff=current_time.replace(day=1,month=1)
    Type_Name=""
elif Report_Type == "Year":
    Type_Name="Year"
    time_cutoff=current_time-timedelta(days=366)
elif Report_Type == "All":
    Type_Name=""
    time_cutoff=datetime(2010,1,1,0,0)
elif Report_Type == "NO":
    Never_Logged_In=True
    Type_Name="Never Logged in"
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
   
accountid=json_login["accountid"]

#print "accountid", accountid
data=opener.open("https://www.myconnectedsite.com/tcc/GetLoginAccount?loginaccountid="+accountid)
#print data.read()
json_account_details = json.load(data)


devicemanager=json_account_details["data"]["devicemanager"]

if not devicemanager:
    f.write("Error: Account does not have rights to delete devices\n".format(Report_Type))
    quit(3)
  


#print "Getting device information"
data=opener.open("https://www.myconnectedsite.com/tcc/getdevices")
#print data.read()
json_total = json.load(data)

success=json_total["success"]
devices=json_total["devices"]

if not success:
   print "Failed to get  devices"


#pprint (devices)
#print "Organizations: {}, Member Count: {}".format(totalorganizationcount,totalmembercount)
#print "Total Device Count: {0}".format(len(devices))


#f=open("{}.{}.html".format("Devices",Org),"w")

f.write ('<TABLE BORDER=1  id="Devices" class="tablesorter">')
f.write ("<caption><b>{0}</b></caption><thead><tr><th>Device</th><th>Description</th><th>Login Time</th><th>Device ID</th><th>Deleted</th></tr></thead>\n".format(Org))
f.write ("<tbody>\n")

for device in devices:
    orgName=device["orgName"].title()
    if orgName== Org:
        deviceName=device["shortname"].upper()
        description=device["description"]
        deviceID=device["deviceid"]
#        pprint (device)
        if device["lastLoginMethod"]==None :
           if Never_Logged_In:
             f.write ("<tr><TD>{0}</TD><TD>{1}</TD><TD>{2}</TD><TD>{3}</TD>".format(deviceName,description,"Never Active",deviceID))
             
             data=opener.open("https://www.myconnectedsite.com/tcc/deletedevice?deviceid="+deviceID)
             json_delete = json.load(data)
             success=json_delete["success"]
             f.write ("<td>{}</td></tr>\n".format(success))
        else :
           if not Never_Logged_In:
             Login_Time=datetime.strptime(device["lastLoginTime"],"%Y-%m-%d %H:%M:%S.%f")
             if Login_Time < time_cutoff:
                 f.write ("<tr><TD>{0}</TD><TD>{1}</TD><TD>{2}</TD><TD>{3}</TD>\n".format(deviceName,description,"Inactive",deviceID))
                 data=opener.open("https://www.myconnectedsite.com/tcc/deletedevice?deviceid="+deviceID)
                 json_delete = json.load(data)
                 success=json_delete["success"]
                 f.write ("<td>{}</td></tr>\n".format(success))

f.write ("</tbody>\n")
f.write ("</table>\n")
f.write ("<p/>\n")

#print "Organization Device Count: {}".format(len(DevicesInOrg))

f.write ("<p/>\n")

f.write ("</body>\n")
f.close

