#!/usr/bin/python
"""Knife script that runs knife commands automatically."""
import os
import datetime
import argparse
import subprocess


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


now = datetime.datetime.now()
current_date = now.strftime("%Y%m%d")
patch_date = now.strftime("%Y%m15")
checkJan = now.strftime("%m")
checkJan = int(checkJan)


def recent_release_date():
    recent_release_date = now.strftime("%Y%m15")
    recent_release_date = int(recent_release_date)
    recent_release_date = str(recent_release_date)
    return recent_release_date

def jan_exception():
    december = now.strftime("%Y")
    december = int(december)
    december = december - 1
    current_date = now.strftime("1215")
    current_date = int(current_date)
    current_date = int(str(december) + str(current_date))
    current_date = str(current_date)
    return current_date

def last_months_release():
    last_months_release_date = now.strftime("%Y%m15")
    last_months_release_date = int(last_months_release_date)
    last_months_release_date -= 100
    last_months_release_date = str(last_months_release_date)
    return last_months_release_date

parser = argparse.ArgumentParser(
    description='Change release date on a list of nodes')
parser.add_argument(
    '-f',
    '--file_with_hosts',
    help='USAGE: python knife_change_releasedate.py -f <FILENAME>',
    required=True)
parser.add_argument(
    '-last',
    '--last_months_release_date',
    action='store_true',
    help='Use last months release USAGE: python knife_change_releasedate.py\
          -f <FILENAME> -s',
    required=False)
parser.add_argument(
    '-recent',
    '--this_months_release',
    action='store_true',
    help='Use the most recent release date USAGE: python knife_change_releasedate.py\
          -f <FILENAME> -r',
    required=False)
parser.add_argument(
    '-info',
    '--patch_info',
    action='store_true',
    help='Get current relese date USAGE: python knife_change_releasedate.py\
          -f <FILENAME> -info',
    required=False)
args = parser.parse_args()

host_file = args.file_with_hosts

i  = host_file

if args.patch_info:
    command = "knife node show " + i + " -a patchcycle"
    os.system(command)
    command = "knife node show " + i + " -a releasedate"
    os.system(command)
    exit()

if args.this_months_release:
    if current_date >= patch_date:
        recent_release_date()
        output = ""
        command = "knife node attribute set " + i + \
            " releasedate " + recent_release_date()
        output = subprocess.Popen(command.split(),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        output = output.stdout.read()
        print(i + ":" + Bcolors.OKGREEN +
              " Release date has been set to " +
              recent_release_date() + Bcolors.ENDC)
        exit()
    else:
        print(Bcolors.WARNING + "This months release has not come out yet. Using last months" + Bcolors.ENDC) # noqa
        command = "knife node attribute set " + i + \
            " releasedate " + last_months_release()
        output = subprocess.Popen(command.split(),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        output = output.stdout.read()
        print(i + ":" + Bcolors.OKGREEN +
              " Release date has been set to " +
              last_months_release() + Bcolors.ENDC)
        exit()
if args.last_months_release_date:
    if checkJan == 1:
        jan_exception()
        output = ""
        command = "knife node attribute set " + i + " releasedate\
                  " + jan_exception()
        output = subprocess.Popen(command.split(),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        output = output.stdout.read()
        print(i + ":" + Bcolors.OKGREEN +
              " Release date has been set to " +
              jan_exception() + Bcolors.ENDC)
        exit()
    else:
        last_months_release()
        output = ""
        command = "knife node attribute set " + i + \
            " releasedate " + last_months_release()
        output = subprocess.Popen(command.split(),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        output = output.stdout.read()
        print(i + ":" + Bcolors.OKGREEN +
              " Release date has been set to " +
              last_months_release() + Bcolors.ENDC)
        exit()

if args.last_months_release_date is False and args.this_months_release\
   is False and args.patch_info is False:
    print(Bcolors.FAIL + "You did not specify which release date to use! Use\
          ' python knife_change_releasedate.py -h ' for help" +
          Bcolors.ENDC)

