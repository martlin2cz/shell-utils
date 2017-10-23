#!/bin/bash
# m@rtlin, 9.10.2017
#
# in loop connects to given URL
# and outputs (appends, obviously) to file LOGFILE
# whether or not server responds code 200 or not
#
# USAGE: monitor-status.sh [URL] [INTERVAL IN minutes] [LOGFILE]
# example: ./monitor-status.sh https://httpstat.us/404 2 logs.log

SITE=$1
WAIT=$2
LOGFILE=$3

while [ true ] ; do

	DATE=$(date);
	MSG=$(curl $SITE -s -f -o /dev/null && echo "OK")
	if [ "$MSG" == "" ] ; then
		MSG="failed"
	fi

	echo -e "$DATE \t $MSG" | tee -a $LOGFILE

	sleep $(( $WAIT * 60 ))
done
