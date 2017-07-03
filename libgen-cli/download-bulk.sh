#!/bin/bash
# m@rtlin, 02.07.2017
# tries to download from given CSV file
# input file is in following format:
# 	status;file-name;query-1;query-2
#######################################

# separator in CSV file
SEPARATOR=';'

#what has to be status to start downloading (exact match, not regex)
DOWNLOAD_WHEN_STATUS=""

#######################################
readarray LINES < $1

#echo ${LINES[*]};

for LINE in "${LINES[@]}"; do
	STATUS=$(echo $LINE | awk -F$SEPARATOR -v pos=1 '{print $pos}')
	FILE=$(echo $LINE 	| awk -F$SEPARATOR -v pos=2 '{print $pos}')
	QUERY1=$(echo $LINE | awk -F$SEPARATOR -v pos=3 '{print $pos}')
	QUERY2=$(echo $LINE | awk -F$SEPARATOR -v pos=4 '{print $pos}')

	echo -e "File: $FILE\n Query 1: $QUERY1\n Query 2: $QUERY2\n Status: $STATUS\n"
	
	if [ "$STATUS" == "$DOWNLOAD_WHEN_STATUS" ] ; then
		echo "[Trying to download]"

		node ~/Programovani/shell/shell-utils/libgen-cli/download-pdf.js "$QUERY1 $QUERY2" "$FILE"
	else
		echo "[Yet downloaded]"
	fi

	echo
done

exit 0


