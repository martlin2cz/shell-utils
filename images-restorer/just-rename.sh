#!/bin/bash
# images-restorer
# m@rtlin, 19.3.2017
#
# For given list of all JPEG files 
# into $1 (with ending slash please) renamed using the filename pattern $PATTERN.
# 
# ./doit.sh <output_dir> [<file(s)_1> [<file(s)_2> [... <file(s)_n>]]]
###############################################################################

## output file name format pattern ( https://www.imagemagick.org/script/escape.php )
OUTPUT_FORMAT="photo_%[EXIF:DateTime].%e"
###############################################################################

## output directory
if [ "$1" == "" ]; then
	echo "Empty output directory, exiting..."
	exit 1
else
	OUTDIR=$1
	shift
fi

## files
FILES=$*

## echo "verbose? $VERBOSE, outdir? $OUTDIR, files: $FILES ."
###############################################################################
ALL_COUNT=$((0))


for FILE in $FILES; do
	ALL_COUNT=$((ALL_COUNT+1))
	
	OUTPUT_FILENAME=$(convert $FILE -print "$OUTPUT_FORMAT\n" /dev/null)
	OUTPUT_PATH="$OUTDIR""$OUTPUT_FILENAME"

	echo "Doing file $FILE, outputing as $OUTPUT_FILENAME"
	MATCH_COUNT=$((MATCH_COUNT+1))
	cp $FILE "$OUTPUT_PATH"
done

###############################################################################
echo "Processed $ALL_COUNT files"
exit 0
