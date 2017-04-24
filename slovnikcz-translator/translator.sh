#!/bin/bash
#	martlin's translator
#	uses slovnik.seznam.cz to translate between various languagues
#	6. 6. 2012, made by m@rltin

#version of script, please do not modifiy this
version="1.0"

#list of useable languagues
lol="cz en de fr it es ru sk"

#home and default foreign languague
home="cz"
fore="en"

#regexp to parge one char (it cotains case-senstive all word char (inc. diarcitics)), char ':' must be ecaped
charreg="[a-zA-Z\-\!\?\,\(\)áéěíóúůýčďňřšťžÁÉĚÍÓÚŮÝČĎŇŠŤŽßüäëÜËÄ]"

help () {
	echo "martlin's translator $version."
	echo "Usage: translate [-r] [FROM|TO] [WORD]"
	echo "       translate [-r] [WORD]       translates WORD from $fore to $home"
	echo "       translate [-r] FROM [WORD]  translates WORD from FROM to $home"
	echo "If WORD isn't entered or is '-', is readen on stdin."
	echo "Switch -r swaps FROM and TO langs."
	echo "Possible langs: "$(echo $lol | sed 's/ /, /g')". One of langs must be cz.";
	echo "Bugs report at martlin@seznam.cz"
	exit 0;
}

case "$1" in
	"-h" | "--help") help;;
	"-r" ) swap="1"; shift ;;
	"*"  ) swap="";;
esac

#if 'second' arg is some language form $lol, it is lang, else it is querry
if [ "$1" != "" ] && [ "$(echo $lol | grep $1)" != "" ]; then
	from=$1
	qerry=$2
else
	from=$fore
	qerry=$1
fi

#was switch -r entered?
if [ "$swap" == "1" ]; then
	to=$from
	from=$home
else
	to=$home
fi

#get qerry - $1 or on sdtin
if [ "$qerry" == "" ] || [ "$qerry" == "-" ]; then
	read qerry
fi

URL="http://slovnik.seznam.cz/$from-$to/word/?q=$qerry"
#echo $URL

wget -q  $URL -O translate.html

cat translate.html | 
	sed -e :a -e N -e 's/\n/ /' -e ta |	#join lines
sed -r "s:<a href=\"/($to-$from/\?q=$charreg+)\">($charreg+)</a>:\nTRWORD\2\n:g" | #find translate results and mark them
	grep "TRWORD" | #filter marks
	sed "s/TRWORD//" |	#remove marks
	sed -e :a -e N -e 's/\n/ /' -e ta	#merge to 1 line

rm translate.html

exit 0
