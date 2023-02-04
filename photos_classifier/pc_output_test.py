""" The unit test of the pc_output module. """

###############################################################################

import unittest

import pc_input
import pc_process
import pc_output

import logging
import pprint

###############################################################################

logging.basicConfig(level = logging.INFO)

###############################################################################

class TestOutput(unittest.TestCase):

    def test_print_sub_groups_basic_by_year(self):
        self.do_test_print_sub_groups_basic("year")

    def test_print_sub_groups_basic_by_months(self):
        self.do_test_print_sub_groups_basic("month")

    def test_print_sub_groups_basic_by_weeks(self):
        self.do_test_print_sub_groups_basic("week")

    def test_print_sub_groups_basic_by_days(self):
        self.do_test_print_sub_groups_basic("day")

    def test_print_sub_groups_basic_by_hours(self):
        self.do_test_print_sub_groups_basic("hour")

    def do_test_print_sub_groups_basic(self, groupper):
        files = pc_input.load(["testing-images"], False)
        subgroups = pc_process.process(files, groupper, False, None, True)
        #print(pprint.pprint(subgroups))
        
        for cell_format in ["count-or-none", "simple-count", "scale"]:
            for compact_format in [True, False]:
                print(f"Output for {cell_format} format, compact? {compact_format}, groupped by {groupper}")
                pc_output.print_sub_groups(subgroups, groupper, cell_format, compact_format, " .oO")
            


    def test_print_groups_basic_by_years(self):
        self.do_test_print_groups_basic("year")

    def test_print_groups_basic_by_months(self):
        self.do_test_print_groups_basic("month")

    def test_print_groups_basic_by_weeks(self):
        self.do_test_print_groups_basic("week")

    def test_print_groups_basic_by_days(self):
        self.do_test_print_groups_basic("day")

    def test_print_groups_basic_by_hours(self):
        self.do_test_print_groups_basic("hour")

    def do_test_print_groups_basic(self, groupper):
        files = pc_input.load(["testing-images"], False)
        groups = pc_process.process(files, groupper, False, None, False)
        
        for line_format in ["list", "count", "count-or-none", "simple-count", "histo", "scale"]:
            for quora in [None, 1]:
                print(f"Output for {line_format} format and quora = {quora}, groupped by {groupper}")
                pc_output.print_groups(groups, groupper, line_format, quora)
            

    def test_compute_scale(self):
        counts = range(0,45)
        media_files_fake = list(map(lambda n: f"file-{n}", counts))
        media_files_fakes = list(map(lambda n: media_files_fake[0:n], counts))

        for scale in [" #", " .oO", " .,;!/", " coedOEMW", "_123456789", pc_output.DEFAULT_SCALE_CHARS]:
            output = list(map(lambda mf: pc_output.compute_scale_character(mf, scale), media_files_fakes))
            print(f"Scaled: {output}")

            # having zero files may allways result in the first char of the sequence
            self.assertEqual(pc_output.compute_scale_character(media_files_fakes[0], scale), scale[0])
            # and having one file may allways result in the second char of the sequence
            self.assertEqual(pc_output.compute_scale_character(media_files_fakes[1], scale), scale[1])

        

if __name__ == '__main__':
    unittest.main()

