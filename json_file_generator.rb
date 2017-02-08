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

@cmd = "ps -ef|
        grep -E 'httpd|java|apache'|
        cut -d ' ' -f1|
        sort -u|
        grep -v [0-9]|
        grep -v root|
        xargs -i sudo su - {} -c 'echo whoami$(whoami)' "
@username = 'sa_rmtmgmt'
@app_counter = 0
@clear_file = 0
f = File.open(options[:host])

f.each do |hostname|
  hostname = hostname.gsub("\n", '')
  if @clear_file == 0
    File.open(hostname + '.json', 'w') { |file| file.truncate(0) }
    @clear_file << 1
  end
  begin
    @app_counter = 0
    @brackets = 0
    username = []
    startapp = []
    stopapp = []
    verifyapp = []
    puts hostname
    ssh = Net::SSH.start(hostname, 'sa_rmtmgmt')
    res = ssh.exec!(@cmd)
    res = res.split("\n")
    res.each do |i|
      username = username.push(i.gsub('whoami', '')) if i =~ /whoami/
      startapp = startapp.push(i.split(/\s\s/)[0]) if i !~ /restart/ &&
                                                      i !~ /chkapplog/ &&
                                                      i !~ /chklog/ &&
                                                      i !~ /large/ &&
                                                      i !~ /\*/ &&
                                                      i !~ /stopped/ &&
                                                      i =~ /start/
      stopapp = stopapp.push(i.split(/\s\s/)[0]) if i =~ /stop/
    end
    ssh.close
  rescue
    puts ''
  end
  File.open(hostname + '.json', 'a') { |file| file.puts('{') }
  File.open(hostname + '.json', 'a') { |file| file.puts('   "apps":[') }
  username.each do |i|
    begin
      break if stopapp[@app_counter].nil? || stopapp[@app_counter].empty?
      puts i
      if stopapp[@app_counter] != 'apachestop' && stopapp[@app_counter] != 'apache_stop'
        File.open(hostname + '.json', 'a') do |file|
          file.puts('      {')
        end
        File.open(hostname + '.json', 'a') do |file|
          file.puts('         "cmdtype": "menu",')
        end
        File.open(hostname + '.json', 'a') do |file|
          file.puts('         "appuser": "' + i + '"'',')
        end
        puts stopapp[@app_counter]
        stopappmenu = stopapp[@app_counter]
        stopappmenu = stopappmenu.rstrip
        File.open(hostname + '.json', 'a') do |file|
          file.puts('         "stop": "' + stopappmenu + '"'',')
        end
        puts startapp[@app_counter]
        startappmenu = startapp[@app_counter]
        startappmenu = startappmenu.rstrip
        File.open(hostname + '.json', 'a') do |file|
          file.puts('         "start":"' + startappmenu + '"'',')
        end
        #add a comma if the json file still needs to be populated
        #To do so I'm saying (if app_counter is not equal to the
        #size of the array) keep adding a comma, else if the app
        #counter is equal to the size of the erray dont add a
        #comma.
        File.open(hostname + '.json', 'a') do |file|
          file.puts('      }') if @app_counter == username.size
        end
        File.open(hostname + '.json', 'a') do |file|
          file.puts('      },') if @app_counter != username.size
        end
      end
      if stopapp[@app_counter] == 'apachestop' || stopapp[@app_counter] == 'apache_stop'
        puts '      {"cmdtype":"init","service":"httpd"},'
        File.open(hostname + '.json', 'a') do |file|
          file.puts('      {"cmdtype":"init","service":"httpd"}')\
          if @app_counter != username.size
        end
        File.open(hostname + '.json', 'a') do |file|
          file.puts('      {"cmdtype":"init","service":"httpd"},')\
          if @app_counter == username.size
        end
      end
      @app_counter += 1
    rescue
      puts 'No Menu Availible'
    end
  end
  File.open(hostname + '.json', 'a') { |file| file.puts('    ]') }
  File.open(hostname + '.json', 'a') { |file| file.puts('}') }
  File.open(hostname + '.json').close
end
