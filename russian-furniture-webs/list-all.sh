#!/bin/bash
# Script for iterative running the list.sh script over bunch of URLs (from given FILE)
# Usage: ./list-all.sh FILE
# m@rtlin, 10.12.2019


FILE=$1

for URL in $(cat $FILE); do
	echo "### $URL"
	./list.sh $URL
done

