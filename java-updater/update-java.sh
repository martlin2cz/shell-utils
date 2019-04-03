#!/bin/bash
# by using update-alternatives installs given java version 
# with priority specified by YYMM of current date
# m@rtlin, 25.3.2019
#####################################################################
if [ $# == "0" ]; then echo "Usage: $0 NEW_JAVA_HOME_DIR_PATH"; exit 1; fi
if [ $(whoami) != "root" ]; then echo "Run as root, please"; exit 2; fi

# dir where the new java lays (homedir) (with ending slash)
JDK_DIR=$1
# priority in format YYMM
PRIORITY=$(date "+%y%m")

# the final target basedir (with ending slash)
TARGET_DIR=/usr/bin/
# which java programs to install
PROGRAMS="java javac javadoc jmap"

#####################################################################
echo "Installing $JDK_DIR with priority $PRIORITY:"

for PROGRAM in $PROGRAMS; do
	echo "Installing $PROGRAM ..."
	
	TARGET="$TARGET_DIR""$PROGRAM"
	JDK_PATH=$(pwd)"/$JDK_DIR""bin/""$PROGRAM"
	
	update-alternatives --install $TARGET $PROGRAM $JDK_PATH $PRIORITY
done

echo "Installed, see:"
java -version

exit 0
