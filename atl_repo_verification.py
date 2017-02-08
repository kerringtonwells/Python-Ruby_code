#
#  Written by Kerrington Wells 2016
#
#

"""Script that verify's client repos are in sync with the master repo."""
import subprocess
import datetime
import os

now = datetime.datetime.now()
patch_date = now.strftime("%Y%m15")
current_date = now.strftime("%Y%m%d")

email = 'echo See the attached document.  | mailx -s "atl Pulp Repo not in sync" -a \
        "atl_pulp_repo"' + current_date + '".txt" "Kerrington.Wells@ihg.com,\
         Benjie.Godfrey@ihg.com,\
         Birendra.Singh@ihg.com"'

rh_6_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-6Server-x86_64-" + patch_date + "/" # noqa
rh_6_dts_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-6Server-dts-x86_64-" + patch_date + "/" # noqa
rh_6_dts2_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-6Server-dts2-x86_64-" + patch_date + "/" # noqa
rh_6_eus_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-6Server-eus-x86_64-" + patch_date + "/" # noqa
rh_6_optional_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-6Server-optional-x86_64-" + patch_date + "/" # noqa
rh_5_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-5Server-x86_64-" + patch_date + "/" # noqa
rh_5_dts_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-5Server-dts-x86_64-" + patch_date + "/" # noqa
rh_5_dts2_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-5Server-dts2-x86_64-" + patch_date + "/" # noqa
rh_5_eus_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-redhat-5Server-eus-x86_64-" + patch_date + "/" # noqa
ihg_misc_5_i386_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-misc-5-i386/" # noqa
ihg_misc_5_x86_64_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-misc-5-x86_64/" # noqa
ihg_misc_6_x86_64_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-misc-6-x86_64/" # noqa
ihg_misc_master_cmd = "lynx -dump -listonly\
    http://iadd1pli05rp001.ihgint.global/pulp/repos/ihg-misc/" # noqa
# atl pulp repos
rh_6_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-6Server-x86_64-" + patch_date + "/" # noqa
rh_6_dts_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-6Server-dts-x86_64-" + patch_date + "/" # noqa
rh_6_dts2_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-6Server-dts2-x86_64-" + patch_date + "/" # noqa
rh_6_eus_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-6Server-eus-x86_64-" + patch_date + "/" # noqa
rh_6_optional_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-6Server-optional-x86_64-" + patch_date + "/" # noqa
rh_5_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-5Server-x86_64-" + patch_date + "/" # noqa
rh_5_dts_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-5Server-dts-x86_64-" + patch_date + "/" # noqa
rh_5_dts2_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-5Server-dts2-x86_64-" + patch_date + "/" # noqa
rh_5_eus_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-redhat-5Server-eus-x86_64-" + patch_date + "/" # noqa
ihg_misc_5_i386_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-misc-5-i386/" # noqa
ihg_misc_5_x86_64_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-misc-5-x86_64/" # noqa
ihg_misc_6_x86_64_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-misc-6-x86_64/" # noqa
ihg_misc_atl_cmd = "lynx -dump -listonly\
   http://atld1pli05rp001.hiw.com/pulp/repos/ihg-misc/" # noqa


def call_repo(repo_link):
    """Return repo contents in a string given the repo link."""
    output = subprocess.Popen(repo_link.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    repo = []
    diff = ""
    repo = output.stdout.read()
    repo = repo.split("\n")
    for rpms in repo:
        diff += rpms.rsplit('/')[-1]
        diff += "\n"
    return diff

if call_repo(rh_6_master_cmd) == call_repo(rh_6_atl_cmd):
    print("atl's Red Hat 6 repo is in sync")
else:
    print("WARNING:atl's Red Hat 6 repo is not in sync")
    message = "WARNING:atl's Red Hat 6 repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_6_dts_master_cmd) == call_repo(rh_6_dts_atl_cmd):
    print("atl's Red Hat 6 dts repo is in sync")
else:
    print("WARNING:atl's Red Hat 6 dts repo is not in sync")
    message = "WARNING:atl's Red Hat 6 dts repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_6_dts2_master_cmd) == call_repo(rh_6_dts2_atl_cmd):
    print("atl's Red Hat 6 dts2 repo is in sync")
else:
    print("WARNING:atl's Red Hat 6 dts2 repo is not in sync")
    message = "WARNING:atl's Red Hat 6 dts2 repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_6_eus_master_cmd) == call_repo(rh_6_eus_atl_cmd):
    print("atl's Red Hat 6 eus repo is in sync")
else:
    print("WARNING:atl's Red Hat 6 eus repo is not in sync")
    message = "WARNING:atl's Red Hat 6 eus repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_6_optional_master_cmd) == call_repo(rh_6_optional_atl_cmd):
    print("atl's Red Hat 6 optional repo is in sync")
else:
    print("WARNING:atl's Red Hat 6 optional repo is not in sync")
    message = "WARNING:atl's Red Hat 6 optional repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_5_master_cmd) == call_repo(rh_5_atl_cmd):
    print("atl's Red Hat 5 repo is in sync")
else:
    print("WARNING:atl's Red Hat 5 repo is not in sync")
    message = "WARNING:atl's Red Hat 5 repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_5_dts_master_cmd) == call_repo(rh_5_dts_atl_cmd):
    print("atl's Red Hat 5 dts repo is in sync")
else:
    print("WARNING:atl's Red Hat 5 dts repo is not in sync")
    message = "WARNING:atl's Red Hat 5 dts repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_5_dts2_master_cmd) == call_repo(rh_5_dts2_atl_cmd):
    print("atl's Red Hat 5 dts2 repo is in sync")
else:
    print("WARNING:atl's Red Hat 5 dts2 repo is not in sync")
    message = "WARNING:atl's Red Hat 5 dts2 repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(rh_5_eus_master_cmd) == call_repo(rh_5_eus_atl_cmd):
    print("atl's Red Hat 5 eus repo is in sync")
else:
    print("WARNING:atl's Red Hat 5 eus repo is not in sync")
    message = "WARNING:atl's Red Hat 5 eus repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(ihg_misc_5_i386_master_cmd) == call_repo(ihg_misc_5_i386_atl_cmd):
    print("atl's IHG Misc 5 i386 repo is in sync")
else:
    print("WARNING:atl's IHG Misc 5 i386 repo is not in sync")
    message = "WARNING:atl's IHG Misc 5 i386 repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(ihg_misc_5_x86_64_master_cmd) == call_repo(ihg_misc_5_x86_64_atl_cmd): # noqa
    print("atl's IHG Misc 5 x86 64 repo is in sync")
else:
    print("WARNING:atl's IHG Misc 5 x86 64 repo is not in sync")
    message = "WARNING:atl's IHG Misc 5 x86 64 repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(ihg_misc_6_x86_64_master_cmd) == call_repo(ihg_misc_6_x86_64_atl_cmd): # noqa
    print("atl's IHG Misc 6 x86 64 repo is in sync")
else:
    print("WARNING:atl's IHG Misc 6 x86 64 repo is not in sync")
    message = "WARNING:atl's IHG Misc 6 x86 64 repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)
if call_repo(ihg_misc_master_cmd) == call_repo(ihg_misc_atl_cmd):
    print("atl's IHG Misc repo is in sync")
else:
    print("WARNING:atl's IHG Misc repo is not in sync")
    message = "WARNING:atl's IHG Misc repo is not in sync\n"
    with open("atl_pulp_repo" + current_date + ".txt", "a") as myfile:
        myfile.write(message)

if call_repo(rh_6_master_cmd) != call_repo(rh_6_atl_cmd)\
   or call_repo(rh_6_dts_master_cmd) != call_repo(rh_6_dts_atl_cmd)\
   or call_repo(rh_6_dts2_master_cmd) != call_repo(rh_6_dts2_atl_cmd)\
   or call_repo(rh_6_eus_master_cmd) != call_repo(rh_6_eus_atl_cmd)\
   or call_repo(rh_6_optional_master_cmd) != call_repo(rh_6_optional_atl_cmd)\
   or call_repo(rh_5_master_cmd) != call_repo(rh_5_atl_cmd)\
   or call_repo(rh_5_dts_master_cmd) != call_repo(rh_5_dts_atl_cmd)\
   or call_repo(rh_5_dts2_master_cmd) != call_repo(rh_5_dts2_atl_cmd)\
   or call_repo(rh_5_eus_master_cmd) != call_repo(rh_5_eus_atl_cmd)\
   or call_repo(ihg_misc_5_i386_master_cmd) != call_repo(ihg_misc_5_i386_atl_cmd)\
   or call_repo(ihg_misc_5_x86_64_master_cmd) != call_repo(ihg_misc_5_x86_64_atl_cmd)\
   or call_repo(ihg_misc_6_x86_64_master_cmd) != call_repo(ihg_misc_6_x86_64_atl_cmd)\
   or call_repo(ihg_misc_master_cmd) != call_repo(ihg_misc_atl_cmd):
    os.system(email)
