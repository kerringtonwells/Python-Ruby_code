#
#  Written by Kerrington Wells 2016
#
#

"""Script parses sanlun lun output and returns output in csv format."""
import re
import sys


arr = []
alias = []
lunid = []
lsize = []
wwid = []
file = open(str(sys.argv[1]))
for line in file:
        line = line.rstrip()
        if re.search('ONTAP', line):
                ontap_placeholder = line.rsplit('/')[-1]
                ontap_placeholder = ontap_placeholder.rsplit('.')[0]
                ontap_placeholder = ontap_placeholder.split(',')
                alias.append(ontap_placeholder)
        if re.search('LUN:', line):
                lun = line.rsplit(':')[1]
                lunid.append(lun)
        if re.search('LUN Size:', line):
                lun_size = line.rsplit(':')[1]
                lun_size = lun_size.replace("g", "")
                lun_size = lun_size.rsplit('.')[0]
                lsize.append(lun_size)
        if re.search('Host Device', line):
                if re.search('36006', line)is None:
                        host_device = line[line.find("(") + 1:line.find(")")]
                        wwid.append(host_device)
for a, b, c, d in zip(alias, lunid, lsize, wwid):
        a = str(a)
        a = a[a.find("[") + 1:line.find("]")]
        a = a[a.find("'") + 1:line.find("'")]
        a = ''.join(a)
        b = ''.join(b)
        a = a.replace(" ", "")
        a = re.sub(r'\s+', '', a)
        b = re.sub(r'\s+', '', b)
        c = re.sub(r'\s+', '', c)
        d = re.sub(r'\s+', '', d)
        print(a + "," + b + "," + c + "," + d + ",oracle,dba")
