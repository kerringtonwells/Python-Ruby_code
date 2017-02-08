import subprocess


def change_release_knife(host):
    cmd = "knife_change_release_date.py -recent -f " + host
    output = subprocess.Popen(cmd,
                              shell=True,
                              stdout=subprocess.PIPE)
    output.wait()
    output = output.stdout.read()
    return output

