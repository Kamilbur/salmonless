import unittest

from sra_explorer import SRAExplorer

class MyTestCase(unittest.TestCase):
    query = 'SRR32296278[All Fields]'

    def test_count(self):
        self.assertEqual(
            SRAExplorer(self.query).experiment_count,
            1
        )

    def test_generator(self):
        elements = list(SRAExplorer(self.query))

        self.assertEqual(len(elements), 4)
        self.assertEqual(elements[0].runs.acc, 'SRR32296276')


if __name__ == '__main__':
    unittest.main()
