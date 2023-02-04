""" The output (do the actual action based on the processed data, classified medias) module of the photos_classifier. """

###############################################################################

import pc_input

import logging
import datetime
import sys
import pandas
import numpy
import os
import shutil

###############################################################################

""" The date format to be used for the print in the histo output """
HISTO_DATE_FORMAT="%y-%m-%d"

""" The character to be used to output one picture in the histo output """
HISTO_CHAR="|"

""" The date format to be used for the group moved/copied photos directory. Can contain %COUNT to render the number of the files in the group """
GROUP_DIRNAME_DATE_FORMAT="%Y-%m-%d-having-%COUNT-files"

""" The scale of charecters going from 0 files to oo files """
SCALE_CHARS=" .,;!iILHM8%@#"

LOGGER = logging.getLogger("p_c")

###############################################################################

def range_the_dates(groups, include_empty):
    """ Returns the range of dates to iterate over in the given groups.
    If include_empty is true, returns all dates between the starting and ending.
    Otherwise just the dates of the groups. """

    if include_empty:
        min_date = min(groups.keys())
        if (min_date == pc_input.NO_DATE):
            min_date = sorted(groups.keys())[1]

        max_date = max(groups.keys())
        ranged = pandas.date_range(min_date, max_date)
        return map(lambda d: d.date(), ranged)
    else:
        dated = map(lambda d: d.date(), groups.keys())
        return sorted(set(dated))
    

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

def format_number_of_medias(files_count, frmt):
    """ Formats the given files_count based on the format """

    if frmt == "count":
        if files_count:  
            return "%4d" % (files_count)    
        else:
            return "%4s" % (".")
        
    if frmt == "simple_count":
        if files_count == 0:
            return "."
    
        if files_count > 9:
            return "+"
        
        return str(files_count)
    
    if frmt == "scale":
        scale_len = len(SCALE_CHARS)
        index = int(numpy.floor(scale_len * numpy.tanh(files_count / (1.2 * scale_len))))
        if index >= scale_len:
            index = scale_len - 1
        return SCALE_CHARS[index];


def print_by_hours(groups, include_empty_days = None, frmt = "count"):
    """ Prints the table days x hours, having number of photos in each cell """

    sys.stdout.write("%9s |" % ("hour"))
    for hour in range(0, 24):
        if frmt == "count":
            sys.stdout.write("%4d" % (hour))
        else:
            sys.stdout.write(str(hour % 10))

    sys.stdout.write("\n")

    dates_range = range_the_dates(groups, include_empty_days)
    for date in dates_range:
        date_str = date.strftime(HISTO_DATE_FORMAT)
        sys.stdout.write("%9s |" % (date_str))

        for hour in range(0, 24):
            datetimed = datetime.datetime.combine(date, datetime.time(hour, 0, 0))

            if datetimed in groups.keys():
                files_count = len(groups[datetimed])
            else:
                files_count = 0

            formated = format_number_of_medias(files_count, frmt)
            sys.stdout.write(formated)

        sys.stdout.write("\n")

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
        shutil.copy(media_file, group_dir)

    elif action == "move":
         LOGGER.debug(f"Moving {media_file} to {group_dir}")
         shutil.move(media_file, group_dir)

    else:
        raise Exception("Either copy or move is allowed")

