#!/bin/bash
#m@rtlin, 20. rij 2014
#stahne .deb soubor baliku $1

DEBIAN=wheezy
ARCH=i386
MIRROR=cz

package=$1
#############################
echo fetching mirrors list for $package
wget -q -O package-download-page.html https://packages.debian.org/$DEBIAN/$ARCH/$package/download || exit 1

url=$(cat package-download-page.html | grep ftp.$MIRROR.debian.org | sed -r 's!([^<]*)<li><a href="([^"]+)">(.*)!\2!')
rm package-download-page.html

if [ "$url" == "" ]; then
	echo "package $package not recognized" > /dev/stderr
	exit 3
fi

echo downloading $url
wget -q $url || exit 2

echo done
exit 0
