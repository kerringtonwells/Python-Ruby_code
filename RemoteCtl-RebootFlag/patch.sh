#!/bin/bash
chefospatch() {
        Host=$1; uHost=$2; mSUDO="$3"
        set -o pipefail
        echo $$ >$TEMP_DIR/procs/$Host
#
# Chef: Stopapp
# patch, get uptime, reboot, verify
# verify :get uptime/ wait, get uptime
#
# Chef: Start app
#
#    Get uptime
        sUpt=$(ssh -T $SSH_ARGS $uHost "awk -F. '{print \$1}' /proc/uptime" 2>/dev/null)
        [ $? -ne 0 ] && { Failrecord $Host "Could not even get uptime. aborting"; return 1; }
        conout $Host "uptime at start: $sUpt secs"

# stopapp using chef
        conout $Host "Stop Applications ..."
        ssh -T $SSH_ARGS $uHost "$mSUDO chef-client -o ihg-service::stopapp" 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        [ $? -ne 0 ] && { Failrecord $Host "Stopapp failed. aborting"; return 1; }

#    Patch update
        conout $Host "Start OS update ..."
        ssh -T $SSH_ARGS $uHost "$mSUDO chef-client -o ihg-patch::full" 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        [ $? -ne 0 ] && { Failrecord $Host "OS Patch update failed. aborting"; return 1; }


        if [ $Rboot -eq 1 ]; then
        Reboot
        fi
# startapp using chef
        conout $Host "Starting Applications ..."
        ssh -T $SSH_ARGS $uHost "$mSUDO chef-client -o ihg-service::startapp" 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        [ $? -ne 0 ] && { Failrecord $Host "Startapp failed. aborting"; return 1; }



# All good.
        echo $Host >>$TEMP_DIR/Success
        rm -f $TEMP_DIR/procs/$Host 2>/dev/null


}

ospatch() {
        Host=$1; uHost=$2; mSUDO="$3"
        set -o pipefail
        echo $$ >$TEMP_DIR/procs/$Host
#
# Get appusers
# Check for process; stop process; verify stopped
#
# patch, get uptime, reboot, verify
# verify :get uptime/ wait, get uptime
#
# Start app; verify
#
#    Get uptime
        sUpt=$(ssh -T $SSH_ARGS $uHost "awk -F. '{print \$1}' /proc/uptime" 2>/dev/null)
        [ $? -ne 0 ] && { Failrecord $Host "Could not even get uptime. aborting"; return 1; }
        conout $Host "uptime at start: $sUpt secs"
#   Get appusers
        conout $Host "Get app users"
        appusers=$(getappusers $Host)
        [ $DEBUG -ne 0 ] && conout $Host "AppUsers = $appusers"
        for appu in $appusers
        do

                conout $Host "Check and stop processes for $appu"
#    Check process status
                Up=$((echo 'shopt -s expand_aliases; chkprocs -s|tail -1')|ssh -T $SSH_ARGS $uHost "$mSUDO -i -u $appu" 2>/dev/null)
                [ $? -ne 0 ] && { Failrecord $Host "Could not get application status. aborting"; return 1; }
                conout $Host "Application $appu status: $Up"

                if [ "X$Up" = "XUp" ]; then
# Stop the process
                        (echo 'shopt -s expand_aliases; stopapp')|ssh -T $SSH_ARGS $uHost "$mSUDO -i -u $appu" 2>&1|conout $Host

# Check again
                        sleep 2
                        Up=$((echo 'shopt -s expand_aliases; chkprocs -s|tail -1')|ssh -T $SSH_ARGS $uHost "$mSUDO -i -u $appu" 2>/dev/null)
                        [ $? -ne 0 ] && { Failrecord $Host "Could not get application status. aborting"; return 1; }
                        conout $Host "Application $appu status: $Up"

                        [ "X$Up" = "XUp" ] && { Failrecord $Host "Could not stop the application. aborting"; return 1; }
                fi
        done

#    Patch update
        conout $Host "Start OS update ..."
        ssh -T $SSH_ARGS $uHost "$mSUDO chef-client -o ihg-patch::full" 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        [ $? -ne 0 ] && { Failrecord $Host "OS Patch update failed. aborting"; return 1; }



        for appu in $appusers
        do
# Start the process
                conout $Host "Start application $appu"
                (echo 'shopt -s expand_aliases;startapp')|ssh -T $SSH_ARGS $uHost "$mSUDO -i -u $appu" 2>&1|conout $Host
# Check
                sleep 2
        done
        for appu in $appusers
        do
                conout $Host "Verify application $appu"
                Up=$((echo 'shopt -s expand_aliases; chkprocs -s')|ssh -T $SSH_ARGS $uHost "$mSUDO -i -u $appu" 2>&1 |tail -1)
                [ $? -ne 0 ] && { Failrecord $Host "Could not get application status. aborting"; return 1; }
                conout $Host "Application $appu status: $Up"

                [ "X$Up" != "XUp" ] && { Failrecord $Host "Could not start the application. aborting"; return 1; }
        done

# All good.
        echo $Host >>$TEMP_DIR/Success
        rm -f $TEMP_DIR/procs/$Host 2>/dev/null
}



vospatch() {
        Host=$1; uHost=$2; mSUDO="$3"
        set -o pipefail
        echo $$ >$TEMP_DIR/procs/$Host
#
# patch, get uptime, reboot, verify
# verify :get uptime/ wait, get uptime
#
#    Get uptime
        sUpt=$(ssh -T $SSH_ARGS $uHost "awk -F. '{print \$1}' /proc/uptime" 2>/dev/null)
        [ $? -ne 0 ] && { Failrecord $Host "Could not even get uptime. aborting"; return 1; }
        conout $Host "uptime at start: $sUpt secs"
#    Patch update
        ssh -T $SSH_ARGS $uHost "$mSUDO chef-client -o ihg-patch::full" 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        [ $? -ne 0 ] && { Failrecord $Host "OS Patch update failed. aborting"; return 1; }


if [ $Rboot -eq 1 ]; then
Reboot
fi

        echo $Host >>$TEMP_DIR/Success
        rm -f $TEMP_DIR/procs/$Host 2>/dev/null
}




