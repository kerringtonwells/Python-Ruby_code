# Written by Kerrington Wells 
import cherrypy
import random
import string
import subprocess

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080,
                       })


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"

    @cherrypy.expose
    def redhat6(self):
        cmd = "python /root/repo_changelog.py -year 2016 -month Jan"
        output = subprocess.Popen(cmd,
                                  shell=True,
                                  stdout=subprocess.PIPE)
        output = output.stdout.read()
        return output


    @cherrypy.expose
    def generate(self):
        return ''.join(random.sample(string.hexdigits, 8))


if __name__ == '__main__':
    cherrypy.quickstart(StringGenerator())

