# 2016
# Written By Kerrington Wells
require 'open3'
hostname = `hostname -f`
def save_health_count(hostname)
  cmd = 'curl -l https://dash.ihg.com/api/ipsoft/hostDowntimeUptime.php?hosts=' + hostname + '\\&action=downtime\\&duration=100'
  cmd = cmd.gsub("\n","")
  puts cmd
  stdout, stdeerr, status = Open3.capture3(cmd)
  output = stdout
  puts output
  if output.include? 'rrors' or output.include? 'Undefined variable:' or  output.include? 'Trying to get property of non-object'
    puts 'THIS NODE IS WAS NOT DOWNTIMED'
  else
    puts 'HOST HAS BEEN DOWNTIMED.'
  end
  cmd = 'curl -l https://dash.ihg.com/api/ipsoft/hostStatus.php?hosts=' + hostname  + '.ihg'
  cmd = cmd.gsub("\n","")
  stdout, stdeerr, status = Open3.capture3(cmd)
  output = stdout
  output = output.split(/,/)
  total = 0
  output.each do |x|
    if x.include? "OK"
      x = x.gsub! /"OK":/, ''
      total += x.to_i
    end
  end
  File.open('/var/log/node_health', 'w') { |file| file.write(total) }
  total
end

save_health_count(hostname)
