#!/bin/bash
## vyhledá spoje zadaného JŘ typu ze zadané zastávky do zadaného směru a vypíše jako záznamy ve tvaru _H?H:MM_|_LL_ oddělené bílým znakem
## m@rtlin, 28. čen 2014
## update na verzi 1.2 dne 25. cen 2015

###############################################################################
function get_next_3() {
	## Zpracujeme vstup
	local jrtype=$1
	local from=$2
	local to=$3
	local datetime=$4

	if [ "$datetime" == "" ] ; then
		datetime=$(date "+%m/%d/%y %H:%M")
	fi
	
	echo "Posílám dotaz: typ: $jrtype, z: $from, do: $to, kdy: $datetime" >&2

	## Sestavíme URL dotazu
	fromesc=$(echo $from | sed 's/ /%20/g')
	toesc=$(echo $to | sed 's/ /%20/g')

	date=$(date --date="$datetime" "+%d.%m.%y")
	time=$(date --date="$datetime" "+%H:%M")

	url="www.idos.cz/$jrtype/spojeni/?f=$fromesc&t=$toesc&date=$date&time=$time&submit=true"
	#echo "$url"

	## Stáhneme soubor s výsledky
	wget -q -O spoje.html $url

	## A rozsekáme
	cat spoje.html |
		tr -d '\n' | sed -r 's/\s+/ /g'| #sloučíme do jednoho řádku
		sed "s|<!-- zobrazeni vysledku end-->.*$||" | #odstranime konec za tabulkou
		sed "s|<tr class=\"datarow first\">|\\nJR_DATA_ROW: |g" | #a vytvoříme samostatné řádky s obsahy požadovaných tr tagů (odchycení začátku)
		grep "JR_DATA_ROW:" |	#vyfiltrujeme jen naše požadované "řádky" (tj. vyhodíme vše před prvním JR_DATA_ROW)
		sed -r "s|.+<td class=\"date\">([^<]+)</td>.+<td class=\"right\">([0-9]{1,2}\:[0-9]{1,2})</td>.+onclick=\"return PopupOpen\(event,&#39;route&#39;\);\">([^<]+)</a>.+Celkový čas <strong>([^<]+)</strong>.+|\1\t\2\t\3\t\4\||g" | #vyfiltrujeme vse potrebne
		sed "s| |_|g" | #odstraníme mezery z údajů
		cat
}

###############################################################################
## Ověříme vstup
if [ "$#" -ge "3" ] ; then
	jrtype=$1
	from=$2
	to=$3
	count=$4
	datetime=$5
else
	echo "Použití: $0 TYPE FROM TO [COUNT] [DATETIME]"
	echo "pozor na mezery a raděj bez diakritiky"   
	exit 1
fi

if [ "$count" == "" ] ; then
	count=3
fi

spoje=""

for (( i=0; $i<$count ; i=$i+3)); do 
	#echo Next -> $datetime
	this3=$(get_next_3 "$jrtype" "$from" "$to" "$datetime")
	echo -n $this3

	lastspoj=$(echo $this3 | sed -r "s;^.+\|([^\|]+)\|$;\1;g")
	lsdatetime=$(echo $lastspoj | sed -r "s|^([0-9]+)\.([0-9]+)\. ([0-9]+:[0-9]+).+$|\2/\1 \3|")
	nsdatetime=$(date --date="$lsdatetime + 2minutes" "+%m/%d/%y %H:%M" )
	
	datetime=$nsdatetime
done
###############################################################################
#

#echo $spoje
rm spoje.html
exit 1








	sed -r "s|.+<td class=\"right\">([0-9]{1,2}\:[0-9]{1,2})</td>.+onclick=\"return PopupOpen(event,&#39;route&#39;);\">([^<]+)</a>.+|____\1__\2__|" | #TODO vyfiltrujeme čas ... a co dál?	
	
spojetmp=$(cat spoje.html |
	 tr -d '\n' | sed -r 's/\s+/ /g'| #sloučíme do jednoho řádku
	 sed "s|<tr class=\"datarow first\">|\n[[[|g" |	#a vytvoříme samostatné řádky s obsahy požadovaných tr tagů (odchycení začátku)
	 sed "s|</tr>|]]]\n|g" | #a vytvoříme samostatné řádky s obsahy požadovaných tr tagů (konce)
	 grep '\[\[\[' ) #vyfiltrujeme - necháme pouze je

echo $spojetmp | tr "]]]" "]]]\n\n"

#echo $spojetmp

#if [ "$(echo $spojetmp | grep 'onclick="return PopupOpen(event,&#39;route&#39;);">')" != "" ] ; then
#	echo "s linkou"
#spoje=$(echo $spojetmp | sed -r 's|.+<td class=\"right\">([0-9]{1,2}\:[0-9]{1,2})</td>.+onclick="return PopupOpen\(event,&#39;route&#39;\);">([^[])+</a>.+|\n__________\1_____\2_____\n|g')

	#	spoje=$(echo $spojetmp | sed -r 's|.+<td class=\"right\">([0-9]{1,2}\:[0-9]{1,2})</td>.+onclick="return PopupOpen(event,&#39;route&#39;);"[^>]*>([^<])+</a>.+|_\1_@_\2_|')
#else
#	echo "Bez linky"
##	spoje=$(echo $spojetmp | sed -r 's|.+<td class=\"right\">([0-9]{1,2}\:[0-9]{1,2})</td>.*|_\1_@_ _|')
#fi


 #	 sed -r 's|.+<td class=\"right\">([0-9]{1,2}\:[0-9]{1,2})</td>.+<a onclick="return PopupOpen\(event,&#39;route&#39;\);"[^>]*>([^<])+</a>.+|_\1_@_\2_|')

echo $spoje

#echo $spoje | sed -r 's|_([^_]+)_@_([^_]+)_ ?|v \1 (linka \2)\n|g'

rm spoje.html
exit 0
