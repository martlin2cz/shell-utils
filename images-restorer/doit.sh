#!/bin/bash
# images-restorer
# m@rtlin, 19.3.2017
#
# For given list of all files (whatever, images, txts, xmls, audio/video, ...)
# copies JPEG photos (i.e. images captured by model = $MODEL) 
# into $1 (with ending slash please) renamed using the filename pattern $PATTERN.
# 
# ./doit.sh <output_dir> [<file(s)_1> [<file(s)_2> [... <file(s)_n>]]]
###############################################################################

## media type specifier
MODEL="Lenovo A1000"

## regex of expected JPEG image to match output from program file
REGEX="JPEG image data, Exif standard: \[(.+ )?model=$MODEL( .+)?\]"

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
MATCH_COUNT=$((0))
MISS_COUNT=$((0))
ALL_COUNT=$((0))


for FILE in $FILES; do
	ALL_COUNT=$((ALL_COUNT+1))
	
	FILE_REGEX="$FILE: $REGEX"
	MATCH=$(file $FILE | grep -E "$FILE_REGEX")
	
	if [ "$MATCH" != "" ] ; then
		OUTPUT_FILENAME=$(convert $FILE -print "$OUTPUT_FORMAT\n" /dev/null)
		OUTPUT_PATH="$OUTDIR""$OUTPUT_FILENAME"

		echo "MATCH $FILE, outputing as $OUTPUT_FILENAME"
		MATCH_COUNT=$((MATCH_COUNT+1))
		cp $FILE "$OUTPUT_PATH"
	else
		echo "MISS  $FILE"
		MISS_COUNT=$((MISS_COUNT+1))
	fi
done

###############################################################################
echo "Processed $ALL_COUNT files, matched $MATCH_COUNT, missed $MISS_COUNT"
exit 0
