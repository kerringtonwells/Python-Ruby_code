import subprocess

def get_patch_cycle(host):
    output = ""
    get_patch_cycle_cmd = "knife node show %s -a patchcycle" % (host)
    output = subprocess.Popen(get_patch_cycle_cmd.split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    output = output.stdout.read()
    return output
