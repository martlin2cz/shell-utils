""" The output (do the actual action based on the processed data, classified medias) module of the photos_classifier. """

###############################################################################

import pc_input
import pc_process

import logging
import datetime
import sys
import pandas
import numpy
import os
import shutil

###############################################################################

""" The general with of the header/label column of both the 'list' and 'table' output. '"""
LABEL_WIDTH=20

""" If not compact table view, how wide the each column is to be? """
NORMAL_COLUMN_WIDTH=4

""" The date formats for the line headers/labels. """
LINE_LABEL_DATE_FORMATS = { "year": "%Y", "month": "%Y-%m", "week": "%Y-%m-%d +7d", "day": "%a %Y-%m-%d", "hour": "%a %Y-%m-%d %H:xx" }

""" The date formats (optionally containing the %COUNT directive) for the directories names. """
GROUP_DIRNAME_FORMATS = { 
    "year":  "%Y_having-%COUNT-files", 
    "month": "%Y-%m_having-%COUNT-files",
    "week":  "%Y-%m-%d_having-%COUNT-files",
    "day":   "%Y-%m-%d_having-%COUNT-files",
    "hour":  "%Y-%m-%d %H:xx_having-%COUNT-files" }

""" The character to be used to indicate one media in the histo output (bellow output_quora) """
HISTO_CHAR_IN_QUORA="|"

""" The character to be used to indicate one media in the histo output (over output_quora) """
HISTO_CHAR_OVER_QUORA="!"

""" The scale of charecters going from 0 files to oo files """
DEFAULT_SCALE_CHARS=" .,;!iILHM8%@#"

""" The logger. """
LOGGER = logging.getLogger("p_c")

###############################################################################

def print_groups(groups, groupper, line_format, quora = None, scale = DEFAULT_SCALE_CHARS):
    """ Prints the groups groupped by the given groupper with the specified line format (and configuration of the format). """

    LOGGER.info(f"Printing {len(groups)} groups (in rows) in format {line_format}")
    LOGGER.debug(f"Printing {len(groups)} groups (in rows) groupped by groupper {groupper}, in format {line_format}, with quora {quora} and scale {scale}")

    for media_date in groups.keys():
        media_files = groups[media_date]

        label = compute_line_label(media_date, groupper)
        files_str = strigify_files(media_files, line_format, quora, scale)
        
        line = "%s | %s" % (label, files_str)
        print(line)

    LOGGER.info(f"Printed  {len(groups)} groups")


def compute_line_label(media_date, groupper):
    """ Computes the label for the given date. May have fixed length no matter the inputs. """

    #TODO if NO_DATE then return something custom
    line_label_date_format = LINE_LABEL_DATE_FORMATS[groupper]
    media_date_str = media_date.strftime(line_label_date_format)
    return media_date_str.rjust(LABEL_WIDTH)


def strigify_files(media_files, line_format, quora, scale):
    """ Constructs the line contents for the given media files in the given format, with the given configuration. """

    if line_format == "list":
        return str(media_files)

    if line_format == "count":
        return str(len(media_files))

    if line_format == "count-or-none":
        return compute_count_or_none(media_files)

    if line_format == "simple-count":
        return compute_simple_count(media_files)
    
    if line_format == "histo":
        return compute_histo_line(media_files, quora)

    if line_format == "scale":
        return compute_scale_character(media_files, scale)

    raise ValueError(f"Unsupported line format: {line_format}")


def compute_count_or_none(media_files):
    """ Returns the count of the medias or blank if none """

    if len(media_files) == 0:
        return " "
    else:
        return str(len(media_files))
    
def compute_simple_count(media_files):
    """ Converts the given media files into the simple-count, i.e. 1-9 (if exactly that number of medias) or + (if 10-19) or * (20 and more) """

    count = len(media_files)
    if count == 0:
        return " "
    if count < 10:
        return str(count)
    if count < 20:
        return "+"
    else:
        return "*"

def compute_histo_line(media_files, quora):
    """ Converts the given media files into the histo view of them. """

    count = len(media_files)
    if not quora:
        quora = numpy.inf

    if count < quora:
        return HISTO_CHAR_IN_QUORA * count
    else:
        remaining_count = count - quora
        return (HISTO_CHAR_IN_QUORA * quora) + (HISTO_CHAR_OVER_QUORA * remaining_count)

    
def compute_scale_character(media_files, scale):
    """ Converts the given media files into the scale character of them. """

    files_count = len(media_files)
    scale_len = len(scale)

    if files_count == 0:
        index = 0
    else:
        scale_len_reduced = scale_len + 0
        files_count_reduced = files_count + 1
        stretch = 0.75
        index = int(scale_len_reduced * numpy.tanh(stretch * files_count_reduced / scale_len_reduced))
   
    if index >= scale_len:
        index = scale_len - 1

    return scale[index];


###############################################################################

def print_sub_groups(groups_with_subgroups, groupper, cell_format, compact_view = True, scale = DEFAULT_SCALE_CHARS):
    """ Prints the given groups with their subgroups, beeing groupped by the given groupper. Outputs in the table with given cell format, possibly compact (columns of with just 1 char) and if in the scale output, by using the given scale. """

    subgroupper = pc_process.SUBGROUP_CHILD_GROUPPER_MAPPING[groupper]
    LOGGER.info(f"Printing {len(groups_with_subgroups)} groups (in table) in format {cell_format}")
    LOGGER.debug(f"Printing {len(groups_with_subgroups)} groups with subgroups (in table) groupped by groupper {groupper} and subgroupper {subgroupper}, in format {cell_format}, with compact view {compact_view} and scale {scale}")

    header = "---".rjust(LABEL_WIDTH)
    sys.stdout.write(header + " | ")

    for column_num in pc_process.SUBGROUP_CHILDREN_RANGE_MAPPING[subgroupper]:
        row_label = compute_column_label(column_num, groupper, compact_view)
        sys.stdout.write(row_label)
    sys.stdout.write(os.linesep)

    for group_date in groups_with_subgroups.keys():
        subgroup = groups_with_subgroups[group_date]
        line_label = compute_line_label(group_date, groupper)
        sys.stdout.write(line_label + " | ")

        for subgroup_date in subgroup.keys():
            subgroup_files = subgroup[subgroup_date]
            cell_str = compute_cell(subgroup_files, cell_format, compact_view, scale)
            sys.stdout.write(cell_str)

        sys.stdout.write(os.linesep)

    LOGGER.info(f"Printed  {len(groups_with_subgroups)} groups")

def compute_column_label(column_num, groupper, compact_view):
    """ Computes the table label of the column. """
    
    if groupper == "week":
        if compact_view:
             return ["M", "T", "W", "T", "F", "S", "S"][column_num]
        else:
             return ["Mon", "Tue", "Wen", "Thr", "Fri", "Sat", "Sun"][column_num].rjust(NORMAL_COLUMN_WIDTH)
    
    if compact_view:
        return str(column_num % 10)
    else:
        return str(column_num).rjust(NORMAL_COLUMN_WIDTH)


def compute_cell(subgroup_files, cell_format, compact_view, scale):
    """ Computes the actual table cell, based on the files and cell format. """

    cell_str = strigify_files(subgroup_files, cell_format, None, scale)
    if compact_view:
        return cell_str.rjust(1)[-1]
    else:
        return cell_str.rjust(NORMAL_COLUMN_WIDTH)


###############################################################################

def copy_or_move(groups, groupper, action, destination):
    """ Copies or moves (based on the action) the files to the corresponding destination sub-dirs """

    LOGGER.info(f"Copying/Moving ({action}) of {len(groups)} groups to {destination}")

    dirname_format = GROUP_DIRNAME_FORMATS[groupper]

    for media_date in groups.keys():
        media_files = groups[media_date]
        files_count = len(media_files)

        dirname_format_with_count = dirname_format.replace("%COUNT", str(files_count));
        dirname = media_date.strftime(dirname_format_with_count)

        group_dir = os.path.join(destination, dirname)
        os.makedirs(group_dir)

        for media_file in media_files:
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
        raise ValueError("Either copy or move is allowed")

