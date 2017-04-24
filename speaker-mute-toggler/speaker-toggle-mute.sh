#!/bin/bash
# toggles mute/unmute at Speakers at given $CARD
# m@rtlin, 02.1.2016
# v1.0

#the audio card to use, use something like: aplay -l | grep ", device "
CARD=0

#name of "speakers" output
SPEAKERS=Speaker

#value of speakers' noise which is meant as "on"
THRESHOLD=50

###############################################################################
STATUS=$(amixer --card $CARD get $SPEAKERS)

#we will ignore secon channel
VOLUME=$(echo $STATUS \
	| grep -P '\[\d{1,3}%\]' \
	| sed -r 's|\[([0-9]{1,3})\%\]|_\1_|' \
	| sed -r 's|([^\_]+)\_([^\_]+)\_([^\_]+)|\2|' \
	| head -n1 \
	)

ON=$(echo $STATUS \
	| grep -P '\[on\]' \
	| sed -r 's|.*\[on\].*|on|g' \
	| head -n1
	)

#http://stackoverflow.com/questions/24896433/assigning-the-result-of-test-to-a-variable
[ "$ON" != "on" ]
IS_ON=$?

IS_LOUD=$(echo $(($VOLUME > $THRESHOLD)))

#echo == $IS_ON == $IS_LOUD ==
#echo $VOLUME
#echo $ON


if   (($IS_ON == 0 || $IS_LOUD == 0))  ; then

	amixer --quiet --card $CARD set $SPEAKERS unmute
	amixer --quiet --card $CARD set $SPEAKERS 100%
	echo "Speakers on"

else 

	amixer --quiet --card $CARD set $SPEAKERS 1%
	echo "Speakers off"

fi

