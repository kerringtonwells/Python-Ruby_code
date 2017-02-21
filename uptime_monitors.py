#!/usr/bin/python
import subprocess
import argparse
import signal 
import multiprocessing 

parser = argparse.ArgumentParser(
    description='Create application list')
parser.add_argument(
    '-file',
    '--file_name',
    help='USAGE: uptime_monitors.py -file <filename> ',
    required=True)
args = parser.parse_args()

with open(args.file_name) as f:
    hosts = f.readlines()


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


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


def uptime_monitor(host):
    ampersand = "&"
    host = host.replace("\n", "")
    host = host.replace("None", "")
    cmd = "curl -sL host.php?hosts=%s%saction=uptime%sduration=100" % (host,ampersand,ampersand) # noqa
    output = subprocess.Popen(cmd.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output = output.stdout.read()
    if ("rrors" in output) or ("Undefined variable:" in output) or ("Trying to get property of non-object" in output):
        value = host + ":" + Bcolors.OKGREEN + ' Is not being monitored ' + Bcolors.ENDC
    else:
        value = host + ":" + Bcolors.OKGREEN + ' Has been uptimed ' + Bcolors.ENDC
    return value

pool = multiprocessing.Pool(6, init_worker)

try:
    for i in pool.imap(uptime_monitor, hosts):
        print(i) 
except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        exit(0)

