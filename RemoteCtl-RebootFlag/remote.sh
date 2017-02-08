#!/bin/bash
#
# Version: Feb 03, 2016
#
# Usage: remotectl [options] command
#       Builds query based upon the options
#               use knife search to list node names if no command given
#               use ssh (in parallel) to excute command at selected nodes
# options:
#  Chef search query options
#       --workgroup, -w <workgroup name>
#       --function, -f <function name>
#       --datacenter, -d <datacenter>
#       --environment, -e <chef environment>
#       --tags, -t <comm separated list of tags>
#       --nodes, -n <node name>
#       -a <String>       Arbitrary attribute query (Example: os:linux )
#       -N              [Experimental] Negate next query
#       -o             [Experimental] Next query option would be OR'ed
#                       (instead of default AND)
#   Host-list options
#       -h <space separated host names> Add hosts to list of hosts.
#       -H <file>               Add contents of file to list of hosts.
#
#   Actions
#       --command       command-set: one of predefined list of command
#                               ospatch
#       -r <recipe>     recipe: Cookbook::recipe format
#       -s <service>    service: OS service name
#       [command]       Arbitrary command if no recipe or service given
#                       service: start, stop, restart, status, reload
#                       recipe: ignored
#                       Hostname list if no command provided
# Misc options
#       -L login       Force use of 'login' name on all hosts.
#                       [Not yet implemented]
#       -q              No output unless necessary. (Summary report only)
#       -D              debug flag on
#       -m n            Run concurrently on 'n' hosts at a time (asynchronous).
#                        Use '0' (zero) for infinite. (default 20)

# -- For Debug --------------------
#PS4=':${LINENO}+'
#set -x
#DEBUG=2
#

source ./patch.sh
source ./ssh.sh

CONC=10
THECMD='uptime'
#-----------------------------------
#
# ^did not work investigate later
#
OPTLIST=":c:w:f:d:t:n:e:SRNoqDa:h:H:r:s:L:m:"

me=$(id -un|sed 's/admin_//')
fLogin=0
KQ=0
Negate=0
NextOR=0
Rboot=0
Query=""
HostList=()
declare -a harray
declare -A preDefCMDs
pCMD=
preDefCMDs=(
        [chefospatch]=chefospatch
        [ospatch]=ospatch
        [vospatch]=vospatch
)

listOnly=0 # 0: true, non-zero: false
TAGSUDO=1
TEMP_BASE=/var/tmp
TEMP_DIR=""
#TEMP_DIR=$(mktemp -d $TEMP_BASE/$(basename $0).XXXXXX) || exit 1

DEBUG=0
QUIET=0
SSH_ARGS="-o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no"
REMOTE_SHELL='bash'
runScript=0
Success=0
Failed=0
Active=0

create_temp() {
        MKTEMP=$(which mktemp 2>/dev/null)
        if [ -x "$MKTEMP" ] ; then
                [ "$DEBUG" -ge 2 ] && echo "DEBUG:${LINENO}: using mktemp ($MKTEMP)." 1>&2
                TEMP_DIR=$(mktemp -d $TEMP_BASE/$(basename $0).XXXXXX) || exit 1
        else
                [ "$DEBUG" -ge 2 ] && echo "DEBUG:${LINENO}: can't find mktemp... using alternate." 1>&2
                TEMP_DIR="$TEMP_BASE/$(basename $0).$(date +%s)"
                [ "$DEBUG" -ge 2 ] && echo "DEBUG:${LINENO}: Creating temp dir ($TEMP_DIR)." 1>&2
                if [ -e "$TEMP_DIR" ] ; then
                        echo "$0: Temp dir \"$TEMP_DIR\" already exists!" 1>&2
                        exit 1
                fi
                mkdir -m 700 $TEMP_DIR
        fi
}

destroy_temp() {
if [ $QUIET -ge 1 ] || [ $Failed -ge 1 ]; then
        echo "Review and delete Temp DIR $TEMP_DIR"
else
        if [ -d "$TEMP_DIR" ] ; then
                [ "$DEBUG" -ge 2 ] && echo "DEBUG:${LINENO}: Removing temp dir ($TEMP_DIR)." 1>&2
                rm -rf "$TEMP_DIR" 2>/dev/null
        fi
fi
}
#
#
Failrecord() {
        conout $1 "${@:2}"
        echo $1 >>$TEMP_DIR/Failed
        rm -f $TEMP_DIR/procs/$1 2>/dev/null
}

conout() {

        echo "${@:2}" | tee -a $TEMP_DIR/out/$1 |sed -e "s/^/$1: /"
}

Reboot() {
#    Reboot
        conout $Host "Rebooting ..."
        ssh -T $SSH_ARGS $uHost "$mSUDO -i reboot " 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        [ $? -ne 0 ] && { Failrecord $Host "Reboot command failed. aborting"; return 1; }
#    Wait in loop
        conout $Host "Waiting for reboot."
        loopcount=20; Noresponse=0; Rebooted=0
        while [ $loopcount -gt 0 ]; do
                (( loopcount-- ))
                sleep 15
                nUpt=$(ssh -T $SSH_ARGS $uHost "awk -F. '{print \$1}' /proc/uptime" 2>/dev/null)
#               conout $Host "uptime now is : $nUpt secs"
                if [ $? -ne 0 ]; then
                        Noresponse=1
                        conout $Host "Loopcount=$loopcount."
                        continue
                else
                        Noresponse=0
                        if [ "$nUpt" -gt "$sUpt" ]; then
                                conout $Host "Loopcount=$loopcount. uptime: $nUpt"
                                continue
                        else
                                Rebooted=1
                                conout $Host "System Reboot completed"
                                break
                        fi
                fi
        done
        if [ $Noresponse -eq 0 ] && [ $Rebooted -eq 0 ]; then
                Failrecord $Host "System has not gone for reboot yet. Loop timeout."
                exit 1
        elif [ $Noresponse -ne 0 ]; then
                Failrecord $Host "System has not rebooted yet. Loop timeout."
                exit 1
        fi
return 0


}




function addstr {
        str="$1"
        if [ $Negate -eq 1 ]; then
                if [ "X$Query" = "X" ]; then
                        str="NOT $str"
                else
                        str="-$str"
                fi
                Negate=0
        fi

        if [ "X$Query" = "X" ]; then
                Query="$str"
        else
                if [ $NextOR -eq 1 ]; then
                        Query+=" OR $str"
                        NextOR=0
                else
                        Query+=" AND $str"
                fi
        fi
}

while getopts "$OPTLIST" opt ; do
        case $opt in
#    Knife search options
        a) KQ=1; addstr "$OPTARG" ;;
        w) KQ=1; addstr "datacenter_workgroup:$OPTARG"  ;;
        f) KQ=1; addstr "datacenter_function:$OPTARG" ;;
        d) KQ=1
                case ${OPTARG,,} in
                adc) DC="ADC" ;;
                sc9|sjc*) DC="SJCD1" ;;
                dc4|iad*) DC="IADD1" ;;
                hebra*) DC="EMEA" ;;
                apac) DC="APAC" ;;
                *) DC="ADC" ;;
                esac
                addstr "Datacenter:${DC}"
#               addstr "Datacenter:${OPTARG^^}"
                 ;;
        e) KQ=1
                case ${OPTARG,,} in
                dev*) CEnv="Development" ;;
                prd|prod*) CEnv="Production" ;;
                qa) CEnv="QA" ;;
                qap) CEnv="QAP" ;;
                int) CEnv="Integration" ;;
                stg|stag*) CEnv="Staging" ;;
                perf*) CEnv="Perftest" ;;
                utc) CEnv="UTC" ;;
                trg|train*) CEnv="Training" ;;
                *) CEnv="Development" ;;
                esac
                addstr "chef_environment:$CEnv"
#               addstr "chef_environment:$OPTARG"
                 ;;
        t) KQ=1; addstr "tags:$OPTARG" ;;
        n) KQ=1; addstr "fqdn:$OPTARG" ;;
        N) Negate=1  ;;
        o) NextOR=1  ;;

# optional Additional Host options
        h) HostList+=( $OPTARG ) ;;
        H) HostList+=( $(<$OPTARG) ) ;;

# Action options Service/ Recipe/ Command?
        c) listOnly=1; pCMD=$OPTARG
                if [ ! ${preDefCMDs[$pCMD]+_} ]; then
                        echo "$pCMD: Unknown command"
                        exit 1
                fi
                ;;
        r) listOnly=1; Recipe=$OPTARG ;;
        s) listOnly=1; Service=$OPTARG ;;
        S) listOnly=1; runScript=1 ;;

# Concurrent SSH? may add other SSH options here later
        m) CONC=$OPTARG ;;
        R) Rboot=1 ;;
        L) me=$OPTARG; fLogin=1 ;;

# Misc
        D) DEBUG=$(($DEBUG+1)) ;;
        q) QUIET=1 ;;
        \?) echo "Invalid option: -$OPTARG" >&2
                exit 1 ;;
        :) echo "Option -$OPTARG requires an argument." >&2
                exit 1 ;;
        esac
        [ $DEBUG -ge 2 ] && {
                echo "DEBUG:${LINENO}"
                echo "  KQ=$KQ Negate=$Negate NextOR=$NextOR listOnly=$listOnly CONC=$CONC"
                echo "  Query=$Query"
                echo "  HostList=${HostList[*]}"
                }
done


shift $(($OPTIND - 1))

listOnly=$(($# + $listOnly))

if [ $# -ne 0 ]; then
        THECMD="$@"
fi

[ $DEBUG -ge 1 ] && {
        echo "DEBUG:${LINENO}"
        echo "  Option parsing Complete"
        echo "  Query=$Query"
        echo "  KQ=$KQ Negate=$Negate NextOR=$NextOR listOnly=$listOnly CONC=$CONC THECMD=$THECMD"
        echo "  HostList=${HostList[*]}"
        }

if [ $listOnly -eq 0 ]; then
        if [ $KQ -ne 0 ]; then
                knife search "$Query" -i
        fi
        for h in ${HostList[*]}
        do
                echo $h
        done
        exit 0
fi

#       knife ssh "$Query" "$@"
# Go for SSH
[ $DEBUG -ge 1 ] && echo "DEBUG:${LINENO}: Go for SSH"
#
# We cannot have both Cookbook and Service actions
#
if [ "X$Recipe" != "X" ] && [ "X$Service" != "X" ] && [ "X$pCMD" != "X" ]; then
        echo "only one of Recipe, Service or Command option can be used"
        exit 1
fi

if [ "X$Service" != "X" ]; then
        [ $DEBUG -ge 1 ] && echo "DEBUG:${LINENO}: Service=$Service Action: $THECMD"
                                        # Service: only selected action allowed
        if [[ "$THECMD" =~ ^(start|restart|status|stop|reload)$ ]]; then
                TAGSUDO=1
                runCMD="service $Service $THECMD"
        else
                echo $THECMD is not one of accepted commands
                exit 1
        fi
elif [ "X$Recipe" != "X" ]; then
        [ $DEBUG -ge 1 ] && echo "DEBUG:${LINENO}: Recipe=$Recipe Ignored: $THECMD"
        TAGSUDO=1
        runCMD="chef-client -o $Recipe"
elif [ $runScript -eq 1 ]; then
        TAGSUDO=0
        theScript="$THECMD"
        [ $DEBUG -ge 1 ] && echo "DEBUG:${LINENO}: arbitrary script to run = $theScript"
else
        TAGSUDO=0
        runCMD="$THECMD"
        [ $DEBUG -ge 1 ] && echo "DEBUG:${LINENO}: arbitrary command to run = $runCMD"
fi

# Lets go
#
create_temp

if [ $KQ -ne 0 ]; then
        knife search "$Query" -i >$TEMP_DIR/HostList 2>$TEMP_DIR/knife.error
        harray=( $(<$TEMP_DIR/HostList) )
        [ $DEBUG -ge 1 ] && {
                echo "DEBUG:${LINENO}: HostList from chef"
                for h in ${harray[*]}; do
                        echo "  $h"
                done
                }
fi

harray+=( ${HostList[*]} )
[ $DEBUG -ge 1 ] && {
        echo "DEBUG:${LINENO}: Combined HostList"
        for h in ${harray[*]}; do
                echo "  $h"
        done
        }

mkdir -p $TEMP_DIR/out/
mkdir -p $TEMP_DIR/procs
#echo 0 >$TEMP_DIR/Active
#echo 0 >$TEMP_DIR/Success
touch $TEMP_DIR/Success
#echo 0 >$TEMP_DIR/Failed
touch $TEMP_DIR/Failed


halen=${#harray[@]}

# Concurrent zero or less == all at once
[ $CONC -le 0 ] && CONC=$halen

hin=0
while [ $hin -lt $halen ]
do
        procs=$(ls $TEMP_DIR/procs |wc -l)
        while [ $procs -ge $CONC ]; do
                [ "$DEBUG" -ge 1 ] && echo "DEBUG:${LINENO}: Active=$procs"
                sleep 1
                procs=$(ls $TEMP_DIR/procs |wc -l)
        done

        [ "$DEBUG" -ge 1 ] && {
                echo "DEBUG:${LINENO}: hin=$hin, Active=$procs, Success=$(wc -l <$TEMP_DIR/Success), Failed=$(wc -l <$TEMP_DIR/Failed)"
                echo "DEBUG:${LINENO}: HostIndex=$hin ${harray[hin]}"
        }
        HOST=${harray[hin]}

        [ "$DEBUG" -ge 1 ] && echo "DEBUG:${LINENO}: Going for host $HOST"

# workarounds for Hosted and Public Cloud
# Delete when fixed

        uHOST="$HOST"
        [ $fLogin -eq 1 ] && uHOST="$me@$HOST"
        SUDO="sudo"

        if [[ ${HOST,,} =~ ^(iadd1|sjcd1|va) ]]; then
                [ $fLogin -eq 0 ] && {
                        if [ "$me" != "sa_rmtmgmt" ]; then
                                uHOST="admin_$me@$HOST"
                        fi
                }

                SUDO="dzdo"

                if [[ ${HOST,,} =~ ^va ]]; then
                        if [[ $HOST =~ '.' ]]; then
                                uHOST=${uHOST/./-nat.}
                        else
                                uHOST="${uHOST}-nat"
                        fi
                fi
        fi
# End of workaround

        goCMD="$runCMD"
        [ $TAGSUDO -eq 1 ] && goCMD="$SUDO -i $runCMD"

        [ "$DEBUG" -ge 1 ] && echo "DEBUG:${LINENO}: b4SSH HOST=$HOST goCMD=$goCMD uHOST=$uHOST SUDO=$SUDO TAGSUDO=$TAGSUDO"

        if [ "X$pCMD" != "X" ]; then
                ${preDefCMDs[$pCMD]} $HOST $uHOST $SUDO &
        elif [ $runScript -eq 1 ]; then
                ssh_script $HOST $uHOST $SUDO &
        else
                ssh_connect $HOST $uHOST "$goCMD" &
        fi
#

        ((hin++))
done

while [ $(ls $TEMP_DIR/procs|wc -l) -gt 0 ]
do
        wait
done

echo
Failed=$(wc -l <$TEMP_DIR/Failed)
echo "Summary:"
echo "  Failed: $Failed"
echo "  Succeeded: $(wc -l <$TEMP_DIR/Success)"
destroy_temp
exit $Failed
