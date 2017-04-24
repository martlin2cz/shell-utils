#/bin/bash
#m@rtlin, 20. rij 2014
# balíku $1 zjistí seznam závislostí a ty všechny stáhne do .

package=$1
#######################################

deps=$(apt-cache depends $package | grep "Závisí" | sed -r 's! [ \|]Závisí na: !!')

echo -e package $package depends on: "\n"$deps

deps="$package $deps"

for pkg in $deps; do
	echo "downloading $pkg ..."
	./download_deb.sh $pkg > /dev/null
done

echo done
exit 0

