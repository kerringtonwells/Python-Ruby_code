#!/usr/bin/python
"""Retrive changelog data and compare this months releases to last months."""
import datetime
import subprocess
import re
import argparse

month = "Jan"
year = "2016"

class ReleaseDate:
    """Get this months and last months release date."""

    def __init__(self):
        """Get date object."""
        self.now = datetime.datetime.now()
        self.current_date = self.now.strftime("%Y%m%d")
        self.patch_date = self.now.strftime("%Y%m15")
        self.checkJan = self.now.strftime("%m")
        self.checkJan = int(self.checkJan)

    def get_current_release(self):
        """Return this months release date."""
        if self.checkJan == 1:
            if int(self.now.strftime("%d")) < 15:
                recent_release_date = self.now.strftime("%12%m15")
                recent_release_date = int(recent_release_date)
                recent_release_date = str(recent_release_date)
            else:
                recent_release_date = self.now.strftime("%Y%m15")
                recent_release_date = int(recent_release_date)
                recent_release_date = str(recent_release_date)
        if int(self.now.strftime("%d")) < 15:
            recent_release_date = self.now.strftime("%Y%m15")
            recent_release_date = int(recent_release_date)
            recent_release_date -= 100
            recent_release_date = str(recent_release_date)
        else:
            recent_release_date = self.now.strftime("%Y%m15")
            recent_release_date = int(recent_release_date)
            recent_release_date = str(recent_release_date)
        return recent_release_date

    def get_last_relesae(self):
        """Return last months release date."""
        if self.checkJan == 1:
            if int(self.now.strftime("%d")) < 15:
                last_months_release_date = self.now.strftime("%11%m15")
                last_months_release_date = int(last_months_release_date)
                last_months_release_date = str(last_months_release_date)
            else:
                last_months_release_date = self.now.strftime("%12%m15")
                last_months_release_date = int(last_months_release_date)
                last_months_release_date = str(last_months_release_date)
        if self.checkJan == 2:
            if int(self.now.strftime("%d")) < 15:
                last_months_release_date = self.now.strftime("%12%m15")
                last_months_release_date = int(last_months_release_date)
                last_months_release_date = str(last_months_release_date)
            else:
                last_months_release_date = self.now.strftime("%Y%m15")
                last_months_release_date = int(last_months_release_date)
                last_months_release_date -= 100
                last_months_release_date = str(last_months_release_date)
        if int(self.now.strftime("%d")) < 15:
            last_months_release_date = self.now.strftime("%Y%m15")
            last_months_release_date = int(last_months_release_date)
            last_months_release_date -= 200
            last_months_release_date = str(last_months_release_date)
        else:
            last_months_release_date = self.now.strftime("%Y%m15")
            last_months_release_date = int(last_months_release_date)
            last_months_release_date -= 100
            last_months_release_date = str(last_months_release_date)
        return last_months_release_date


class RepoList:
    """Get repolist."""

    def __init__(self):
        release_date = None
        self.release_date = release_date

    def get_repo_list(self, cmd):
        repo_array = []
        output = subprocess.Popen(cmd,
                                  shell=True,
                                  stdout=subprocess.PIPE)
        output = output.stdout.read()
        output = output.split()
        for i in output:
            if ".rpm" in i:
                repo_array.append(i)
        return repo_array

    def get_change_log(self, rpm_list, path):
        for i in rpm_list:
            cmd = "rpm -qp --changelog %s%s" % (path, i)
            output = subprocess.Popen(cmd,
                                      shell=True,
                                      stdout=subprocess.PIPE)
            output = output.stdout.read()
            if re.search(month +' \d\d ' + year, output):
                output = re.split('\n\s*\n', output)
                print("<br>")
                print("-------------------------------------------------------------------------------<br>") # noqa
                print(i)
                print("<br>")
                print("-------------------------------------------------------------------------------<br>") # noqa
                for line in output:
                    if re.search(month +' \d\d ' + year, line):
                        print("<br>")
                        line = line.replace("\n", "<p>")
                        print(line)
                        print("<br>")
            else:
                pass

release = ReleaseDate()
repo_list = RepoList()
