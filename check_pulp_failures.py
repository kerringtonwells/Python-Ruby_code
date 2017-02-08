#
#  Written by Kerrington Wells 2016
#
#

"""Check /var/log/messages for pulp failures."""
import os
import datetime
now = datetime.datetime.now()
current_date = now.strftime("%Y%m%d")
month = (now.strftime("%B"))
month = month[0] + month[1] + month[2]
day = now.strftime("%d")
day = str(day)
if day == "01":
    day = " 1"
if day == "02":
    day = " 2"
if day == "03":
    day = " 3"
if day == "04":
    day = " 4"
if day == "05":
    day = " 5"
if day == "06":
    day = " 6"
if day == "07":
    day = " 7"
if day == "08":
    day = " 8"
if day == "09":
    day = " 9"
month_day = month + " " + day
with open("/var/log/messages") as f:
    messages = f.readlines()
pulp_log = open("pulp_error_log_" + current_date + ".txt", "w")
pulp_log.truncate()
pulp_log.close()
email = 'echo See the attached document.  | mailx -s "PULP ERRORS" -a \
        "pulp_error_log_"' + current_date + '".txt" "Kerrington.Wells@ihg.com,\
         Benjie.Godfrey@ihg.com,\
         Birendra.Singh@ihg.com"'
for message in messages:
    if month_day in message and ("pulp") in message and ("ERROR") in message:
        print(message)
        message.count("pulp")
        with open("pulp_error_log_" + current_date + ".txt", "a") as myfile:
            myfile.write(message)
if os.stat("pulp_error_log_" + current_date + ".txt").st_size == 0:
    pass
else:
    os.system(email)
