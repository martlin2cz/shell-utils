#!/usr/bin/python3.8
#
# An tool for classifing the photos semi-automatically/partially
# by the date taken
#
# m@rtlin, 29.12.2022
# Requirements: exifread

#import exifread
#import datetime
#
#import shutil
#import logging
#
#import pandas
#import ffmpeg
#import sys
#import numpy

import pc_input
import pc_process
import pc_output

import logging
import argparse
import os

###############################################################################

LOGGER = logging.getLogger("p_c")

def doit(directory, recurse, action, include_empty = False, quora = None, destination = None, display_format = "count"):
    """ Does the actual action with the given directory (possibly recursivelly), with the optional quora and destination) """
    groups = None
    if action == "hours":
        groups = pc_process.load_and_group_by_day_and_hour(directory, recurse)
    else:
        groups = pc_process.load_and_group_by_date(directory, recurse)

    if action == "histo":
        pc_output.print_date_histogram(groups, include_empty, quora)

    if action == "list":
        pc_output.print_files_by_date(groups, include_empty)

    if action == "copy" or action == "move":
        pc_output.copy_or_move(groups, quora, action, destination)

    if action == "hours":
        pc_output.print_by_hours(groups, include_empty, display_format)

def check_args(parsed_args):
    """ Validates the provided args """

    if not os.path.isdir(parsed_args.directory):
        raise ValueError(f"The {parsed_args.directory} is not a directory")

    if parsed_args.destination and not os.path.isdir(parsed_args.destination):
        raise ValueError(f"The {parsed_args.destination} is not a directory")


def configure_logging(verbose, debug):
    """ Sets the logger configuration based on the command line flags """

    exif_logger = logging.getLogger("exifread")
    exif_logger.setLevel(logging.ERROR)

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
        choices = ["list", "histo", "copy", "move", "hours"], 
        default = "histo",
        help = "What to do with the result. Just output the date->files mapping ('list'), "
        + "show a histogram (date->number of files) ('histo', DEFAULT), show table day x hour x number of photos ('hours') or copy ('copy') or move ('move') the files into folder for each day?")

parser.add_argument("-r", "--recursive", action = "store_true",
        help = "If set, will look for the photo/video files in the DIRECTORY recursivelly")

parser.add_argument("-q", "--quora", action = "store", type = int,
        help = "Specifies what amount of photos/videos per day starts to be interresting (smaller amount ignores the day by -a=copy and -a=move)")

parser.add_argument("-e", "--include-empty", action = "store_true", dest = "include_empty",
        help = "When -a=list or -a=histo, output for all days (even the ones with no photos/videos at all) (otherwise days having at least one)")

parser.add_argument("-d", "--destination", action = "store",
        help = "When -a=copy or -a=move set, specifies where to copy/move the files to (their owning group dirs)")

parser.add_argument("-f", "--display-format", action = "store",
        choices = ["count", "simple_count", "scale"],
        default = "scale",
        help = "When -a=hours, specifies whether to print the number of medias ('count') count as 0-9 (or +) ('simple_count') or character scale ('scale') (DEFAULT)")

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
    doit(parsed.directory, parsed.recursive, parsed.action, parsed.include_empty, parsed.quora, parsed.destination, parsed.display_format)

#    print(date_of_photo("testing-images/detaily-o-zasilce.jpg"))
#    print(date_of_photo("testing-images/kus-qeerka.jpg"))
#    print(list_files("testing-images", False))
#    print(list_files(".", True))
#    print(load_and_group("testing-images", True))
#    logging.basicConfig(level = logging.INFO, format="%(asctime)s %(levelname)8s %(name)s %(message)s")
#    LOGGER.setLevel(logging.DEBUG)
#    print(run("testing-images", True))
#    print(parser.parse_args(["-v", "--debug", "--quora", "42", "foobar"]))
#   print(list(map(lambda n: format_number_of_medias(n, "scale"), range(0,60))))
