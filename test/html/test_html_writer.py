import unittest
import io

from code_generation.html.html_file import *

__doc__ = """
Unit tests for HTML code generator
"""


class TestHTMLFunctionGenerator(unittest.TestCase):

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        html = HtmlFile(None, writer=writer)
        with html.block(element='p', id='id1', name='name1'):
            html('Text')
        print(writer.getvalue())
        result = """<p id="id1" name="name1">\n  Text\n</p>\n"""
        self.assertIn(result, writer.getvalue())


if __name__ == "__main__":
    unittest.main()
