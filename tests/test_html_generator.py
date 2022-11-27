import unittest
import filecmp
import os
import io
import sys

from code_generation.html_generator import *

__doc__ = """
Unit tests for HTML code generator
"""


class TestHTMLFunctionGenerator(unittest.TestCase):

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        html = HtmlFile(None, writer=writer)


if __name__ == "__main__":
    unittest.main()
