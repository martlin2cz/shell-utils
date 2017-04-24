#!/bin/bash
# v1.0, m@rtlin, 11. 11. 2013
#v pravidelncýh intervalech $INTERVAL +-50% (náhodně) sekund se dotazuje na soubor na $URL a pokud dojde k jeho změně, přehraje zvuk $ALERT a stáhne soubor $TOHSHOW jako $TOSHOWTMP a zobrazí ho v evince.

#Ukázková data:
#INTERVAL=5
#URL=http://localhost
#TMPFILE=index.html
#TMPFILE2=index.html_old
#ALERT=~/sirene.wav
#TOSHOW=http://localhost/share/131028/liv.pdf
#TOSHOWTMP=liv.pdf

INTERVAL=1800
URL=http://phoenix.inf.upol.cz/~krajcap/courses/2013ZS/DATA1/
TMPFILE=index.html
TMPFILE2=index.html_old
ALERT=~/sirene.wav
TOSHOW=http://phoenix.inf.upol.cz/~krajcap/courses/2013ZS/DATA1/vysledky.pdf
TOSHOWTMP=vysledky.pdf

changed() {
	aplay $ALERT
	wget $TOSHOW
	evince $TOSHOWTMP
	rm $TOSHOWTMP
}

echo -n "Je "$(date "+%H:%M")" a provádím inicializaci ...  "
wget --quiet $URL 
cp $TMPFILE $TMPFILE2
NEXTINT=$INTERVAL
echo "Zinicializováno"

while true; do
	echo -n "Je "$(date "+%H:%M")" a stahuji ...  "
	wget --quiet $URL 

	if  ! [ -e $TMPFILE -a -e $TMPFILE ]; then
		echo "CHYBA: stažený soubor neexistuje, končím"
	fi
	if [ "$(cat $TMPFILE)" != "$(cat $TMPFILE2)" ]; then
		echo -e "ZMĚNA!"
		rm $TMPFILE $TMPFILE2
		changed
		break
	else
		NEXTINT=$(($INTERVAL / 2 + $RANDOM % $INTERVAL))
		echo "beze změny, za $NEXTINT sekund zkusím zase"
		mv $TMPFILE $TMPFILE2
	fi

	sleep $NEXTINT
done
