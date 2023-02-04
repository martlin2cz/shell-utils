""" The unit test of the pc_classifier module. """

###############################################################################

import unittest

import pc_classifier

import logging
import pprint

###############################################################################

logging.basicConfig(level = logging.INFO)

###############################################################################

class TestClassifier(unittest.TestCase):


#    def test_list_one(self):
#        directories = ["testing-images"]
#        recurse = False
#        groupper = "day"
#        fill_empty = False
#        remove_quora = 1
#        line_format = "histo"
#        output_quora = None
#        scale = " .oO0"
#
#        print("----------------")
#        pc_classifier.list_groups(directories, recurse, groupper, fill_empty, remove_quora, line_format, output_quora, scale)
#        print("----------------")
#
#
#    def test_list_all(self):
#        directories = ["testing-images"]
#        recurse = False
#
#        for groupper in ["year", "month", "week", "day", "hour"]:
#            for fill_empty in [True, False]:
#                for remove_quora in [None, 1, 2]:
#                    for line_format in ["list", "simple-count", "count", "histo", "scale"]:
#                        for output_quora in [None, 1, 2]:
#                             scale = " .oO0"
#                            print(f"=============== : {directories}, {recurse}, {groupper}, {fill_empty}, {remove_quora}, {line_format}, {output_quora}, {scale}")
#                            pc_classifier.list_groups(directories, recurse, groupper, fill_empty, remove_quora, line_format, output_quora, scale)
#
#
    def test_table_one(self):
        directories = ["testing-images"]
        recurse = False
        groupper = "day"
        fill_empty = False
        remove_quora = 1
        line_format = "histo"
        output_quora = None
        scale = " .oO0"

        print("----------------")
        pc_classifier.table_subgroups(directories, recurse, groupper, fill_empty, remove_quora, line_format, output_quora, scale)
        print("----------------")

    def test_table_all(self):
        directories = ["testing-images"]
        recurse = False

        for groupper in ["year", "month", "week", "day", "hour"]:
            for fill_empty in [True, False]:
                for remove_quora in [None, 1, 2]:
                    for cell_format in ["count", "scale"]:
                        for compact in [True, False]:
                            scale = " .oO0"
                            print(f"=============== : {directories}, {recurse}, {groupper}, {fill_empty}, {remove_quora}, {cell_format}, {compact}, {scale}")
                            pc_classifier.table_subgroups(directories, recurse, groupper, fill_empty, remove_quora, cell_format, compact, scale)


        
        

if __name__ == '__main__':
    unittest.main()


