#!/opt/chef/embedded/bin/ruby

require 'rubygems'
require 'net/ssh'
require 'fileutils'
options = {}
OptionParser.new do |opts|
  opts.banner = 'Usage: example.rb [options]'
  opts.on('-f', '--Host File', 'Host File') { |value| options[:host] = value }
end.parse!
initd_list = ["apigee-message-processor", "apigee-router", "apigee-management-server", "apigee-ui", "apigee-slapd", "apigee-qpidd", "ccps", "dlq", "growth", "guest", "guest-nonatp", "httpd", "mvsd-gnp", "mvsd-taf", "none", "offer", "order", "partner","tcserver", "pnc-booking", "reimbursement", "rules", "scuap-tcserver", "static", "stay-realtime", "tcServer", "tcserver-ccoap", "tcserver-cflap", "tcserver-comap", "tcserver-evsap", "tcserver-gcaap", "tcserver-gcsap", "tcserver-gcuap", "tcserver-gnrap", "tcserver-gsyap", "tcserver-initate", "tcserver-iosap", "tcserver-mkpap", "tcserver-orap", "tcserver-orsap", "tcserver-rflap", "tcserver-stpap", "tomcat", "wind-dashboard"]

#check if nodes are public cloud nodes

#If the file already contains -nat in it remove it first
#This avoids errors and confusion later in the script

 File.open(options[:host], 'r') do |f1|
   while line = f1.gets
     if line.match(/^VA1/)
       File.open(options[:host] + '.tmp', 'a') do |file|
          file.puts(line.gsub '-nat','')
       end
     end
   end
 end

 if File.file?(options[:host] + '.tmp')
   FileUtils.mv(options[:host] + '.tmp', options[:host])
 end

File.open(options[:host], 'r') do |f1|
  while line = f1.gets
    if line.match(/^VA1/)
      File.open(options[:host] + '.tmp', 'a') do |file|
         file.puts(line.sub '.','-nat.')
      end
    end
  end
end

if File.file?(options[:host] + '.tmp')
  FileUtils.mv(options[:host] + '.tmp', options[:host])
end

@cmd = "ls -l /etc/rc3.d/| awk '{print $9}'|sed 's/^...//'"
@username = 'sa_rmtmgmt'
f = File.open(options[:host])
f.each do |hostname|
  application = String.new
  hostname = hostname.gsub("\n", '')
  begin
    puts hostname
    ssh = Net::SSH.start(hostname, 'sa_rmtmgmt')
    res = ssh.exec!(@cmd)
    res = res.split("\n")
    ssh.close
    if hostname.include? '-nat'
      hostname = hostname.gsub("-nat", '')
    end

    #Create attributes based on the order is the node results
    #I get the start up order by running ls -l on /etc/rc3.d

    res.each do |i|
      if initd_list.include? i
        application << i + " "
      end
    end
    node_attributes = httpd = "knife node attribute set " + hostname + " services ""'" + application + "'"
    system node_attributes
    get_node_attributes = httpd = "knife node attribute get " + hostname + " services "
    system get_node_attributes
  rescue
    puts ''
  end
end

#Removeing -nat from last file
 File.open(options[:host], 'r') do |f1|
   while line = f1.gets
     if line.match(/^VA1/)
       File.open(options[:host] + '.tmp', 'a') do |file|
          file.puts(line.gsub '-nat','')
       end
     end
   end
 end
 if File.file?(options[:host] + '.tmp')
   FileUtils.mv(options[:host] + '.tmp', options[:host])
 end

File.open(options[:host]).close

