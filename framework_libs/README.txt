Version: 1.14

Kerrington Wells: 11/29/2016
    Fixed issue with concatinating strings and integers in patch_fremework_compare.

Kerrington Wells: 11/21/2016
    Added apigee services to set_node_attributes.rb script. 

Kerrington Wells: 11/21/2016
    Created compare script that compares counts pre and post patch. Added apigee scritps to set_node_attributes.rb initd_list

Kerrington Wells: 11/15/2016
    Added functionality to knife_change_release_date.py that changes release date if the current date is set to the 15th.

Kerrington Wells: 11/15/2016
    Removed wait from os.system commands. 

Kerrington Wells: 11/14/2016
    Fixed uptime downtime bug. Nodes that are not being monitored where printing that they'd been downtimed or uptime. 

Kerrington Wells: 11/14/2016
    Adding OK's Criticals, Warnings and pendings as a cumilative number instead of just OK's (from status) Made corrections to remote ctl output and uptime downtime api calls.

Kerrington Wells: 11/14/2016
    Added failure Threshhold flage to patch_framework.

Kerrington Wells: 11/10/2015
    Add Multiprocessing to change Relase date. 

Kerrington Wells: 11/9/2016
    Added Multiprocessing to the downtime uptime and patchcycle portions of the script.

Kerrington Wells: 11/8/2016
    Added tcserver back to set_node_attributes array, removed retry logic for IP soft for testing purposes. Added mulprocessing to ipsof's status and downtime. 

Kerrington Wells: 10/25/2016
    Added retry logic when ipsoft status returns null or an empty string.

Kerrington Wells: 10/24/2016
    Fixed bug that caused framework to fail with index out of bounds exception. Removed status check as php api is already the status of the api call.

Kerrington Wells: 10/17/2016
    Added functionality to patch_framework.py that allows users to patch using 1 patch group (100%). Added she bang to knife_change_release_date.py script. Broke out post patch function, created python module that runs the post patch check function.

