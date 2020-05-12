#!/bin/bash
# Collects the servers from the INFILE sqllite db
# and outputs the html file with their (default) favicons.
#
###########################################################
# the history input file
INFILE=history.db
# the output file
OUTFILE=ficonmap.html
###########################################################

echo "" > OUTFILE
echo "<html><head>"  >> OUTFILE
echo "	<title>favicons map!</title>"  >> OUTFILE
echo "	<style>" >> OUTFILE
echo "		img {width: 16px; height: 16px; }"  >> OUTFILE
echo "	</style>"  >> OUTFILE
echo "</head><body>" >> OUTFILE

###########################################################

SERVERS=$(sqlite3 $INFILE "SELECT server FROM history")

for SERVER in $SERVERS; do
	echo "	<img src=\"https://$SERVER/favicon.ico\" alt=\"&#x2717;\" title=\"$SERVER\">" >> OUTFILE
done

###########################################################
echo "</body></html>" >> OUTFILE
