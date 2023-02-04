""" The whole classifier (some sort of fascade) of the classifier. Provides the actual "public" functions. """

###############################################################################

import pc_input
import pc_process
import pc_output

import logging


###############################################################################

def list_groups(directories, recurse, groupper, fill_empty, remove_quora, line_format, output_quora, scale):
    """ Loads (optionally recursivelly) the given directories,
        groups their media files by the given groupper,
        optionally filling the ones having no files,
        optionally removing ones having less than remove_quora files,
        and outputs them in a rows in line_format for each line (one of: "list", "count", "simple-count", "histo" or "scale"),
        optionally marking overflowing output_quora in the output somehow """

    files = pc_input.load(directories, recurse)
    groups = pc_process.process(files, groupper, fill_empty, remove_quora, False)
    pc_output.print_groups(groups, groupper, line_format, output_quora, scale)

def table_subgroups(directories, recurse, groupper, fill_empty, remove_quora, cell_format, compact_view, scale):
    """ Loads (optionally recursivelly) the given directories,
        groups their media files by the given groupper and subgroupper,
        optionally filling the ones having no files,
        optionally removing ones having less than remove_quora files,
        and outputs them in a table with given cell_format (either "count" or "scale"),
        optionally marking overflowing output_quora in the output somehow """

    files = pc_input.load(directories, recurse)
    subgroups = pc_process.process(files, groupper, fill_empty, remove_quora, True)


    if cell_format == "count":
        if compact_view:
            cell_format_corrected = "simple-count"
        else: 
            cell_format_corrected = "count-or-none"
    else:
        cell_format_corrected = cell_format

    pc_output.print_sub_groups(subgroups, groupper, cell_format_corrected, compact_view, scale)


def copy_or_move_to_groups(directories, recurse, groupper, action, quora, destination):
    """ Loads (optionally recursivelly) the given directories,
        groups their media files by the given groupper,
        optionally removing ones having less than qoura files,
        and either copies (if action="copy") or moves them (if action="move")
        into the destination directory """

    files = pc_input.load(directories, recurse)
    groups = pc_process.process(files, groupper, False, quora, False)
    pc_output.copy_or_move(groups, groupper, action, destination)


###############################################################################
