#!/bin/bash
# Copies all contents from CD to specified location
# m@rtlin, 26.11.2018

#######################################

# the source (the cd) (without the leading /, please)
FROM=/media/cdrom0

# the target (the external, or internal drive, and its sub-folder) (without the leading /, please)
TO=/media/$(whoami)/Janča/janča/audioknihy

# the readme file name
READMENAME=cojeto.txt

######################################

# check the input
if [ "$#" != "2" ] ; then
	echo "Použití: $0 \"<AUTOR>\" \"<NAZEV>\""
	exit 1
fi

# name of the author of the content
AUTHOR=$1

# title of the cotent
TITLE=$2

######################################

# construct dirname for the target
DIRNAME=$(echo "$AUTHOR - $TITLE" | iconv -f utf8 -t ascii//TRANSLIT | sed -r "s/[ ,_]/_/g")

# create target dir
TARGET=$TO'/'$DIRNAME
mkdir $TARGET

# do the copy
SOURCE=$FROM'/*'
cp -rv $SOURCE $TARGET

# create the readme file
READMEFILE=$TARGET'/'$READMENAME
echo -e "AUTOR: $AUTHOR\nTITUL: $TITLE\nZDROJ: K. M. P." > $READMEFILE

# okay?
echo Zkopírováno do $DIRNAME !
eject

exit 0
