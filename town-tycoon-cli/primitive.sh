#!/bin/bash

USERNAME=martlin2cz
PASSWORD=iwontsay
INTERVAL=60

function log_in() {
	wget --quiet \
		--post-data="kname=$USERNAME&kpass=$PASSWORD&x=16&y=42" \
		--save-cookie tmp/cookie.txt \
		-O tmp/logged.html \
		http://nz.town-tycoon.net/play/index.php
	
	if [ "$(grep 'error' tmp/logged.html)" == "" ]; then
		log "Logged in"
	else
		log "LOGIN FAILED"
	fi
}

while [ true ]; do

	log_in	
	sleep $INTERVAL

done
