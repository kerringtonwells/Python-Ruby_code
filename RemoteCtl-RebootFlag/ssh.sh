#!/bin/bash
ssh_connect() {
#
        Host=$1
        uHost=$2
        myCMD="$3"
        set -o pipefail

        echo $$ >$TEMP_DIR/procs/$Host
        ssh -T $SSH_ARGS $uHost "$myCMD" 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        if [ $? -ne 0 ]; then
                echo $Host >>$TEMP_DIR/Failed
        else
                echo $Host >>$TEMP_DIR/Success
        fi
        rm -f $TEMP_DIR/procs/$Host 2>/dev/null
}




ssh_script() {
#
        Host=$1; uHost=$2; mSUDO="$3"
        set -o pipefail

        echo $$ >$TEMP_DIR/procs/$Host
        cat $theScript|ssh -T $SSH_ARGS $uHost "$mSUDO -i" 2>&1 \
            | tee -a $TEMP_DIR/out/$Host |while read SSH_LINE ; do
                if [ "$QUIET" -lt 1 -a "$SSH_LINE" != "" ] ; then
                        echo "$SSH_LINE" | sed -e "s/^/$Host: /"
                fi
            done
        if [ $? -ne 0 ]; then
                echo $Host >>$TEMP_DIR/Failed
        else
                echo $Host >>$TEMP_DIR/Success
        fi
        rm -f $TEMP_DIR/procs/$Host 2>/dev/null
}

