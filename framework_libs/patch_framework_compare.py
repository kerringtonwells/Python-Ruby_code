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


def compare_health(before, after, hosts):
    iterator = 0
    for host in hosts:
        host = host.replace("\n", "")
        host = host.replace("None", "")
        if int(before[iterator]) <= int(after[iterator]):
            print(host + ":" + Bcolors.OKGREEN +
                  " Post patch health check application count: " +
                  str(after[iterator]) + Bcolors.ENDC)
            pass
        else:
            print(host + ":" + Bcolors.FAIL + " Pre patch count: " +
                  str(before[iterator]) +
                  " Post patch count: " +
                  str(after[iterator]) +
                  Bcolors.ENDC)
            pass
        iterator += 1
    # return output
