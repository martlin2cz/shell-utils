#!/bin/bash
## web update checker
## m@rtlin, 8.10.2019
## 
## in given interval watches (crawls) the given URL 
## and when starts to contain specified text, does something
##
#################################################

if [ "$#" != "2" ]; then
	echo "Usage: $0 URL PATTERN"
	exit 1
fi

# timeout in minutes between the requests
INTERVAL=10

#temp file path where to temporary store the loaded page
FILE=/tmp/page.html

# the adress to look at
URL=$1

# the value to try to find at the page
PATTERN=$2

#################################################
while [ true ] ; do
	echo -n $(date "+%d.%m. %T")
	echo -n " Loaging page ..."
	wget -q -O "$FILE" "$URL"
	echo -n " Loaded!"

	MATCH=$(grep --context 1 "$PATTERN" "$FILE")
	
	if [ "$MATCH" != "" ]; then
		echo " MATCH:"
		echo $MATCH
		xmessage "The page $URL contains now $PATTERN!"
		exit 0
	else
		echo " No match. :-(";
	fi
	
	sleep "${INTERVAL}m"
done
