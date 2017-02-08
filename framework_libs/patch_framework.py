#!/usr/bin/python
#  Written by Kerrington Wells 2016
#
#  PROGRAM FLOW:
#
#  python patch_framwork.py
#  |
#   ---- Run "knife search node 'name:nodename' to generate node-list then splits node list into patch groups. # noqa
#  |
#   ---- change release date (Calling knife_change_releasedate.py)
#  |
#   ---- Down Time Monitors (Calling Ip-Soft Api from python)
#  |
#   ---- Get application health (Calling Ip-Soft Api from python)
#  |
#   ---- Set Service Attributes (Calling set_node_attributes.rb from python)
#  |
#   ---- Patch (calling remc3.sh from python)
#  |
#   ---- Get-uptime (Calling remc3.sh from python)
#  |
#   ---- Get patch Cycle (Running knife node show patchinfo from python)
#  |
#   ---- Get application health AFTER PATCHING(Calling Ip-softs api from python) # noqa
#  |
#   ---- Uptime Monitors (Calling Ip-soft api from python)


"""Generate application node list and split the nodes list."""
import argparse
import os
import math
import subprocess
import time
import os.path
import re
import json
import signal
from patch_framework_releasedate import change_release_knife
from patch_framework_patch_cycle import get_patch_cycle
from patch_framework_uptime import uptime_monitor
from patch_framework_downtime import downtime_monitor
from patch_framework_pre_health import host_health_before_patch
from patch_framework_post_health import *
from patch_framework_compare import compare_health

class Bcolors:
    """This class allows print to have colors."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[44m'
    WARNING = '\033[41m'
    FAIL = '\033[41m'
    ENDC = '\033[0m'

    def disable(self):
        """Disable colors once they have been used."""
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


parser = argparse.ArgumentParser(
    description='Create application list')
parser.add_argument(
    '-app',
    '--Get_application_list',
    help='USAGE: python split_application_nodes.py -a VA1IHGDWEB* ',
    required=False)
parser.add_argument(
    '-percentage',
    '--Percentage',
    help='USAGE: python split_application_nodes.py -a VA1IHGDWEB* -p 0.1',
    required=True)
parser.add_argument(
    '-file',
    '--file_name',
    help='USAGE: python split_application_nodes.py -a VA1IHGDWEB* -p 0.1',
    required=False)
parser.add_argument(
    '-threshold',
    '--failure_threshold',
    help='USAGE: python split_application_nodes.py -a VA1IHGDWEB* -p 0.1 -t .10',
    required=True)
args = parser.parse_args()

business_application = args.Get_application_list
patch_percentage = args.Percentage
user_filename = args.file_name
patch_percentage = float(patch_percentage)
failure_threshold = float(args.failure_threshold)
if patch_percentage == 0.25:
    pass
elif patch_percentage == 0.4:
    pass
elif patch_percentage == 0.1:
    pass
elif patch_percentage == 1:
    pass
else:
    print("Enter 0.1, 0.25 or 0.4")
    exit(0)

if failure_threshold > 1:
    print("Failure threshold percentage must be less than 1 (example .10)")
    exit(0)

if args.file_name is None:
    bus_app = business_application[:-1]
    cmd = "knife search node 'name:%s'|\
           grep -i 'Node Name:'|\
           awk '{print $3}' > App_%s_application_list" % (business_application,
                                                          bus_app)
    os.system(cmd)
elif args.Get_application_list is None:
    bus_app = user_filename
    cmd = "cp %s App_%s_application_list" % (bus_app, bus_app)
    os.system(cmd)
else:
    print("Please specify an Application group OR a Filename")
    print("Cannot specify both")
    exit(0)

with open("App_" + bus_app + "_application_list") as f:
    count = sum(1 for _ in f)

"""Remove stale application lists from preivious runs"""
remove_stale_files = "rm -rf App_%s_patch_group_*" % (bus_app)

os.system(remove_stale_files)

if count == 0:
    print("Query yeilded no results.")
    exit(0)

"""IMPORTANT. READ THIS.. Getting the patch groups to split evenly
is impossible for --low-- numbers.
By low numbers I mean anything less than 10.
So to solve this I create more groups instead of less groups.
For example,
lets take a 25 percent split. If you split 6 by 25 percent you get 1.5.
When python converts that to an int you get 1.
So the output in this case would be 6 patch groups not four. Whoevers
reading this may be asking, well why dont you just split the nodes
using the celiing of 1.5 which would be 2? If you split by
the celing when you have a
whole number you'll get a bug where you'll start skipping groups.
Since you jumpingto the celiing each time you'll start skipping lines
every now and then. So its better to go lower than higher."""


def patch_group(file_count):
    """Creating patch groups."""
    patch_groups = patch_percentage * file_count
    patch_groups = math.ceil(patch_groups)
    patch_groups = int(patch_groups)
    return patch_groups

"""The patch groups below will take the last line from the previous
patch groups and continue from the last_line of the previous group.
So lets say patch group 1
has 10 lines in the file, patch group two will take the return value of the
function from patch group 1 and continue from line 11."""


def create_host_group(file):
    """Create host group."""
    host_group = 1
    host_group = str(host_group)
    output = ""
    with open(file) as fp:
        for i, line in enumerate(fp):
            """For application lists less than 4"""
            if count <= 10:
                if i < patch_group(count) and i <= count:
                    output += line
                    text_file = open("App_" + bus_app +
                                     "_patch_group_" + host_group, "w")
                    text_file.write(output)
                    text_file.close()
            else:
                """For application lists greater than 3"""
                if i < patch_group(count) and i <= count:
                    output += line
                    text_file = open("App_" + bus_app +
                                     "_patch_group_" + host_group, "w")
                    text_file.write(output)
                    text_file.close()
    with open("App_" + bus_app + "_patch_group_1") as f:
        host_group_1 = sum(1 for _ in f)
    return host_group_1


def first_groups_last_line():
    """Returning first patch group count."""
    first_group_count = sum(1 for line in open('App_' +
                                               bus_app + '_patch_group_1'))
    return first_group_count


def create_host_group2(file):
    """Create host group."""
    host_group = 2
    host_group = str(host_group)
    output = ""
    line_number = create_host_group("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 2
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group3(file):
    """Create host group."""
    host_group = 3
    host_group = str(host_group)
    output = ""
    line_number = create_host_group2("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 3
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group4(file):
    """Create host group."""
    host_group = 4
    host_group = str(host_group)
    output = ""
    line_number = create_host_group3("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 4
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group5(file):
    """Create host group."""
    host_group = 5
    host_group = str(host_group)
    output = ""
    line_number = create_host_group4("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 5
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group6(file):
    """Create host group."""
    host_group = 6
    host_group = str(host_group)
    output = ""
    line_number = create_host_group5("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 6
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group7(file):
    """Create host group."""
    host_group = 7
    host_group = str(host_group)
    output = ""
    line_number = create_host_group6("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 7
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group8(file):
    """Create host group."""
    host_group = 8
    host_group = str(host_group)
    output = ""
    line_number = create_host_group7("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 8
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group9(file):
    """Create host group."""
    host_group = 9
    host_group = str(host_group)
    output = ""
    line_number = create_host_group8("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 9
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1
    return line_number


def create_host_group10(file):
    """Create host group."""
    host_group = 10
    host_group = str(host_group)
    output = ""
    line_number = create_host_group9("App_" + bus_app + "_application_list")
    last_line = first_groups_last_line() * 11
    with open(file) as fp:
        for i, line in enumerate(fp):
            if i == line_number and line_number < last_line:
                output += line
                text_file = open("App_" + bus_app +
                                 "_patch_group_" + host_group, "w")
                text_file.write(output)
                text_file.close()
                line_number += 1

"""Here I'm calling the patch group functions and closing
the files."""

try:
    create_host_group("App_" + bus_app + "_application_list")
    create_host_group2("App_" + bus_app + "_application_list")
    create_host_group3("App_" + bus_app + "_application_list")
    create_host_group4("App_" + bus_app + "_application_list")
    create_host_group5("App_" + bus_app + "_application_list")
    create_host_group6("App_" + bus_app + "_application_list")
    create_host_group7("App_" + bus_app + "_application_list")
    create_host_group8("App_" + bus_app + "_application_list")
    create_host_group9("App_" + bus_app + "_application_list")
    create_host_group10("App_" + bus_app + "_application_list")
    open('App_' + bus_app + '_patch_group_1').close
    open('App_' + bus_app + '_patch_group_2').close
    open('App_' + bus_app + '_patch_group_3').close
    open('App_' + bus_app + '_patch_group_4').close
    open('App_' + bus_app + '_patch_group_5').close
    open('App_' + bus_app + '_patch_group_6').close
    open('App_' + bus_app + '_patch_group_7').close
    open('App_' + bus_app + '_patch_group_8').close
    open('App_' + bus_app + '_patch_group_9').close
    open('App_' + bus_app + '_patch_group_10').close
except:
    pass

with open("App_" + bus_app + "_application_list") as f:
    hosts = f.readlines()
    hosts.sort()

pre_patch_success_uptime = 0
pre_patch_monitors = 0
pre_patch_success_health = 0
post_patch_success_health = 0
post_patch_success_uptime = 0
post_patch_monitors = 0
# Calling set_node_attribute.rb. This add node attributes to the nodes
# Rundeck output tends to run together. Adding sleep time in between functions.

print("")
print("---------------CREATING-NODE-ATTRIBUTES---------------")
print("")
cmd = "set_node_attributes.rb -f" + "App_" + bus_app + "_application_list" # noqa
output = subprocess.Popen(cmd,
                          shell=True,
                          stdout=subprocess.PIPE)
output = output.stdout.read()
print(output)


"""Calling the patch framework and passing each patch_group that
was generated"""


def change_release_date(hosts):
    pool = multiprocessing.Pool(6, init_worker)
    try:
        for i in pool.imap(change_release_knife, hosts):
            print(i)
            pass
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        exit(0)


# Get the availibility of the ipsoft api


# Downtime monitors and check availibility of ip softs api
def downtime_monitors(hosts):
    pool = multiprocessing.Pool(6, init_worker)
    try:
        for i in pool.imap(downtime_monitor, hosts):
            print(i)
            pass
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        exit(0)

# # Get Host Health before patch.
# # See how many applications are running before the patch.


def pre_patch_host_health_check(hosts):
    print("")
    print("---------------PRE-PATCH-HOST-HEALTH-CHECK---------------")
    print("")
    pre_patch_tmp = []
    pre_patch = []
    pool = multiprocessing.Pool(6, init_worker)
    try:
        for x in pool.imap(host_health_before_patch, hosts):
            pre_patch_tmp.append(x)
            print(Bcolors.OKGREEN + x + Bcolors.ENDC)
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        exit(0)
    pre_patch_tmp.sort()
    for i in pre_patch_tmp:
        i = i.split(':', 1)[1]
        pre_patch.append(int(i))
    return pre_patch


def post_patch_host_health_check(hosts):
    print("")
    print("---------------POST-PATCH-HOST-HEALTH-CHECK---------------")
    print("")
    post_patch_tmp = []
    post_patch = []
    pool = multiprocessing.Pool(6, init_worker)
    try:
        for x in pool.imap(host_health_after_patch, hosts):
            post_patch_tmp.append(x)
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        exit(0)
    post_patch_tmp.sort()
    for i in post_patch_tmp:
        i = i.split(':', 1)[1]
        post_patch.append(int(i))
    return post_patch

"""Calling the patch framework and passing each patch_group that
was generated"""


def patchcycle(hosts):
    pool = multiprocessing.Pool(6, init_worker)
    try:
        for i in pool.imap(get_patch_cycle, hosts):
            print(i)
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        exit(0)


def uptime(group):
    """Running uptime for each patch group."""
    print("")
    print("---------------CHECK-UPTIME---------------")
    print("")
    output = ""
    remotectl = "/usr/bin/remc3_rundeck -H %s uptime" % (group)
    output = subprocess.Popen(remotectl.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output = output.stdout.read()
    print(output)


def remotectl(group):
    """Running remotectl for each patch group."""
    output = ""
    remotectl = "/usr/bin/remc3_rundeck -H %s -c chefospatch" % (group)
    output = subprocess.Popen(remotectl.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output = output.stdout.read()
    return output


def uptime_monitors(host):
    pool = multiprocessing.Pool(6, init_worker)
    try:
        for i in pool.imap(uptime_monitor, host):
            print(i)
            pass
    except:
        pool.terminate()
        pool.join()
        exit(0)


print("")
print("")
print("------------------------------------------------------------------------GROUP 1------------------------------------------------------------------------")
print("")
print("")
with open("App_" + bus_app + "_patch_group_1") as f:
    hosts_1 = f.readlines()
    hosts_1.sort()
with open("App_" + bus_app + "_patch_group_1") as f:
    patch_group_1_count = sum(1 for _ in f)
pre_patch_list = pre_patch_host_health_check(hosts_1)
print("")
print("---------------SET-RELEASE-DATE---------------")
print("")
change_release_date(hosts_1)
print("")
print("---------------DOWNTIME-MONITOR---------------")
print("")
downtime_monitors(hosts_1)
print("")
print("---------------BEGIN-PATCHING-----------------")
print("")
remotectl_output = remotectl("App_" + bus_app + "_patch_group_1")
print(remotectl_output)
failed_nodes = 0
failure_rate = remotectl("App_" + bus_app + "_patch_group_1").split("\n")
for i in failure_rate:
    if re.search("Failed: ", i):
        failed_nodes = i.split(":")[1]
        failed_nodes = int(failed_nodes)
failures_allowed = int(patch_group_1_count) * failure_threshold
failures_allowed = int(math.ceil(failures_allowed))
print("Number of Failures allowed: " + str(failures_allowed))
if failed_nodes >= failures_allowed:
    print('')
    print('WARNING')
    print(failed_nodes)
    print('There are too many failures in patch_group_1 to continue.')
    exit(0)
elif patch_group_1_count == 0:
    exit(0)
else:
    pass
post_patch_list = post_patch_host_health_check(hosts_1)
compare_health(pre_patch_list, post_patch_list, hosts_1)
uptime("App_" + bus_app + "_patch_group_1")
print("")
print("---------------PATCHCYCLE---------------")
print("")
patchcycle(hosts_1)
print("")
print("---------------UPTIME-MONITORS---------------")
print("")
uptime_monitors(hosts_1)
if os.path.isfile("App_" + bus_app + "_patch_group_2"):
    if os.stat("App_" + bus_app + "_patch_group_2").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 2------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_2") as f:
            hosts_2 = f.readlines()
            hosts_2.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_2)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_2)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_2)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_2")
        with open("App_" + bus_app + "_patch_group_2") as f:
            patch_group_2_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_2").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_2_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_2 to continue.')
            exit(0)
        elif patch_group_2_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_2)
        compare_health(pre_patch_list, post_patch_list, hosts_2)
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_2)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_2)
if os.path.isfile("App_" + bus_app + "_patch_group_3"):
    if os.stat("App_" + bus_app + "_patch_group_3").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 3------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_3") as f:
            hosts_3 = f.readlines()
            hosts_3.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_3)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_3)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_3)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_3")
        with open("App_" + bus_app + "_patch_group_3") as f:
            patch_group_3_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_3").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_3_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_2 to continue.')
            exit(0)
        elif patch_group_3_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_3)
        compare_health(pre_patch_list, post_patch_list, hosts_3)
        uptime("App_" + bus_app + "_patch_group_3")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_3)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_3)
if os.path.isfile("App_" + bus_app + "_patch_group_4"):
    if os.stat("App_" + bus_app + "_patch_group_4").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 4------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_4") as f:
            hosts_4 = f.readlines()
            hosts_4.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_4)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_4)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_4)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_4")
        with open("App_" + bus_app + "_patch_group_4") as f:
            patch_group_4_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_4").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_4_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_4 to continue.')
            exit(0)
        elif patch_group_4_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_4)
        compare_health(pre_patch_list, post_patch_list, hosts_4)
        uptime("App_" + bus_app + "_patch_group_4")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_4)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_4)
if os.path.isfile("App_" + bus_app + "_patch_group_5"):
    if os.stat("App_" + bus_app + "_patch_group_5").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 5------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_5") as f:
            hosts_5 = f.readlines()
            hosts_5.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_5)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_5)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_5)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_5")
        with open("App_" + bus_app + "_patch_group_5") as f:
            patch_group_5_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_5").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_5_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_5 to continue.')
            exit(0)
        elif patch_group_5_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_5)
        compare_health(pre_patch_list, post_patch_list, hosts_5)
        uptime("App_" + bus_app + "_patch_group_5")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_5)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_5)
if os.path.isfile("App_" + bus_app + "_patch_group_6"):
    if os.stat("App_" + bus_app + "_patch_group_6").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 6------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_6") as f:
            hosts_6 = f.readlines()
            hosts_6.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_6)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_6)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_6)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_6")
        with open("App_" + bus_app + "_patch_group_6") as f:
            patch_group_6_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_6").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_6_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_6 to continue.')
            exit(0)
        elif patch_group_6_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_6)
        compare_health(pre_patch_list, post_patch_list, hosts_6)
        uptime("App_" + bus_app + "_patch_group_6")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_6)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_6)
if os.path.isfile("App_" + bus_app + "_patch_group_7"):
    if os.stat("App_" + bus_app + "_patch_group_7").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 7------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_7") as f:
            hosts_7 = f.readlines()
            hosts_7.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_7)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_7)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_7)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_7")
        with open("App_" + bus_app + "_patch_group_7") as f:
            patch_group_7_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_7").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_7_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_7 to continue.')
            exit(0)
        elif patch_group_7_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_7)
        compare_health(pre_patch_list, post_patch_list, hosts_7)
        uptime("App_" + bus_app + "_patch_group_7")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_7)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_7)
if os.path.isfile("App_" + bus_app + "_patch_group_8"):
    if os.stat("App_" + bus_app + "_patch_group_8").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 8------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_8") as f:
            hosts_8 = f.readlines()
            hosts_8.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_8)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_8)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_8)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_8")
        with open("App_" + bus_app + "_patch_group_8") as f:
            patch_group_8_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_8").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_8_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_8 to continue.')
            exit(0)
        elif patch_group_8_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_8)
        compare_health(pre_patch_list, post_patch_list, hosts_8)
        uptime("App_" + bus_app + "_patch_group_8")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_8)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_8)
if os.path.isfile("App_" + bus_app + "_patch_group_9"):
    if os.stat("App_" + bus_app + "_patch_group_9").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 9------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_9") as f:
            hosts_9 = f.readlines()
            hosts_9.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_9)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_9)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_9)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_9")
        with open("App_" + bus_app + "_patch_group_9") as f:
            patch_group_9_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_9").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_9_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_9 to continue.')
            exit(0)
        elif patch_group_9_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_9)
        compare_health(pre_patch_list, post_patch_list, hosts_9)
        uptime("App_" + bus_app + "_patch_group_9")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_9)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_9)
if os.path.isfile("App_" + bus_app + "_patch_group_10"):
    if os.stat("App_" + bus_app + "_patch_group_10").st_size == 0:
        pass
    else:
        print("")
        print("")
        print("------------------------------------------------------------------------GROUP 10------------------------------------------------------------------------")
        print("")
        print("")
        time.sleep(30)
        with open("App_" + bus_app + "_patch_group_10") as f:
            hosts_10 = f.readlines()
            hosts_10.sort()
        pre_patch_list = pre_patch_host_health_check(hosts_10)
        print("")
        print("---------------SET-RELEASE-DATE---------------")
        print("")
        change_release_date(hosts_10)
        print("")
        print("---------------DOWNTIME-MONITOR---------------")
        print("")
        downtime_monitors(hosts_10)
        print("")
        print("---------------BEGIN-PATCHING---------------")
        print("")
        remotectl_output = remotectl("App_" + bus_app + "_patch_group_10")
        with open("App_" + bus_app + "_patch_group_10") as f:
            patch_group_10_count = sum(1 for _ in f)
        print(remotectl_output)
        failed_nodes = 0
        failure_rate = remotectl("App_" + bus_app + "_patch_group_10").split("\n")
        for i in failure_rate:
            if re.search("Failed: ", i):
                failed_nodes = i.split(":")[1]
                failed_nodes = int(failed_nodes)
        failures_allowed = int(patch_group_10_count) * failure_threshold
        failures_allowed = int(math.ceil(failures_allowed))
        print("Number of Failures allowed: " + str(failures_allowed))
        if failed_nodes > failures_allowed:
            print('')
            print('WARNING')
            print(failed_nodes)
            print('There are too many failures in patch_group_10 to continue.')
            exit(0)
        elif patch_group_10_count == 0:
            exit(0)
        else:
            pass
        post_patch_list = post_patch_host_health_check(hosts_10)
        compare_health(pre_patch_list, post_patch_list, hosts_10)
        uptime("App_" + bus_app + "_patch_group_10")
        print("")
        print("---------------PATCHCYCLE---------------")
        print("")
        patchcycle(hosts_10)
        print("")
        print("---------------UPTIME-MONITORS---------------")
        print("")
        uptime_monitors(hosts_10)


