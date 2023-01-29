#!/usr/bin/python3.8
#
# An tool for classifing the photos semi-automatically/partially
# by the date taken
#
# m@rtlin, 29.12.2022
# Requirements: exifread

import exifread
import datetime
import os
import shutil
import logging
import argparse
import pandas
import ffmpeg

###############################################################################

""" The date format to be used for the print in the histo output """
HISTO_DATE_FORMAT="%y-%m-%d"

""" The character to be used to output one picture in the histo output """
HISTO_CHAR="|"

""" The date format to be used for the group moved/copied photos directory. Can contain %COUNT to render the number of the files in the group """
GROUP_DIRNAME_DATE_FORMAT="%Y-%m-%d-having-%COUNT-files"

""" The indicator of no date avaiable (do not use None, causes ton of issues) """
NO_DATE=datetime.date(1970, 1, 1)

###############################################################################

LOGGER = logging.getLogger("p_c")

def datetime_of_photo_raw(photo_file):
    """ Returns the datetime of the photo taken at, as raw exif data """

    with open(photo_file, 'rb') as fh:
        tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
        if "EXIF DateTimeOriginal" in tags.keys():
            return tags["EXIF DateTimeOriginal"]

        if "EXIF DateTimeDigitized" in tags.keys():
            return tags["EXIF DateTimeDigitized"]

        if "Image DateTime" in tags.keys():
            return tags["Image DateTime"]

        raise ValueError(f"The file {photo_file} doesn't contain timestamp")

def date_of_photo(photo_file):
    """ Returns the actual DATE of the photo taken at, but as datetime date object """ 

    try:
        LOGGER.debug(f"Loading date taken of photo {photo_file}")
        raw_datetime = datetime_of_photo_raw(photo_file)
        actual_datetime = datetime.datetime.strptime(str(raw_datetime), "%Y:%m:%d %H:%M:%S")
        return actual_datetime.date()
    except Exception:
        LOGGER.debug(f"Date of photo {photo_file} obtain failed")
        return NO_DATE


def datetime_of_video_raw(video_file):
    """ Returns the datetime of the video shot at, as a raw string """

    video_metadata = ffmpeg.probe(media_file)
    for stream in video["streams"]:
        if "tags" in keys(stream):
            tags = stream["tags"]
            if "creation_time" in tags:
                return tags["creation_time"]
 
def date_of_video(video_file):
    """ Returns the actual DATE of the video shot at, but as datetime date object """ 

    try:
        LOGGER.debug(f"Loading date taken of video {video_file}")
        raw_datetime = datetime_of_video_raw(video_file)
        actual_datetime = datetime.datetime.strptime(str(raw_datetime), "%Y:%m:%d %H:%M:%S")
        return actual_datetime.date()
    except Exception:
        LOGGER.debug(f"Date of video {video_file} obtain failed")
        return NO_DATE
   

def date_of_media(media_file):
    """ Returns the actual DATE of the photo/video taken at, as datetime date object """ 

    LOGGER.debug(f"Loading date taken/shot of {media_file}")
        
    date = date_of_photo(media_file)
    if date:
        return date

    date = date_of_video(media_file)
    if date:
        return date

    LOGGER.error(f"Date of media {video_file} obtain failed")
    return NO_DATE

def list_files(directory, recurse):
    """ Lists all the files in the given directory, possibly recurring """

    #TODO ensure existence

    result = []
    for (dirpath, dirs, files) in os.walk(directory):
        LOGGER.debug(f"Loaded files {files} in dir {dirpath}")
        #TODO filter files by extension
        files_resolved = [os.path.join(dirpath, f) for f in files]
        result.extend(files_resolved)
        if not recurse:
            break

    return result

def load(directory, recurse):
    """ Loads the medias and their date of taken into file->date dict"""

    files = list_files(directory, recurse)
    files_count = len(files)
    LOGGER.info(f"Loaded {files_count} media files")

    with_dates = dict(map( lambda f: (f, date_of_media(f)), files))
    LOGGER.info(f"Loaded dates of taken of the loaded medias")
    return with_dates

def load_and_group(directory, recurse):
    """ Loads the medias in the given directory and groups them by date of taken """

    files = load(directory, recurse)
    files_count = len(files)

    result = {}
    for media_file in files.keys():
        date = files[media_file]
        group_of_date = None

        if date in result.keys():
            LOGGER.debug(f"Inserting {media_file} into existing group {date}")
            group_of_date = result[date]
        else:
            LOGGER.debug(f"Creating new group {date} for {media_file}")
            group_of_date = []
            result[date] = group_of_date

        group_of_date.append(media_file)

    groups_count = len(result)
    LOGGER.info(f"Collected {groups_count} groups, averaging {files_count / groups_count} medias per group")

    return result

def range_the_dates(groups, include_empty):
    """ Returns the range of dates to iterate over in the given groups.
    If include_empty is true, returns all dates between the starting and ending.
    Otherwise just the dates of the groups. """

    if include_empty:
        min_date = min(groups.keys())
        if (min_date == NO_DATE):
            min_date = sorted(groups.keys())[1]

        max_date = max(groups.keys())
        ranged = pandas.date_range(min_date, max_date)
        return map(lambda d: d.date(), ranged)
    else:
        return sorted(groups.keys())
    

def print_date_histogram(groups, include_empty = None, quora = None):
    """ Prints the symbolic histogram of date->number of medias """

    if quora:
        quora_bar_str = HISTO_CHAR * quora
        print("%9s : %s" % ("quora", quora_bar_str))
    
    dates_range = range_the_dates(groups, include_empty)
    for date in dates_range:
        date_str = date.strftime(HISTO_DATE_FORMAT)
        if date in groups.keys():
            files_count = len(groups[date])
        else:
            files_count = 0

        bar_str = HISTO_CHAR * files_count
        print("%9s : %s" % (date_str, bar_str))

def print_files_by_date(groups, include_empty):
    """ Prints just the date->list of files """

    dates_range = range_the_dates(groups, include_empty)
    for date in dates_range:
        date_str = date.strftime(HISTO_DATE_FORMAT)

        if date in groups.keys():
            files = groups[date]
        else:
            files = []

        print(date_str + " -> " + str(files))

def copy_or_move(groups, quora, action, target_owner):
    """ Copies or moves the medias in groups excessing the quora into the specified target dir """

    for date in groups.keys():
        group_files = groups[date]
        files_count = len(group_files) 
        
        if quora and files_count < quora:
            LOGGER.debug(f"The group {date} has less than {quora} medias, skipping")
             # TODO: if not above the quora, simply ignore?
        else:
            LOGGER.debug(f"The group {date} has exceeded the {quora} quora, processing then")
            dirname = GROUP_DIRNAME_DATE_FORMAT.replace("%COUNT", str(files_count));
            dirname = date.strftime(dirname)

            group_dir = os.path.join(target_owner, dirname)
            os.makedirs(group_dir)

            for media_file in group_files:
                copy_or_move_file(media_file, action, group_dir)

def copy_or_move_file(media_file, action, group_dir):
    """ Copies or moves the given file (based on action) into the given target dir) """

    if action == "copy":
        LOGGER.debug(f"Copiing {media_file} to {group_dir}")
        shutil.copy(photo_file, group_dir)

    elif action == "move":
         LOGGER.debug(f"Moving {media_file} to {group_dir}")
         shutil.move(photo_file, group_dir)

    else:
        raise Exception("Either copy or move is allowed")

def _run(directories, recurse):
    """ Does some action (method for debug/testing purposes) """

    groups = load_and_group(directories, recurse)
    print("uncomment me")
    #print_date_histogram(groups, 2)
    #copy_or_move(groups, 2, "copy", "/tmp/photos-1")

def doit(directory, recurse, action, include_empty = False, quora = None, destination = None):
    """ Does the actual action with the given directory (possibly recursivelly), with the optional quora and destination) """
    groups = load_and_group(directory, recurse)

    if action == "histo":
        print_date_histogram(groups, include_empty, quora)

    if action == "list":
        print_files_by_date(groups, include_empty)

    if action == "copy" or action == "move":
        copy_or_move(groups, quora, action, destination)

def check_args(parsed_args):
    """ Validates the provided args """

    if not os.path.isdir(parsed_args.directory):
        raise ValueError(f"The {parsed_args.directory} is not a directory")

    if parsed_args.destination and not os.path.isdir(parsed_args.destination):
        raise ValueError(f"The {parsed_args.destination} is not a directory")


def configure_logging(verbose, debug):
    """ Sets the logger configuration based on the command line flags """

    if not (verbose or debug):
        return
    
    if verbose:
        new_level = logging.INFO

    if debug:
        new_level = logging.DEBUG

    logging.basicConfig(level = logging.INFO, format="%(asctime)s %(levelname)8s %(name)s %(message)s")
    LOGGER.setLevel(new_level)

###############################################################################

parser = argparse.ArgumentParser(
        description = "Classifies (by coping, moving, or just outputting to console) photos or videos (or possibly any other media file, based on its format) by date (day)")

parser.add_argument("-a", "--action", action = "store",
        choices = ["list", "histo", "copy", "move"], 
        default = "histo",
        help = "What to do with the result. Just output the date->files mapping, show a histogram (date->number of files) (DEFAULT) or copy or move the files into folder for each day?")

parser.add_argument("-r", "--recursive", action = "store_true",
        help = "If set, will look for the photo/video files in the DIRECTORY recursivelly")

parser.add_argument("-q", "--quora", action = "store", type = int,
        help = "Specifies what amount of photos/videos per day starts to be interresting (smaller amount ignores the day by -a=copy and -a=move)")

parser.add_argument("-e", "--include-empty", action = "store_true", dest = "include_empty",
        help = "When -a=list or -a=histo, output for all days (even the ones with no photos/videos at all) (otherwise days having at least one)")

parser.add_argument("-d", "--destination", action = "store",
        help = "When -a=copy or -a=move set, specifies where to copy/move the files to (their owning group dirs)")

parser.add_argument("-v", "--verbose", action = "store_true",
        help = "Enables verbose output")

parser.add_argument("-D", "--debug", action = "store_true",
        help = "Enables full debug output")

parser.add_argument("directory", metavar = "DIRECTORY",
        help = "The directory to scan for the photo/video files (either --recursive or not)")

if __name__ == "__main__":
    parsed = parser.parse_args()
    check_args(parsed)
    configure_logging(parsed.verbose, parsed.debug)
    doit(parsed.directory, parsed.recursive, parsed.action, parsed.include_empty, parsed.quora, parsed.destination)

#    print(date_of_photo("testing-images/detaily-o-zasilce.jpg"))
#    print(date_of_photo("testing-images/kus-qeerka.jpg"))
#    print(list_files("testing-images", False))
#    print(list_files(".", True))
#    print(load_and_group("testing-images", True))
#    logging.basicConfig(level = logging.INFO, format="%(asctime)s %(levelname)8s %(name)s %(message)s")
#    LOGGER.setLevel(logging.DEBUG)
#    print(run("testing-images", True))
#    print(parser.parse_args(["-v", "--debug", "--quora", "42", "foobar"]))
 
