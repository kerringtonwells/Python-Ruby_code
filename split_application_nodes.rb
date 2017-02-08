#
#  Written by Kerrington Wells 2016
#
#

require 'rubygems'
require 'net/ssh'
require 'pry'

 options = {}
 OptionParser.new do |opts|
   opts.banner = 'Usage: example.rb [options]'
   opts.on('-a', '--Create application list', 'application_list')\
     { |value| options[:application] = value }
 end.parse!
 business_application = options[:application]
@cmd = "knife search node 'name:" + business_application + "'|\
       grep -i 'Node Name:'|\
       awk '{print $3}' > application_list"
system(@cmd)
@count  = File.foreach('application_list').inject(0) { |c, _ln| c + 1 }
File.open('application_list').close

def patch_group(file_count)
  @patch_groups = 0.25 * file_count
  @patch_groups = @patch_groups.to_int
  return @patch_groups
end

def create_host_group(file)
  host_group = 1
  host_group = host_group.to_s
  line = 0
  File.open('patch_group_' + host_group, 'w') { |fn| fn.truncate(0) }
  File.foreach(file) do |fp|
    if line < patch_group(@count) && line < @count
      line += 1
      File.open('patch_group_' + host_group, 'a') do |fn|
        fn.puts(fp)
      end
    end
  end
  host_group_1 = File.foreach('patch_group_'\
    + host_group, 'a').inject(0) { |c, _ln| c + 1 }
  File.open('patch_group_1').close
end

def create_host_group2(file)
  host_group = 2
  host_group = host_group.to_s
  line_number = create_host_group('application_list')
  last_line = create_host_group('application_list') * 1.97
  line = 1
  File.open('patch_group_' + host_group, 'w') { |fn| fn.truncate(0) }
  File.foreach(file) do |fp|
    if line == line_number && line_number <= last_line
      line_number += 1
      File.open('patch_group_' + host_group, 'a') do |fn|
        fn.puts(fp)
      end
    end
    line += 1
  end
  line_number
end

def create_host_group3(file)
  host_group = 3
  host_group = host_group.to_s
  line_number = create_host_group2('application_list')
  last_line = create_host_group2('application_list')  * 1.49
  line = 1
  File.open('patch_group_' + host_group, 'w') { |fn| fn.truncate(0) }
  File.foreach(file) do |fp|
    if line == line_number && line_number <= last_line
      line_number += 1
      File.open('patch_group_' + host_group, 'a') do |fn|
        fn.puts(fp)
      end
    end
    line += 1
  end
  return line_number
end

def create_host_group4(file)
  host_group = 4
  host_group = host_group.to_s
  line_number = create_host_group3('application_list')
  last_line = create_host_group3('application_list') * 2
  line = 1
  File.open('patch_group_' + host_group, 'w') { |fn| fn.truncate(0) }
  File.foreach(file) do |fp|
    if line == line_number && line_number <= last_line
      line_number += 1
      File.open('patch_group_' + host_group, 'a') do |fn|
        fn.puts(fp)
      end
    end
    line += 1
  end
end

if @count == 1
  create_host_group('application_list')
elsif @count == 2
  create_host_group('application_list')
  create_host_group2('application_list')
else
  create_host_group('application_list')
  create_host_group2('application_list')
  create_host_group3('application_list')
  create_host_group4('application_list')
end

File.open('patch_group_1').close
File.open('patch_group_2').close
File.open('patch_group_3').close
File.open('patch_group_4').close

# remc3_1 = `/usr/bin/remc3_rundeck -H patch_group_1 'ls -ltrha'`
# puts remc3_1
# remc3_1 = remc3_1.split()
# remc3_1_count = remc3_1.index("Failed:") + 1
# remc3_1_failure_count = remc3_1[remc3_1_count]
# remc3_1_failure_count = remc3_1_failure_count.to_i
# @patch_group_1_count = File.foreach('patch_group_1').inject(0) { |c, _ln| c + 1 }
# failures_allowed = @patch_group_1_count * 0.1
# failures_allowed = failures_allowed.ceil
# if remc3_1_failure_count >= failures_allowed
#   puts ''
#   puts 'WARNING'
#   puts 'There were too many failures in patch_group_1 to continue.'
#   exit(0)
# else
#   remc3_2 = `/usr/bin/remc3_rundeck -H patch_group_2 'ls -ltrha'`
#   puts remc3_2
# end
# remc3_2 = remc3_2.split()
# remc3_2_count = remc3_2.index('Failed:') + 1
# remc3_2_failure_count = remc3_2[remc3_2_count]
# remc3_2_failure_count = remc3_2_failure_count.to_i
# @patch_group_2_count = File.foreach('patch_group_2').inject(0) { |c, _ln| c + 1 }
# failures_allowed = @patch_group_2_count * 0.1
# failures_allowed = failures_allowed.ceil
# if remc3_2_failure_count >= failures_allowed
#   puts ''
#   puts 'WARNING'
#   puts 'There were too many failures in patch_group_2 to continue.'
#   exit(0)
# else
#   remc3_3 = `/usr/bin/remc3_rundeck -H patch_group_3 'ls -ltrha'`
#   puts remc3_3
# end
# remc3_3 = remc3_3.split()
# remc3_3_count = remc3_3.index('Failed:') + 1
# remc3_3_failure_count = remc3_3[remc3_3_count]
# remc3_3_failure_count = remc3_3_failure_count.to_i
# @patch_group_3_count = File.foreach('patch_group_3').inject(0) { |c, _ln| c + 1 }
# failures_allowed = @patch_group_3_count * 0.1
# failures_allowed = failures_allowed.ceil
# if remc3_3_failure_count >= failures_allowed
#   puts ''
#   puts 'WARNING'
#   puts 'There were too many failures in patch_group_3 to continue.'
#   exit(0)
# else
#   remc3_4 = `/usr/bin/remc3_rundeck -H patch_group_4 'ls -ltrha'`
#   puts remc3_4
# end
