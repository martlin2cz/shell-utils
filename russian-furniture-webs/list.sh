#!/bin/bash
# Script for listing the wierd russian furniture websites
# usage: ./list.sh [INITIAL_URL]
# m@rtlin, 10.12.2019

#URL="https://www.lbsprague.cz/hotelovy-nabytek"
URL=$1

while [ true ] ; do
	echo -n $(date) " | "
	wget --quiet -O tmp_download $URL

	if [ "$(file tmp_download | grep 'HTML')" != "" ]; then
		echo -n "[HTML] | "
		mv tmp_download html_download

	elif [ "$(file tmp_download | grep 'gzip')" != "" ]; then
		echo -n "[GZIP] | "
		mv tmp_download gzip_download.gz
		gunzip gzip_download.gz
		mv gzip_download html_download
	elif [ "$(file tmp_download | grep 'empty')" != "" ]; then
		echo "No response from server"
		exit 1
	
	else
		echo "Unsupported file!"
		exit 2
	fi

	NEWURL=$( cat html_download  \
		| sed -E 's/<a href="([^"]+)"[^>]*>[^<]+<\/a>/\n\1\n/g' \
		| grep -E "^https?://")

	# cat html_download | sed -E 's/<a href="([^"]+)"[^>]*>[^<]+<\/a>/\n$$$$$$\n\1\n$$$$$$\n/g'
	
	if [ "$NEWURL" == "" ]; then
		echo "No next url"
		exit 3
	fi

	echo $NEWURL
	URL=$NEWURL

	sleep 10
done

