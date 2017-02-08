"""Script that checks application status post patch."""
import multiprocessing
import subprocess
import json
import signal
import re


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


post_patch = []


def host_health_after_patch(host):
    """Get host count after patch."""
    count = 0
    host = host.replace("\n", "")
    host = host.replace("None", "")
    cmd = "curl -l https://dash.ihg.com/api/ipsoft/hostStatus.php?hosts=%s.ihg" % (host)
    output = subprocess.Popen(cmd.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output.wait()
    output = output.stdout.read()
    parsed = json.loads(output)
    p_out = json.dumps(parsed, indent=4, sort_keys=True)
    for line in p_out.splitlines():
        if ('OK' in line) or ('WARN' in line) or ('CRIT' in line) or ('UNKNOWN' in line) or ('PENDING' in line): # noqa
            line = line.split(':',1)[1]
            line = line.split(',',1)[0]
            line = int(line)
            count += line
        elif 'No hosts found matching your query' in line:
            count = 0
    node = host + "'s active monitors: " + str(count)
    return node
