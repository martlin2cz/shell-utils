#!/bin/bash
#m@rtlin, 2.1.2016
#toggles speakers' "mute" and notifies
#v1.0

#command to run
CMD=speaker-toggle-mute.sh

#dir with icons to use
ICONS_DIR=/usr/share/icons/gnome/48x48/status/


###############################################################################

IS_ON=$($CMD)

if [ "$IS_ON" == "Speakers on" ] ; then
#	echo "ON:" $IS_ON
	notify-send \
	--icon=${ICONS_DIR}audio-volume-high.png \
	--app-name=$0 \
	"Speakers on" \
	"Speakers are now ON"
	
elif [ "$IS_ON" == "Speakers off" ] ; then
	notify-send \
	--icon=${ICONS_DIR}audio-volume-muted.png  \
	--app-name=$0 \
	"Speakers off" \
	"Speakers are now OFF"

else
#	echo "Something bad happened"
	notify-send \
	--icon=dialog-error \
	--app-name=$0 \
	"Speakers off" \
	"Speakers are now OFF"
fi

exit 0
