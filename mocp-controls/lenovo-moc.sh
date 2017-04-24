#!/bin/bash
## Lenovo moc modifikátor $VERSION
## made by m@rtlin
## 28. 12. 2012
## verze 1.1 vytvorena 30.12.2012
##
## Pokud neběží moc server spustí jej a na základě parametru:
## $PREV - pokud probíhá přehrávání, pustí předchozí skladbu, jinak vypíše hlášku
## $NEXT - pokud probíhá přehrávání, pustí další skladbu, jinak jen pustí přehrávání
## $TOGGLE - pokud probíhá přehrávní, pozastaví jej, jinak přehrávání pustí (kombinace play a toggle)
##
## Pozn. pojem probíhá přehráváníi znamená NEBÝT ve stavu STOP, tedy být ve stavu PLAY nebo PAUSE

#verze
VERSION="1.2"

#název pomocného souboru s výpisem mocp --info
MOCPOUTF="mocpout"

#možné parametry
PREV="prev"
NEXT="next"
TOGGLE="toggle"

#konstanty udávající stav serveru
_PLAYING="PLAYING"
_PAUSED="PAUSED"
_STOPPED="STOPPED"
_NOTRUN="NOT_RUNNING"

#retezce, které obsahuje výpis mocp --info udávající jedtlivé stavy přehrávače
PLAYING='State: PLAY'
PAUSED='State: PAUSE'
STOPPED='State: STOP'
NOTRUN='FATAL_ERROR: The server is not running!'

###############################################################################
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
	echo "mocp modifkátor $VERSION. Pokud neběží mocp server spustí jej a provede následující (jako parametr):"
	echo "$PREV, $NEXT, $TOGGLE"
	exit 0
fi

###############################################################################
#výpis mocp --info, informace o stavu serveru
mocp --info > $MOCPOUTF 2>&1

#a určení stavovoé konstanty
if [ "$(grep "$PLAYING" $MOCPOUTF)" != "" ]; then
	state=$_PLAYING

elif [ "$(grep "$PAUSED" $MOCPOUTF)" != "" ]; then
	state=$_PAUSED

elif [ "$(grep "$STOPPED" $MOCPOUTF)" != "" ]; then
	state=$_STOPPED

elif [ "$(grep "$NOTRUN" $MOCPOUTF)" != "" ]; then
	state=$_NOTRUN
else
	echo "Nepodarilo se zjistit stav prehravace." 1>&2
	exit 1
fi

rm $MOCPOUTF

#Neběží server? Tak ho spusť
if [ "$state" == "$_NOTRUN" ]; then
	mocp --server
	state=$_STOPPED
fi

###############################################################################
#Co se má provést?
case $1 in
	$PREV) 
		if [ "$state" == "$_STOPPED" ]; then
			echo "Žádná další skladba k vrácení zpět."
		else
			mocp --prev
		fi
		;;

	$NEXT)
		if [ "$state" == "$_STOPPED" ]; then
			mocp --play
		else
			mocp --next
		fi
		;;

	$TOGGLE)
		if [ "$state" == "$_STOPPED" ]; then
			mocp --play
		else
			mocp --toggle-pause
		fi
	;;

	"")
		echo "Chybí parametr. Použijte -h/--help." 1>&2
		exit 2
		;;

	*)
		echo "Chybný parametr $1. Použijte -h/--help." 1>&2
		exit 3
		;;
esac

exit 0
