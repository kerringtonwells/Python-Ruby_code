import subprocess

def get_ipsoft_api_status(host):
    """Get the status of IP-Softs api."""
    host = host.replace("\n", "")
    cmd = "curl -I https://dash.ihg.com/api/ipsoft/" \
          "hostStatus.php?hosts=%s*" % (host)
    output = subprocess.Popen(cmd.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output = output.stdout.read()
    return output

