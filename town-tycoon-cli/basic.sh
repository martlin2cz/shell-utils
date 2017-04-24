#!/bin/bash

USERNAME=martlin2cz2
PASSWORD=ma248xe-lin2
INTERVAL=60
LOOPSIZE=60

function log() {
	echo -n $(date "+%d.%m. %H:%M:%S") ": "
	echo "$@"
}

function get_notif_info() {
	FIELD=$1
	if [ "$(grep \"$FIELD\" tmp/notifications.xml)" == "" ]; then
		echo "???"
	else
		cat tmp/notifications.xml | sed -r 's/.*<i n="'$FIELD'" v="(-?[0-9\.]+)"\/>.*/\1/g'	
	fi
}

function log_in() {
	wget --quiet \
		--post-data="kname=$USERNAME&kpass=$PASSWORD&x=16&y=42" \
		--save-cookie tmp/cookie.txt \
		-O tmp/logged.html \
		http://gb.town-tycoon.net/play/index.php
	
	if [ "$(grep 'error' tmp/logged.html)" == "" ]; then
		log "Logged in as $USERNAME"
	else
		log "LOGIN FAILED"
	fi
}

function ping_server() {
	wget --quiet \
		--load-cookie tmp/cookie.txt \
		-O tmp/notifications.xml \
		http://gb.town-tycoon.net/play/aj_notifications.php

	log "Money:" $(get_notif_info 'sm') "/" $(get_notif_info 'sgl') \
		"Concrete:" $(get_notif_info 'sb') \
		"Steel:" $(get_notif_info 'ss') \
		"Wood:" $(get_notif_info 'sh') \
		"Storage:" $(get_notif_info 'sl') \
		"Inhibs:" $(get_notif_info 'se') \
		"Energy:" $(get_notif_info 'sen') "/" $(get_notif_info 'sep') \
	


}


while [ true ]; do
	log_in

	for ((I=0; I<$LOOPSIZE; I++)) {
		ping_server
		sleep $INTERVAL
	}

done
