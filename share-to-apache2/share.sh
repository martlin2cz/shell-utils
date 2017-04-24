#!/bin/bash
#Nasdílí soubor, nebo jen vypíše mou IP adresu na interface
#Nasdílení obnáší zkopírovaní souboru do složky SERVER_DIR/SHARE_DIR_NAME/<datum>/soubor
#(Volitleně lze zadat dest_name souboru a rozhraní, viz -h / --help)
#a vypsání odkazu na soubor v LAN

# m@rtlin, 2. dub. 2013, v1.2 (update 10. črc. 2013)

###############################################################################
#Verze aplikace
VERSION="1."

# Adresa rozhraní
DFLT_INTRFC="wlan0"

# Přepínač pro rozhraní
INTRFC_SW_SH="-i"
INTRFC_SW_LNG="--interface"

# Interní značení pro filtry, ideálněněco unikátního ...
IP_ADDR_FLAG="MOJE IPA: "

# Kořenový adresář webu s konocvým lomítkem.
SERVER_DIR="/var/www/"

# Název složky bez konc. lomítka, kde se budou ukládat soubory ke sdílení. Musí existovat v SERVER_DIR
SHARE_DIR_NAME="share"

###############################################################################
show_help() {
	echo "Apache Share app $VERSION"
	echo -e "$0 \n\t[$INTRFC_SW_SH | $INTRFC_SW_LG interface] \n\t[$INTRFC_SW_SH | $INTRFC_SW_LG interface] filename\n\t[$INTRFC_SW_SH | $INTRFC_SW_LG interface] filename destname\n\t"
	echo "Will copy file to share directory and print link to share"
	echo "Default interface is $DFLT_INTRFC, an be redefined by $INTRFC_SW_SH or $INTRFC_SW_LNG"
	echo "No files - only show $interface IP addr."
	exit 0
}

###############################################################################

if ( [ "$1" == "-h" ] || [ "$1" == "--help" ] ); then
	show_help
fi



interface=$DFLT_INTRFC
if ( [ "$1" == "$INTRFC_SW_SH" ] || [ "$1" == "$INTRFC_SW_LNG" ] ); then
	interface=$2
	shift 2
fi

filename=$1
dest_filename=$2

###############################################################################

my_ip=$(ip addr show $interface | 
	sed -r "s/(([[:digit:]]{1,3})\.){3}([[:digit:]]{1,3})/\n$IP_ADDR_FLAG\0\n/g" |
	grep "$IP_ADDR_FLAG" | 
	sed "s/$IP_ADDR_FLAG//" | 
	head -n 1)

if [ "$my_ip" == "" ]; then
	echo "Something is wrong, cannot get you IP Adress"
	exit 2
fi
###############################################################################

# Pouhé vypsání IP adresy, nebo jen nápověda
if [ "$filename" == "" ]; then
	echo "Your IP at $interface is: $my_ip"
	exit 0
fi

if ( [ "$1" == "-h" ] || [ "$1" == "--help" ] ); then
	show_help
fi

if [ "$dest_filename" == "" ]; then
	dest_filename=$filename
fi

#Pomocné určování
new_dir_name=$(date +%y%m%d)

# Odtestování a vytvoření složky na sdílení
share_dir_full=$SERVER_DIR$SHARE_DIR_NAME/$new_dir_name
(ls $share_dir_full > /dev/null 2>&1) || mkdir $share_dir_full

# Zkopírování souboru
cp $filename $share_dir_full/$dest_filename || exit 1
chmod 755 $share_dir_full/$dest_filename

#Vygenerování odkazu
link=http://$my_ip/$SHARE_DIR_NAME/$new_dir_name/$dest_filename
echo -e "File is avaible at link:\n $link"

exit 0
