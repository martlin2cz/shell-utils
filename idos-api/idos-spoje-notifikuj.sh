#!/bin/bash
#Zobazí notifkační okna pro zoadaný seznam směrů
#m@rtlin, 03. čec 2014
#update na v1.2: 04. čec 2014
#update na v1.3: 26. čen 2015


## soubor ikony notifikace
ICON=/home/martin/Programovani/shell/IDOS_API/dpmo-ikonka.png

##příkaz pro načtení seznamu spojů (cesta k get-idos-spoje.sh nebo jen get-idos-spoje.sh, pokud je na PATH)
GISCMD=/home/martin/Programovani/shell/IDOS_API/get-idos-spoje.sh
###############################################################################
##Ověříme vstup
if [ "$(($# % 4))" != "0" ]; then
	echo "Použití: $0  TYPE1 FROM1 TO1 COUNT1   TYPE2 FROM2 TO2 COUNT3 ...  TYPEn FROMn TOn COUNTn"
	echo "pozor na mezery a středníky a raděj bez diakritiky"
	exit 1
fi

##A projdeme všechny dvojce, vytáhneme z nich spojení a zanitifikujeme
while [ "$#" != "0" ]; do
	jrtype=$1
	from=$2
	to=$3
	count=$4
	shift 4

	echo "Hledám spoje $from > $to ..."

	##Načteme spoje
	spoje=$($GISCMD "$jrtype" "$from" "$to" "$count")

	text=$(echo $spoje | sed -r "s;([0-9]+\.[0-9]+\.) ([0-9]+:[0-9]+) ([^ ]+) ([^\|]+)\| ?;v \2 spoj \3 (\4)\n;g")

	##A zobrazíme notifikační okénko
	notify-send --icon=$ICON "$from > $to" "$text"

done

exit 0
##Projdeme všechny to (před průchodem musíme každý "zaescapovat - přepsat mezery na __, pak rozsekat podle ; a pak každý znovu odescapovat)
for toesc in  $(echo $tos | sed 's| |__|g' | sed 's|;| |g'); do
	to=$(echo $toesc | sed 's|__| |g')

	echo "Hledám spoje $from > $to ..."
	##Načteme spoje
	spoje=$($GISCMD "$from" "$to" "$count")

	done

exit 0

