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

###############################################################################

""" The date format to be used for the print in the histo output """
HISTO_DATE_FORMAT="%y-%m-%d"

""" The character to be used to output one picture in the histo output """
HISTO_CHAR="|"

""" The date format to be used for the group moved/copied photos directory """
GROUP_DIRNAME_DATE_FORMAT="%y-%m-%d-unknown"


###############################################################################

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

        return None

def date_of_photo(photo_file):
    """ Returns the actual DATE of the photo taken at, but as datetime date object """ 
    #TODO try-catch the raw procedure
    raw_datetime = datetime_of_photo_raw(photo_file)
    actual_datetime = datetime.datetime.strptime(str(raw_datetime), "%Y:%m:%d %H:%M:%S")
    return actual_datetime.date()
    
def list_files(directory, recurse):
    """ Lists all the files in the given directory, possibly recurring """

    result = []
    for (dirpath, dirs, files) in os.walk(directory):
        #TODO filter files by extension
        files_resolved = [os.path.join(dirpath, f) for f in files]
        result.extend(files_resolved)
        if not recurse:
            break

    return result

def load_and_group(directory, recurse):
    """ Loads the photos in the given directory and groups them by date of taken """
    files = list_files(directory, recurse)

    result = {}
    for photo_file in files:
        date = date_of_photo(photo_file)
        group_of_date = []

        if date in result.keys():
            group_of_date = result[date]
        else:
            result[date] = group_of_date

        group_of_date.append(photo_file)

    return result

def print_date_histogram(groups):
    """ Prints the symbolic histogram of date->number of photos """

    for date in sorted(groups.keys()):
        date_str = date.strftime(HISTO_DATE_FORMAT)
        files_count = len(groups[date])
        bar_str = HISTO_CHAR * files_count
        print(date_str + " : " + bar_str)

def copy_or_move(groups, quora, action, target_owner):
    """ Copies or moves the photos in groups excessing the quora into the specified target dir """

    for date in groups.keys():
        files_count = len(groups[date]) 
        if files_count >= quora:
            # TODO: if not above the quora, simply ignore?
            dirname = date.strftime(GROUP_DIRNAME_DATE_FORMAT)
            group_dir = os.path.join(target_owner, dirname)
            os.makedirs(group_dir)

            files = groups[date]
            for photo_file in files:
                copy_or_move_file(photo_file, action, group_dir)

def copy_or_move_file(photo_file, action, group_dir):
    """ Copies or moves the given file (based on action) into the given target dir) """

    if action == "copy":
        shutil.copy(photo_file, group_dir)

    elif action == "move":
        shutil.move(photo_file, group_dir)

    else:
        raise Exception("Either copy or move is allowed")

def run(directories, recurse):
    groups = load_and_group(directories, recurse)
    #print_date_histogram(groups)
    copy_or_move(groups, 2, "copy", "/tmp/photos-1")

###############################################################################

if __name__ == "__main__":
#    print(date_of_photo("testing-images/detaily-o-zasilce.jpg"))
#    print(date_of_photo("testing-images/kus-qeerka.jpg"))
#    print(list_files("testing-images", False))
#    print(list_files(".", True))
#    print(load_and_group("testing-images", True))
     print(run("testing-images", True))


 
