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


def downtime_monitor(host):
    ipsoft_mon_counter = 0
    ampersand = "&"
    host = host.replace("\n", "")
    host = host.replace("None", "")
    cmd = "curl -sL https://dash.ihg.com/api/ipsoft/hostDowntimeUptime.php?hosts=%s%saction=downtime%sduration=100" % (host,ampersand,ampersand) # noqa
    output = subprocess.Popen(cmd.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output = output.stdout.read()
    if ("rrors" in output) or ("Undefined variable:" in output) or ("Trying to get property of non-object" in output):
        value = host + ":" + Bcolors.OKGREEN + ' Is not being monitored ' + Bcolors.ENDC
    else:
        value = host + ":" + Bcolors.OKGREEN + ' Has been Downtimed ' + Bcolors.ENDC
    return value

