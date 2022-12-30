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
    
    for date in sorted(groups.keys()):
        date_str = date.strftime(HISTO_DATE_FORMAT)
        files_count = len(groups[date])
        bar_str = HISTO_CHAR * files_count
        print("%9s : %s" % (date_str, bar_str))

def copy_or_move(groups, quora, action, target_owner):
    """ Copies or moves the photos in groups excessing the quora into the specified target dir """

    for date in groups.keys():
        files_count = len(groups[date]) 
        if files_count < quora:
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

def run(directories, recurse):
    groups = load_and_group(directories, recurse)
    print_date_histogram(groups, 2)
    #copy_or_move(groups, 2, "copy", "/tmp/photos-1")

###############################################################################

if __name__ == "__main__":
#    print(date_of_photo("testing-images/detaily-o-zasilce.jpg"))
#    print(date_of_photo("testing-images/kus-qeerka.jpg"))
#    print(list_files("testing-images", False))
#    print(list_files(".", True))
#    print(load_and_group("testing-images", True))
     logging.basicConfig(level = logging.INFO)
     LOGGER.setLevel(logging.DEBUG)
     #print(LOGGER)
     print(run("testing-images", True))


 
