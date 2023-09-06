import unittest
from LoadReportServices import dates_extraction


class TestTemporalMethods(unittest.TestCase):

    def test_split(self):
        test_cases = ["May 22nd, 1993"]
        test_answers = ["1993:05:22"]
        for i, t in enumerate(test_cases):
            answer = test_answers[i]
            time_string = dates_extraction(t)
            self.assertEqual(time_string, answer)


if __name__ == '__main__':
    unittest.main()
