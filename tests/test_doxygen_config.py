import unittest
import filecmp
import os
import sys
sys.path.append("../src")
from doxygen_config import DoxygenConfig  # NoQA


class DoxygenConfigTest(unittest.TestCase):
    def test_doxygen_config_binary_match_output(self):
        cfg = DoxygenConfig()
        f1 = 'resources/Doxyfile'
        f2 = 'Doxyfile_to_compare'
        cfg.load(f1)
        cfg.save(f2)
        self.assertTrue(filecmp.cmp(f1, f2))
        os.remove(f2)


if __name__ == '__main__':
    unittest.main()
