#!/usr/bin/env bash

# usage ./test.sh logfile

LOGFILE=$1

PREV_STATUS="up"
STATUS="down"

while true
do
    if nc -z localhost 30080
    then
      STATUS="up"
    else
      STATUS="down"
    fi
    if [[ $STATUS != $PREV_STATUS ]]
    then
       echo "$(date +%s%N) $STATUS" >> $LOGFILE
    fi
    PREV_STATUS=$STATUS
done