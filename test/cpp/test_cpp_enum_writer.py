import unittest
import io
from textwrap import dedent

from code_generation.cpp.source_file import CppSourceFile
from code_generation.cpp.enum_generator import CppEnum
from test.comparing_tools import normalize_code, debug_dump, is_debug

__doc__ = """Unit tests for C++ code generator
"""


class TestCppEnumStringIo(unittest.TestCase):
    """
    Test C++ enum generation by writing to StringIO
    """

    def test_simple_case(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        enum = CppEnum(name="Items")
        enum.add_items(["Chair", "Table", "Shelve"])
        enum.render_to_string(cpp)
        expected_output = dedent("""\
            enum Items
            {
                eChair = 0,
                eTable = 1,
                eShelve = 2,
                eItemsCount = 3
            };""")
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "cpp")

        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_with_prefix(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        enum = CppEnum(name="Items", prefix="Prefix")
        enum.add_items(["A", "B", "C"])
        enum.render_to_string(cpp)
        expected_output = dedent("""\
            enum Items
            {
                PrefixA = 0,
                PrefixB = 1,
                PrefixC = 2,
                PrefixItemsCount = 3
            };""")
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "cpp")

        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_class(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        enum = CppEnum(name="Items", enum_class=True)
        enum.add_items(["A", "B", "C"])
        enum.render_to_string(cpp)
        expected_output = dedent("""\
            enum class Items
            {
                eA = 0,
                eB = 1,
                eC = 2,
                eItemsCount = 3
            };""")
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "cpp")

        self.assertEqual(expected_output_normalized, actual_output_normalized)


if __name__ == "__main__":
    unittest.main()
