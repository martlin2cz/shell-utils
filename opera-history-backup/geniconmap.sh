#!/bin/bash

echo "" > ficonmap.html
echo "<html><head><title>favicon map!</title><style>img {width: 16px; height: 16px; }</style></head><body>" >> ficonmap.html

SERVERS=$(sqlite3 history.db "SELECT server FROM history")

for SERVER in $SERVERS; do
	echo "<img src=\"http://$SERVER/favicon.ico\" alt=\"&#x2717;\" title=\"$SERVER\">" >> ficonmap.html
done


echo "</body></html>" >> ficonmap.html
