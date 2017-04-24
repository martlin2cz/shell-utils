#!/bin/bash
#17. zář 2014 m@rtlin
#Vytvoří seznam.cz účet dle zadaných parametrů (<uz. jmeno> <domena bez @> <heslo>)

if [ "$#" != "3" ]; then
	echo "použití: <uz. jmeno> <domena bez @> <heslo>"
	exit 1;
fi

#params

###################
## uživatelské jméno
username=$1
## doména (seznam.cz, post.cz, email.cz)
domain=$2
## heslo
pass=$3

###################
## pohlaví (m=muž, f=žena)
sex=$(cat /dev/urandom |  tr -dc 'mf' | fold -w 1 | head -n 1)
## rok narození
year=$((1950 + $RANDOM % 50))

###################
## telefon nebo
phone=""
## sekundární email nebo
email=""
## kontrolní otázka (4, 5, 8, 12, 13 nebo 14) a
questionId=$((4 + ($RANDOM%2) + (($RANDOM%2) * 8)))
## odpověď
answer=$(./answer_create.sh)

## soubor, na jehož konec bude vložen záznam o tomto uživateli
LOG=../register/2register.txt
#####################################################################
### main ###

echo "Stahuji data ..."

#download form
wget -q --save-cookies cookies.txt -O registerform.html https://registrace.seznam.cz/register.py/stageZeroScreen 

#parse hidden fields from form
hiddens=$(cat registerform.html | grep '<input type="hidden"' | sed -r 's:(\s+<input type="hidden" name=")([^"]+)(" value=")([^"]*)(" />):\2=\4\&:' | tr -d '\n')

#hidden fields + form values = query
query=$hiddens'&answer='$answer'&domain='$domain'&email='$email'&licence=1&password='$pass'&password2='$pass'&phone='$phone'&questionId='$question'&sex='$sex'&username='$username'&year='$year

#submit form data
echo "Odesílám data (to může trvat) ..."
wget -q --load-cookies cookies.txt --post-data "$query" -O result.html https://registrace.seznam.cz/registrationProcess

#result
if [ "$(cat result.html | grep 'Gratulujeme')" != "" ]; then
	echo "Hotovo! Uživatel $username@$domain s heslem $pass zaregistrován."
	echo $username@$domain'|'$pass >> $LOG
else
	echo "Něco je špatně, nepodařilo se vytvořit účet"
fi
