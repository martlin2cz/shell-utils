#!/bin/python3

import logging
import argparse
import os

import labeler

""" The logger. """
LOGGER = logging.getLogger("labeler")

###############################################################################

def construct_parser():
    """ Constructs the argparser """

    parser = argparse.ArgumentParser(
            description = "Adds Label column to the given CSV file, filling its value based on the rules file.")

    parser.add_argument("-v", "--verbose", action = "store_true",
            help = "Enables verbose output")

    parser.add_argument("-d", "--debug", action = "store_true",
            help = "Enables full debug output")


    parser.add_argument("-c", "--column-name", action = "store", type = str,
            default = "Label", dest = "column_name",
            help = "The name of the new label column")

    parser.add_argument("-o", "--override", action = "store_true",
            dest = "allow_override",
            help = "Allow overriding existing (when record already has a label)?")

    parser.add_argument("-r", "--rewrite", action = "store",
            dest = "rewrite_strategy", choices = ["first", "last", "fail"], default = "last",
            help = "If multiple rules matches, pick label of first matching rule, last one, or none (first actually) and report error?")


    parser.add_argument("-dry", "--dry-run", action = "store_true",
            dest = "dry_run",
            help = "Dry run (do everything, but don't save the OUTFILE at the end")


    parser.add_argument("infile", metavar = "INFILE", action = "store", nargs = 1,
            type = argparse.FileType('r'),
            help = "The input CSV file.")

    parser.add_argument("rules_file", metavar = "RULES_FILE", action = "store", nargs = 1,
            type = argparse.FileType('r'),
            help = "The CSV files with the rules.")

    parser.add_argument("outfile", metavar = "OUTFILE", action = "store", nargs = 1,
            type=argparse.FileType('w'),
            help = "The output CSV file.")

    return parser

###############################################################################

def configure_logging(verbose, debug):
    """ Sets the logger configuration based on the command line flags """

    if not (verbose or debug):
        return
    
    if verbose:
        new_level = logging.INFO

    if debug:
        new_level = logging.DEBUG

    logging.basicConfig(level = logging.INFO, format="%(levelname)8s %(message)s")
    LOGGER.setLevel(new_level)

###############################################################################

if __name__ == "__main__":
    parser = construct_parser()
    parsed = parser.parse_args()

    configure_logging(parsed.verbose, parsed.debug)
    LOGGER.debug("ARGS: %s", parsed)

    column_name = parsed.column_name
    allow_override = parsed.allow_override
    rewrite_strategy = parsed.rewrite_strategy
    dry_run = parsed.dry_run
    infile = parsed.infile[0]
    rules_file = parsed.rules_file[0]
    outfile = parsed.outfile[0]

    labeler.run(infile, rules_file, column_name, allow_override, rewrite_strategy, dry_run, outfile)


