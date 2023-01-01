#!/bin/bash
## made by m@rtlin
## $VERSION
## 11. čec. 2013
## zmodifikovani skriptu lenovo-moc.sh
##
## Vypíše aktální přehrávanou skladbu
##
## Repair na 1.2 dne 17. 10. 2013
##

#verze
VERSION="1.2"

#název pomocného souboru s výpisem mocp --info
MOCPOUTF="mocpout"

#retezce, které obsahuje výpis mocp --info udávající jedtlivé stavy přehrávače
PLAYING='State: PLAY'
PAUSED='State: PAUSE'
STOPPED='State: STOP'
NOTRUN='FATAL_ERROR: The server is not running!'

###############################################################################
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
	echo "Vypíše hlášku o aktuální skladbě"
	exit 0
fi

###############################################################################
#výpis mocp --info, informace o stavu serveru
mocp --info > $MOCPOUTF 2>&1

#samotné získání názvu skladby	
if [ "$(grep "$STOPPED" $MOCPOUTF)" != "" ]; then
	echo "Stopped."
elif [ "$(grep "$NOTRUN" $MOCPOUTF)" != "" ]; then
	echo "Server is not running."
elif [ "$(grep "$PLAYING" $MOCPOUTF)" != "" ] || [ "$(grep "$PAUSED" $MOCPOUTF)" != "" ]; then
	
	#získání jména autora
	auth=$(grep '^Artist: ' $MOCPOUTF | sed 's/Artist: //')

	song=$(grep '^SongTitle: ' $MOCPOUTF | sed 's/SongTitle: //')
	if [ "$song" == "" ]; then
		song=$(grep -e '^Title: ' $MOCPOUTF | sed 's/Title: //')
		if [ "$song" == "" ]; then
			song=$(grep '^File: ' $MOCPOUTF | sed 's/File: //' | sed 's/.*\///')
			#nazev souboru uz musi zabrat
		fi
	fi

	echo $auth
	echo $song
else
	echo "Error"
fi

rm $MOCPOUTF
exit 0
