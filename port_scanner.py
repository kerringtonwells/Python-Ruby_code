#
#  Written by Kerrington Wells 2016
#
#

"""Port Scanner. Allows users to scan ports on remove systems."""
import subprocess
import argparse
import socket
import os
parser = argparse.ArgumentParser(description='Log into a\
                                              list of nodes and run netstat\
                                              -tunlp|grep <ports and\
                                              services you specify\
                                              in a file>')
parser.add_argument('-hostfile',
                    '--hostnamefile',
                    help='Use -n to load file with hostnames',
                    required=True)
parser.add_argument('-portfile',
                    '--port_service_file',
                    help='use -s to load a file\
                          containing ports\
                          or service names',
                    required=True)
args = parser.parse_args()
hosts = args.hostnamefile
content = args.port_service_file
os.system("sort -u " + args.port_service_file + " -o " +
          args.port_service_file)
os.system("sort -u " +
          args.hostnamefile + " -o " + args.hostnamefile)
os.system("sed -i '/^\s*$/d' " +
          args.port_service_file + " " + args.port_service_file)
os.system("sed -i '/^\s*$/d' " + args.hostnamefile + " " + args.hostnamefile)
with open(content) as f:
    content = f.readlines()
with open(hosts) as z:
    hosts = z.readlines()
result = []
for host in hosts:
    host = host.replace("\n", "")
    result.append(host)
    s = socket.socket(socket.AF_INET,
                      socket.SOCK_STREAM)
    try:
        s.connect((host, 22))
    except socket.error as e:
        print(host, "Error on connect: %s" % e)
    for i in content:
        command = "sudo netstat -tunlp|grep -i  " + i
        ssh = subprocess.Popen(["ssh",
                               "%s" % host,
                                command],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result.append(ssh.stdout.readlines())
    s.close()
result = list(result)
result = ','.join(str(v) for v in result)
result = result.replace("[", " ")
result = result.replace("]", " ")
result = result.replace("\\n", " ")
result = result.replace("'", " ")
print(result.replace(",", "\n"))
