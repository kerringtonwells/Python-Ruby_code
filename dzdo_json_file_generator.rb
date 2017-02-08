#
#  Written by Kerrington Wells 2016
#
#

require 'rubygems'
require 'net/ssh'

options = {}
OptionParser.new do |opts|
  opts.banner = 'Usage: example.rb [options]'
  opts.on('-f', '--Host File', 'Host File') { |value| options[:host] = value }
end.parse!

@cmd = "dzdo ls -tlhra /etc/init.d/ |rev| awk '{print $1}'|rev"
@username = 'sa_rmtmgmt'
@app_counter = 0
@clear_file = 0
f = File.open(options[:host])

f.each do |hostname|
  hostname = hostname.gsub("\n", '')
  begin
    application = []
    puts hostname
    ssh = Net::SSH.start(hostname, 'sa_rmtmgmt')
    res = ssh.exec!(@cmd)
    res = res.split("\n")
    res.each do |i|
      application = application.push(i.split(/\s\s/)[0]) if i == "httpd" ||
                                                            i == "tcserver\?"
    end
    ssh.close
    puts application
  rescue
    puts ''
  end
end
