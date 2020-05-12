#!/bin/bash
# Runs the opera history backup.
# TODO comment
###############################################################################
if [ -e "history.db" ]; then
	echo "The history file exists already, get it out of the way"
	exit 1
fi

###############################################################################
echo "Open the Opera and its history page by URL about://history"
read

###############################################################################
echo "Open the developper tools by pressing Ctrl+Shift+I"
read

###############################################################################
echo "Switch to the Opera history page, set focus to the main page area"
echo "and let the script scroll down ad much as needed"
echo "When ready, switch back to this window and press Enter"
read

# start the scroll script
. scroll.sh &
PID=$!

echo "(scrolling is running)"
sleep 5

###############################################################################
echo "Scrolled enough?"
read

# kill the scroll script
kill -TERM $PID

###############################################################################
echo "Wait until the nodejs collector service starts"
#read

# start the nodejs service
# Note: you cannot start via npm, because it cannot be killed then
#npm start &
# start "normally" then:
nodejs service.js &
PID=$!

sleep 5
echo

###############################################################################
echo "Ready?"
read

###############################################################################
echo "Copy the following script to the clipboard"

# output the browser source 
# (without single lined and multilined comments, as one line)
cat browser.js \
	| grep -Ev '^[^\"]*//' \
	| tr ' \n\t' ' ' \
	| sed -E 's|\/\*[^\/]+\*\/||g' 
echo
read

###############################################################################
echo "Paste it to the Opera dev tools console"
read

###############################################################################
echo "And now wait ..."
read

###############################################################################
echo "Done?"
read

###############################################################################
echo "Wait until the collector service terminates"
read

# kill the nodejs service
kill -INT $PID

echo
sleep 5

###############################################################################
echo "Have the nodejs collector service terminated?"
read

###############################################################################
echo "Verify the collected database"
read

# execute the count sql
echo "Collected entries: "
sqlite3 "history.db" "SELECT COUNT(*) FROM history"

###############################################################################
echo "Is the amount of collected entries okay?"
read

###############################################################################
echo "We are done then! You can now close the history page."
read

echo "Bye"
exit 0

