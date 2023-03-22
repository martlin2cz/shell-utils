""" The argparse module implementation. Takes the command-line args and converts them to the detailed structed object. """

###############################################################################

import pc_output
import pc_classifier

import logging
import argparse
import os


###############################################################################

""" The logger. """
LOGGER = logging.getLogger("p_c")

###############################################################################

def parse_args(args):
    """ Parses the actual given args. Returns the object containing all the properties, 'action' indicating what to do. """

    parser = construct_parser()
    
    parsed = parser.parse_args(args)

    configure_logging(parsed.verbose, parsed.debug)
    check_args(parsed)

    return parsed

###############################################################################

def construct_parser():
    parser = argparse.ArgumentParser(
            description = "Classifies (groups) (by coping, moving, or just outputting to console in various forms) photos or videos (or possibly any other media files, based on their format) by date (or time) with particular granularity (years, month, weeks, days, hours). For example, collects all the photos across the years and groups them by the 'month' and outputs in the 'histo' format to see nice histogram of how many photos was taken at each of such month. Or, takes directory full of unordered photos and separates them (by moving) into the directories based on the 'day' they've been taken at.")


    subparsers = parser.add_subparsers(dest = "action", help = "Specify the the format of the printed output (list or table) or action to perform (copy or move).")

    construct_list_sub_parse(subparsers)
    construct_table_sub_parse(subparsers)
    construct_copy_or_move_sub_parse(subparsers, "copy")
    construct_copy_or_move_sub_parse(subparsers, "move")
    construct_dump_sub_parse(subparsers)

    return parser

def construct_list_sub_parse(subparsers):
    parser = subparsers.add_parser("list", help = "Lists (outputs in a list format, each group per line) the groups with specified --row-format of each group and other extra configuring args.")

    parser.add_argument("-f", "--row-format", action = "store", dest = "row_format",
            choices = ["list", "count", "simple-count", "histo", "scale"],
            default = "histo",
            help = "Specifies the format of how to output the medias of the group. Value 'list' just literally lists the medias (the file names), 'count' ouputs the count of the medias, 'simple-count' outputs (0-9, then + then *), 'histo' outputs progressbar, and 'scale' means particular ASCI art scale character (ranging usually from blank space to some dark character like # or M. Can be changed by --scale). Default is 'histo'.")

    parser.add_argument("-e", "--include-empty", action = "store_true", dest = "include_empty",
            help = "Output for all groups (even the ones with no medias at all) from the first to last, or just the ones having at least one media per group?")

    parser.add_argument("-rq", "--remove-quora", action = "store", type = int, dest = "remove_quora",
            help = "Hides from the output all the groups having less than given number of medias.")

    parser.add_argument("-oq", "--output-quora", action = "store", type = int, dest = "output_quora",
            help = "Indicates in the output given number of medias. Usefull in combination with --row-format=histo.")

    parser.add_argument("-s", "--scale", action = "store", default = pc_output.DEFAULT_SCALE_CHARS,
            help = "Use the custom scale for the --row-format='scale'. First character indicates zero medias, second indicates one media, the rest goes gradualy up to infinity. Example: '_xX#'")

    add_common_arguments(parser)


def construct_table_sub_parse(subparsers):
    parser = subparsers.add_parser("table", help = "Outputs int the table format (rows are groupped by the --groupper, columns are then their corresponding subgroups). How each of the cells looks like is given by --cell-format and other extra configuring args.")

    parser.add_argument("-f", "--cell-format", action = "store", dest = "cell_format",
            choices = ["count", "scale"],
            default = "scale",
            help = "Specifies how to ouput number of medias in the corresponding group and subgroup. The 'count' means just the number (either full or simplified, based on --compact), 'scale' means particular ASCI art scale character (ranging usually from blank space to some dark character like # or M. Can be changed by --scale). Default is 'scale'.")

    parser.add_argument("-e", "--include-empty", action = "store_true", dest = "include_empty",
            help = "Output for all groups (even the ones with no medias at all) from the first to last, or just the ones having at least one media per group?")

    parser.add_argument("-q", "--quora", action = "store", type = int, dest = "remove_quora",
            help = "Hides from the output all the groups having less than given number of medias.")

    parser.add_argument("-c", "--compact", action = "store_true",
            help = "When set, outputs each column of width 1 character (otherwise 4).")

    parser.add_argument("-s", "--scale", action = "store", default = pc_output.DEFAULT_SCALE_CHARS,
            help = "Use the custom scale if --cell-format=scale. First character indicates zero medias, second indicates one media, the rest goes gradualy up to infinity. Example: '_xX#'")

    add_common_arguments(parser)


def construct_copy_or_move_sub_parse(subparsers, action):
    parser = subparsers.add_parser(action, help = f"Does {action} with the groupped media files. Creates directory in --destination for each group and does {action} into the particular group directories.")

    parser.add_argument("-q", "--quora", action = "store", type = int,
            help = f"Specifies how small groups are ignored (doesn't get {action}ed if the group has less the quora medias)")

    parser.add_argument("-d", "--destination", action = "store", default = ".",
            help = f"Specifies where to {action} the files to (their owning group dirs). Default is current dir.")
    
    add_common_arguments(parser)



def construct_dump_sub_parse(subparsers):
    parser = subparsers.add_parser("dump", help = "Just outputs the loaded medias and their dates of taken/shot in the specified format.")

    parser.add_argument("-f", "--output-format", action = "store", dest = "output_format",
            choices = ["yaml", "list"],
            default = "list",
            help = "Specifies the format of how to output the collected medias and their date of taken/shot. Value 'list' just literally lists the medias (the file path + date separated by tab), 'yaml' ouputs the data in the YAML file format (to be then back importable). Default is 'list'.")

    add_common_arguments(parser, False)


def add_common_arguments(parser, with_groupper = True):
    parser.add_argument("-v", "--verbose", action = "store_true",
            help = "Enables verbose output")

    parser.add_argument("-D", "--debug", action = "store_true",
            help = "Enables full debug output")

    if with_groupper:
        parser.add_argument("-g", "--groupper", action = "store", default="day",
                choices = ["year", "month", "week", "day", "hour"],
                help = "Group the medias by what? (If in the table output, specifies the rows groupper, column groupper is automatically the lower one). The default is 'day'.")
    
    parser.add_argument("-r", "--recursive", action = "store_true", dest = "recurse",
            help = "If set, will look for the photo/video files in the DIRECTORY... recursivelly")
 
    parser.add_argument("directories", metavar = "DIRECTORY", action = "store",
            nargs = "*",
            help = "The directories to scan for the photo/video files (either --recursive or not). If none given, YAML produced by 'dump' action (with 'yaml' format) is expected on stdin.")

###############################################################################

def check_args(parsed_args):
    """ Validates the provided args """

    for directory in parsed_args.directories:
        if not os.path.isdir(directory):
            raise ValueError(f"The {directory} is not a directory")

    if "destination" in parsed_args:
        if not os.path.isdir(parsed_args.destination):
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

def parse_args(args):
    parser = construct_parser()
    
    parsed = parser.parse_args(args)

    configure_logging(parsed.verbose, parsed.debug)
    check_args(parsed)

    return parsed

###############################################################################

