""" The unit test of the pc_input module. """

###############################################################################

import unittest

import pc_input

###############################################################################



###############################################################################

class TestInput(unittest.TestCase):

    def test_load(self):
        files_non_recursive = pc_input.list_files(["testing-images"], False)
        #print(files_non_recursive)
        self.assertTrue(len(files_non_recursive) > 0)


        files_recursive = pc_input.list_files(".", True)
        #print(files_recursive)
        self.assertTrue(len(files_recursive) > 0)

        self.assertTrue(len(files_recursive) > len(files_non_recursive))
        

    def test_datetime_of_photo(self):
        of_detaily = pc_input.datetime_of_photo("testing-images/detaily-o-zasilce.jpg")
        #print(of_detaily)
        self.assertEqual(of_detaily.year, 2021)

        of_kus = pc_input.datetime_of_photo("testing-images/kus-qeerka.jpg")
        #print(of_kus)
        self.assertEqual(of_kus.year, 2022)

    def test_datetime_of_video(self):
        of_video = pc_input.datetime_of_video("testing-images/videos/video-edit.mp4")
        #print(of_video)
        self.assertNotEqual(of_video.year, 2023)


if __name__ == '__main__':
    unittest.main()
