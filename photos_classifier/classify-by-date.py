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

###############################################################################

""" The date format to be used for the print in the histo output """
HISTO_DATE_FORMAT="%y-%m-%d"

""" The character to be used to output one picture in the histo output """
HISTO_CHAR="|"

""" The date format to be used for the group moved/copied photos directory """
GROUP_DIRNAME_DATE_FORMAT="%y-%m-%d-unknown"


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
        LOGGER.debug(f"Loading date taken of {photo_file}")
        raw_datetime = datetime_of_photo_raw(photo_file)
        actual_datetime = datetime.datetime.strptime(str(raw_datetime), "%Y:%m:%d %H:%M:%S")
        return actual_datetime.date()
    except Exception:
        LOGGER.error(f"Date of photo {photo_file} obtain failed")
        return datetime.date(1970, 1, 1)
       
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
    """ Loads the photos and their date of taken into file->date dict"""

    files = list_files(directory, recurse)
    files_count = len(files)
    LOGGER.info(f"Loaded {files_count} photo files")

    with_dates = dict(map( lambda f: (f, date_of_photo(f)), files))
    LOGGER.info(f"Loaded dates of taken of the loaded photos")
    return with_dates

def load_and_group(directory, recurse):
    """ Loads the photos in the given directory and groups them by date of taken """

    files = load(directory, recurse)
    files_count = len(files)

    result = {}
    for photo_file in files.keys():
        date = files[photo_file]
        group_of_date = None

        if date in result.keys():
            LOGGER.debug(f"Inserting {photo_file} into existing group {date}")
            group_of_date = result[date]
        else:
            LOGGER.debug(f"Creating new group {date} for {photo_file}")
            group_of_date = []
            result[date] = group_of_date

        group_of_date.append(photo_file)

    groups_count = len(result)
    LOGGER.info(f"Collected {groups_count} groups, averaging {files_count / groups_count} photos per group")

    return result

def print_date_histogram(groups, quora = None):
    """ Prints the symbolic histogram of date->number of photos """

    if quora:
        quora_bar_str = HISTO_CHAR * quora
        print("%9s : %s" % ("quora", quora_bar_str))
    
    #TODO print all dates from first to last, if specified
    for date in groups.keys():
        date_str = date.strftime(HISTO_DATE_FORMAT)
        files_count = len(groups[date])
        bar_str = HISTO_CHAR * files_count
        print("%9s : %s" % (date_str, bar_str))

def print_files_by_date(groups):
    """ Prints just the date->list of files """

    for date in sorted(groups.keys()):
        date_str = date.strftime(HISTO_DATE_FORMAT)
        files = groups[date]
        print(date_str + " -> " + str(files))

def copy_or_move(groups, quora, action, target_owner):
    """ Copies or moves the photos in groups excessing the quora into the specified target dir """

    for date in groups.keys():
        files_count = len(groups[date]) 
        
        if quora and files_count < quora:
            LOGGER.debug(f"The group {date} has less than {quora} photos, skipping")
             # TODO: if not above the quora, simply ignore?
        else:
            LOGGER.debug(f"The group {date} has exceeded the {quora} quora, processing then")
            dirname = date.strftime(GROUP_DIRNAME_DATE_FORMAT)
            group_dir = os.path.join(target_owner, dirname)
            os.makedirs(group_dir)

            files = groups[date]
            for photo_file in files:
                copy_or_move_file(photo_file, action, group_dir)

def copy_or_move_file(photo_file, action, group_dir):
    """ Copies or moves the given file (based on action) into the given target dir) """

    if action == "copy":
        LOGGER.debug(f"Copiing {photo_file} to {group_dir}")
        shutil.copy(photo_file, group_dir)

    elif action == "move":
         LOGGER.debug(f"Moving {photo_file} to {group_dir}")
         shutil.move(photo_file, group_dir)

    else:
        raise Exception("Either copy or move is allowed")

def _run(directories, recurse):
    """ Does some action (method for debug/testing purposes) """

    groups = load_and_group(directories, recurse)
    print("uncomment me")
    #print_date_histogram(groups, 2)
    #copy_or_move(groups, 2, "copy", "/tmp/photos-1")

def doit(directory, recurse, action, quora = None, destination = None):
    """ Does the actual action with the given directory (possibly recursivelly), with the optional quora and destination) """
    groups = load_and_group(directory, recurse)

    if action == "histo":
        print_date_histogram(groups, quora)

    if action == "list":
        print_files_by_date(groups)

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
        description = "Classifies (by coping, moving, or just outputting to console) photos by date (day)")

parser.add_argument("-a", "--action", action = "store",
        choices = ["list", "histo", "copy", "move"], 
        default = "histo",
        help = "What to do with the result. Just output the date->files mapping, show a histogram (date->number of files) (DEFAULT) or copy or move the files into folder for each day?")

parser.add_argument("-r", "--recursive", action = "store_true",
        help = "If set, will look for the photo files in the DIRECTORY recursivelly")

parser.add_argument("-q", "--quora", action = "store", type = int,
        help = "Specifies what amount of photos per day starts to be interresting (smaller amount ignores the day by -a=copy and -a=move)")

parser.add_argument("-d", "--destination", action = "store",
        help = "When -a=copy or -a=move set, specifies where to copy/move the files to (their owning group dirs)")

parser.add_argument("-v", "--verbose", action = "store_true",
        help = "Enables verbose output")

parser.add_argument("-D", "--debug", action = "store_true",
        help = "Enables full debug output")

parser.add_argument("directory", metavar = "DIRECTORY",
        help = "The directory to scan for the photo files (either --recursive or not)")

if __name__ == "__main__":
    parsed = parser.parse_args()
    check_args(parsed)
    configure_logging(parsed.verbose, parsed.debug)
    doit(parsed.directory, parsed.recursive, parsed.action, parsed.quora, parsed.destination)

#    print(date_of_photo("testing-images/detaily-o-zasilce.jpg"))
#    print(date_of_photo("testing-images/kus-qeerka.jpg"))
#    print(list_files("testing-images", False))
#    print(list_files(".", True))
#    print(load_and_group("testing-images", True))
#    logging.basicConfig(level = logging.INFO, format="%(asctime)s %(levelname)8s %(name)s %(message)s")
#    LOGGER.setLevel(logging.DEBUG)
#    print(run("testing-images", True))
#    print(parser.parse_args(["-v", "--debug", "--quora", "42", "foobar"]))
 
