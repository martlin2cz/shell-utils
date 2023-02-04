#!/usr/bin/python3.8
#
# An tool for classifing the photos semi-automatically/partially
# by the date taken and some more
#
# m@rtlin, 29.12.2022
#      v2:  4. 2.2023 - 29.2.2023
#
###############################################################################

import pc_classifier
import pc_argparser

import logging
import sys

###############################################################################

""" The logger. """
LOGGER = logging.getLogger("p_c")

###############################################################################

def doit(parsed):
    """ Does the actual action based on th parsed args """

    action = parsed.action

    if action == "list":
        pc_classifier.list_groups(parsed.directories, parsed.recurse, parsed.groupper, parsed.include_empty, parsed.remove_quora, parsed.row_format, parsed.output_quora, parsed.scale)

    if action == "table":
        pc_classifier.table_subgroups(parsed.directories, parsed.recurse, parsed.groupper, parsed.include_empty, parsed.remove_quora, parsed.cell_format, parsed.compact, parsed.scale)

    if action == "copy":
        pc_classifier.copy_or_move_to_groups(parsed.directories, parsed.recurse, parsed.groupper, "copy", parsed.quora, parsed.destination)

    if action == "move":
        pc_classifier.copy_or_move_to_groups(parsed.directories, parsed.recurse, parsed.groupper, "move", parsed.quora, parsed.destination)
        

###############################################################################

if __name__ == "__main__":
    args = sys.argv[1:]
    parsed = pc_argparser.parse_args(args)
    doit(parsed)
