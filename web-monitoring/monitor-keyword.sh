#!/bin/bash
# m@rtlin, 9.10.2017
#
# in loop connects to given URL
# and outputs (appends, obviously) to file LOGFILE
# whether or not cotains given KEYWORD
#
# USAGE: monitor-status.sh [URL] [INTERVAL IN minutes] [LOGFILE] [KEYWORD]
# example: ./monitor-status.sh https://httpstat.us/404 2 logs.log "Not found"

SITE="$1"
WAIT=$2
LOGFILE="$3"
KEYWORD="$4"

while [ true ] ; do

	DATE=$(date);
	MSG=$(curl -s $SITE | grep "$KEYWORD")
	if [ "$MSG" != "" ] ; then
		MSG="has $KEYWORD"
	else
		MSG="nope"
	fi

	echo -e "$DATE \t $MSG" | tee -a $LOGFILE

	sleep $(( $WAIT * 60 ))
done
