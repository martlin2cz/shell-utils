#!/bin/bash
# Each $WAIT second presses the PageDown key

WAIT=5

while [ true ] ; do
	sleep $WAIT
	xdotool key Page_Down
done


