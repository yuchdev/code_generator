import unittest
import io
from textwrap import dedent

from code_generation.cpp.file_writer import CppFile
from code_generation.cpp.enum_generator import CppEnum

__doc__ = """Unit tests for C++ code generator
"""


class TestCppEnumStringIo(unittest.TestCase):
    """
    Test C++ enum generation by writing to StringIO
    """

    def test_cpp_enum(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        enum = CppEnum(name="Items")
        enum.add_items(["Chair", "Table", "Shelve"])
        enum.render_to_string(cpp)
        expected_output = dedent("""\
            enum Items
            {
                Chair,
                Table,
                Shelve
            };""")
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_cpp_enum_with_prefix(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        enum = CppEnum(name="Items", prefix="Prefix")
        enum.add_items(["A", "B", "C"])
        enum.render_to_string(cpp)
        expected_output = dedent("""\
            enum Items
            {
                PrefixA,
                PrefixB,
                PrefixC
            };""")
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_cpp_enum_class(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        enum = CppEnum(name="Items", enum_class=True)
        enum.add_items(["A", "B", "C"])
        enum.render_to_string(cpp)
        expected_output = dedent("""\
            enum class Items
            {
                A,
                B,
                C
            };""")
        self.assertEqual(expected_output, writer.getvalue().strip())


if __name__ == "__main__":
    unittest.main()
