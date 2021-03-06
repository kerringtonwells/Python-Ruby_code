#!/usr/bin/python
import cherrypy
from cherrypy.lib.httputil import parse_query_string
import random
import string
import subprocess
from repo_changelog import *
import re
import os

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080,
                        'server.thread_pool' : 8,
                        'server.max_request_body_size' : 100,
                       })



class Root:

    @cherrypy.expose
    def index(self):
             return """<html>
              <head>
                <title>RPM Changelog</title>
                <link rel="stylesheet" type="text/css" href="images/start_cherry_py.css">
              </head>
              <body>
                <div class="maxl">
                  <img src="images/IHG-group.jpg" alt="IHG" style="width:954px;height:112px;">
                  <h2>Rpm Changelog Dashboard</h2>
		  <form method="get" action="redhat6">
		    <label class="radio inline"> 
		      <input type="radio" name="month" value="Jan" checked>
		      <span>Jan </span> 
		    </label>
		    <label class="radio inline"> 
		      <input type="radio" name="month" value="Feb">
		      <span>Feb </span>
		    </label>
		    <label class="radio inline">
		      <input type="radio" name="month" value="Mar">
		      <span>Mar </span>
		    </label>
		    <label class="radio inline"> 
		      <input type="radio" name="month" value="Apr">
		      <span>Apr </span> 
		    </label>
		    <label class="radio inline"> 
		      <input type="radio" name="month" value="May">
		      <span>May </span>
		    </label>
		    <label class="radio inline">
		      <input type="radio" name="month" value="Jun">
		      <span>Jun </span>
		    </label>
		    <label class="radio inline"> 
		      <input type="radio" name="month" value="Jul">
		      <span>Jul </span> 
		    </label>
		    <label class="radio inline"> 
		      <input type="radio" name="month" value="Aug">
		      <span>Aug </span>
		    </label>
		    <label class="radio inline">
		      <input type="radio" name="month" value="Sep">
		      <span>Sep </span>
		    </label>
		    <label class="radio inline"> 
	              <input type="radio" name="month" value="Oct">
	              <span>Oct </span> 
		    </label>
		    <label class="radio inline"> 
		      <input type="radio" name="month" value="Nov">
		      <span>Nov </span>
		    </label>
		    <label class="radio inline">
		      <input type="radio" name="month" value="Dec">
		      <span>Dec </span>
		    </label>
                    <div>
                      <label class="radio inline">
                        <input type="radio" name="repo" value="eus">
                        <span>Eus </span>
                      </label>
                      <label class="radio inline">
                        <input type="radio" name="repo" value="redhat6" checked>
                        <span>Redhat6 </span>
                      </label>
                      <label class="radio inline">
                        <input type="radio" name="repo" value="optional">
                        <span>Optional </span>
                      </label>
                      <label class="radio inline">
                        <input type="radio" name="repo" value="dts">
                        <span>Dts </span>
                      </label>
                      <label class="radio inline">
                        <input type="radio" name="repo" value="dts2">
                        <span>Dts2 </span>
                      </label>
                    </div>
		    <p><input class="textbox" type="text" value="Enter 4 digit year" name="year" /></p>
		    <p><button class="submit" type="submit">Submit</button></p>
	          </form>
                </div>
              </body>
            </html>"""

    @cherrypy.expose
    def generate(self, length=8):
        return ''.join(random.sample(string.hexdigits, int(length)))

    @cherrypy.expose
    def redhat6(self, month, year, repo):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        def content():
            parse_query_string(cherrypy.request.query_string)
            if repo == "redhat6":
                red_hat_6_rpm_list_path = "/local/pulp/published/yum/master/yum_distributor/ihg-redhat-6Server-x86_64-" + release.get_current_release() + "/*"
                red_hat_6_rpm_list = repo_list.get_repo_list("ls " + red_hat_6_rpm_list_path)
            elif repo == "eus":
                red_hat_6_rpm_list_path = "/local/pulp/published/yum/master/yum_distributor/ihg-redhat-6Server-eus-x86_64-" + release.get_current_release() + "/*"
                red_hat_6_rpm_list = repo_list.get_repo_list("ls " + red_hat_6_rpm_list_path)
            elif repo == "optional":
                red_hat_6_rpm_list_path = "/local/pulp/published/yum/master/yum_distributor/ihg-redhat-6Server-optional-x86_64-" + release.get_current_release() + "/*"
                red_hat_6_rpm_list = repo_list.get_repo_list("ls " + red_hat_6_rpm_list_path)
            elif repo == "dts":
                red_hat_6_rpm_list_path = "/local/pulp/published/yum/master/yum_distributor/ihg-redhat-6Server-dts-x86_64-" + release.get_current_release() + "/*"
                red_hat_6_rpm_list = repo_list.get_repo_list("ls " + red_hat_6_rpm_list_path)
            elif repo == "dts2":
                red_hat_6_rpm_list_path = "/local/pulp/published/yum/master/yum_distributor/ihg-redhat-6Server-dts2-x86_64-" + release.get_current_release() + "/*"
                red_hat_6_rpm_list = repo_list.get_repo_list("ls " + red_hat_6_rpm_list_path)
            yield " " * 1024
            yield "\n" 
            for i in red_hat_6_rpm_list:
                cmd = "rpm -qp --changelog " + red_hat_6_rpm_list_path + "/" + i
                print(cmd)
                output = subprocess.Popen(cmd,
                                          shell=True,
                                          stdout=subprocess.PIPE)
                output = output.stdout.read()
                if re.search(month +' \d\d ' + year, output):
                    output = re.split('\n\s*\n', output)
                    yield "-------------------------------------------------------------------------------\n"
                    yield i + "\n"
                    yield "-------------------------------------------------------------------------------\n"
                    for line in output:
                        if re.search(month +' \d\d ' + year, line):
                            yield line + "\n"
                else:
                    pass
        return content()
    redhat6._cp_config = {'response.stream': True}

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    conf = {'/images': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(current_dir, 'images'),}}
    cherrypy.quickstart(Root(), '/', config=conf)

