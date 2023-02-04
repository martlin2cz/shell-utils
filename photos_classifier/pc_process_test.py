""" The unit test of the pc_process module. """

###############################################################################

import unittest

import datetime
import pprint

import pc_input
import pc_process

import logging

###############################################################################

#logging.basicConfig(level = logging.DEBUG)

###############################################################################

class TestProcess(unittest.TestCase):


    def test_process_one(self):
        files = pc_input.load(["testing-images"], False)

        groupper = "day"
        fill_missing = True
        quora = None
        sub_group = True                    

        print(f"Group by {groupper}, fill empty? {fill_missing}, limit to <{quora}, sub-group? {sub_group} :")
        groups = pc_process.process(files, groupper, fill_missing, quora, sub_group)
        #pprint.pprint(groups)
        #print(len(prepared_subgroup))

    def test_process_all(self):
        files = pc_input.load(["testing-images"], False)

        for groupper in ["year", "month", "week", "day"]:
            for fill_missing in [True, False]:
                for quora in [0, 1, 2, 3]:
                    for sub_group in [True, False]:
                        print(f"Group by {groupper}, fill empty? {fill_missing}, limit to <{quora}, sub-group? {sub_group} :")
                        groups = pc_process.process(files, groupper, fill_missing, quora, sub_group)
                        pprint.pprint(groups)
                        #print(len(prepared_subgroup))
                        #self.assertTrue(len(groups) > 0)

    def test_prepare_sub_groups(self):
        files = pc_input.load(["testing-images"], False)

        for groupper in ["year", "month", "week", "day"]:
            for fill_missing in ["from-first-to-last", "fill-the-interval", "none"]:
                for quora in [0, 1, 2, 3]:
                    groups = pc_process.group_by(files, groupper)
                    subgroups = pc_process.sub_group(groups, files, groupper)
                    prepared_subgroup = pc_process.prepare_sub_groups(subgroups, groupper, fill_missing, quora)
                    #pprint.pprint(prepared_subgroup)
                    print(len(prepared_subgroup))
                    #self.assertTrue(len(prepared_subgroup) > 0)

    def test_sub_groups(self):
        files = pc_input.load(["testing-images"], False)

        for groupper in ["year", "month", "week", "day"]:
            groups = pc_process.group_by(files, groupper)
            subgroups = pc_process.sub_group(groups, files, groupper)
            #pprint.pprint(subgroups)
            print(len(subgroups))
            self.assertTrue(len(subgroups) > 0)


    def test_prepare_groups(self):
        files = pc_input.load(["testing-images"], False)

        for groupper in ["year", "month", "week", "day", "hour"]:
            for fill_missing in ["from-first-to-last", "fill-the-interval", "none"]:
                 for quora in [0, 1, 2, 3]:
                    groups_by_groupper = pc_process.group_by(files, groupper)
                    prepared_by_groupper = pc_process.prepare_groups(groups_by_groupper, groupper, fill_missing, quora, "empty-list")
                    #print(prepared_by_groupper)
                    print(len(prepared_by_groupper))
                    #self.assertTrue(len(prepared_by_groupper) > 0)



    def test_group_by(self):
        files = pc_input.load(["testing-images"], False)


        groupped_by_year = pc_process.group_by(files, "year")
        print(groupped_by_year)
        self.assertTrue(len(groupped_by_year) > 0)

        groupped_by_month = pc_process.group_by(files, "month")
        print(groupped_by_month)
        self.assertTrue(len(groupped_by_month) > 0)

        groupped_by_week = pc_process.group_by(files, "week")
        print(groupped_by_week)
        self.assertTrue(len(groupped_by_week) > 0)

        groupped_by_day = pc_process.group_by(files, "day")
        print(groupped_by_day)
        self.assertTrue(len(groupped_by_day) > 0)

        groupped_by_hour = pc_process.group_by(files, "hour")
        print(groupped_by_hour)
        self.assertTrue(len(groupped_by_hour) > 0)

        # TODO and more


    def test_range_dates(self):
        start_date = datetime.datetime(2022, 11, 10, 9, 8, 7)
        end_date = datetime.datetime(2021, 11, 11, 10, 10, 10)
        
        groups = {start_date: ["lorem"], end_date: ["ipsum"]}
        
        explicit_range = list(pc_process.range_the_dates(groups, "whatever", "none"))        
        print(explicit_range)
        self.assertTrue(len(explicit_range) == 2)

        for groupper in ["year", "month", "week", "day", "hour"]:
            for fill_missing in ["from-first-to-last", "fill-the-interval", "none"]:
                alled_range = list(pc_process.range_the_dates(groups, groupper, fill_missing))        
                print(len(alled_range))
                #print(alled_range)
                self.assertTrue(len(alled_range) > 0)
            

    def test_compute_key(self):
        indate = datetime.datetime(2022, 11, 10, 9, 8, 7) #Thr
        print(indate)
        
        by_hour = pc_process.compute_key(indate, "hour")
        print(by_hour)
        self.assertEqual(by_hour.month, 11)
        self.assertEqual(by_hour.day, 10)
        self.assertEqual(by_hour.hour, 9)
        self.assertEqual(by_hour.minute, 0)
        self.assertEqual(by_hour.second, 0)

        by_day = pc_process.compute_key(indate, "day")
        print(by_day)
        self.assertEqual(by_day.month, 11)
        self.assertEqual(by_day.day, 10)
        self.assertEqual(by_day.hour, 0)
        self.assertEqual(by_day.minute, 0)

        by_week = pc_process.compute_key(indate, "week")
        print(by_week)
        self.assertEqual(by_week.month, 11)
        self.assertEqual(by_week.day, 7)
        self.assertEqual(by_week.hour, 0)
        self.assertEqual(by_week.minute, 0)

        by_month = pc_process.compute_key(indate, "month")
        print(by_month)
        self.assertEqual(by_month.month, 11)
        self.assertEqual(by_month.day, 1)
        self.assertEqual(by_month.hour, 0)
        self.assertEqual(by_month.minute, 0)

        by_year = pc_process.compute_key(indate, "year")
        print(by_month)
        self.assertEqual(by_year.month, 1)
        self.assertEqual(by_year.day, 1)
        self.assertEqual(by_year.hour, 0)
        self.assertEqual(by_year.minute, 0)



    def test_week_manipulation(self):
        indate = datetime.datetime(2023, 2, 28, 0, 0, 1) #Tue

        weekstart = pc_process.compute_key(indate, "week")
        self.assertEqual(weekstart.month, 2)
        self.assertEqual(weekstart.day, 27) #Mon

        weekmon = pc_process.combine_key(weekstart, "_day-of-week", 0)
        self.assertEqual(weekmon.month, 2)
        self.assertEqual(weekmon.day, 27) #still Mon
                
        weeksat = pc_process.combine_key(weekstart, "_day-of-week", 5)
        self.assertEqual(weeksat.month, 3)
        self.assertEqual(weeksat.day, 4) #Sat

        weekthr = pc_process.combine_key(weekstart, "_day-of-week", 3)
        self.assertEqual(weekthr.month, 3)
        self.assertEqual(weekthr.day, 2) #Thr


        print(indate)

if __name__ == '__main__':
    unittest.main()
