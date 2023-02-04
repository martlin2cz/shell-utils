""" The unit test of the pc_classifier module. """

###############################################################################

import unittest

import pc_argparser

import logging
import pprint

###############################################################################

logging.basicConfig(level = logging.INFO)

###############################################################################

class TestArgparser(unittest.TestCase):
    
    def test_parse_some(self):
        parsed = pc_argparser.parse_args(["table", "--compact", "--debug", "-s= .oO0", "-r", "testing-images"])

        print(parsed)

    def test_helps(self):
        parser = pc_argparser.construct_parser()

        try:
            print("==================")
            parser.parse_args(["--help"])
        except SystemExit:
            print("==================")
            pass

        try:
            print("==================")
            parser.parse_args(["list", "--help"])
        except SystemExit:
            print("==================")
            pass

        try:
            print("==================")
            parser.parse_args(["copy", "--help"])
        except SystemExit:
            print("==================")
            pass

    def test_argparser(self):
        parser = pc_argparser.construct_parser()

        print(parser)
        

if __name__ == '__main__':
    unittest.main()


