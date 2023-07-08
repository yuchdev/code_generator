import unittest
import io

from code_generation.cpp.file_writer import CppFile
from code_generation.cpp.array_generator import CppArray

__doc__ = """Unit tests for C++ code generator
"""


class TestCppArrayStringIo(unittest.TestCase):
    """
    Test C++ array generation by writing to StringIO
    """

    def test_cpp_array(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        arr = CppArray(name="my_array", type="int", array_size=5)
        arr.add_array_items(["1", "2", "0"])
        arr.render_to_string(cpp)
        expected_output = "int my_array[5] = {1, 2, 0};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_cpp_array_with_newline_align(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        arr = CppArray(name="my_array", type="int", array_size=5, newline_align=True)
        arr.add_array_items(["1", "2", "0"])
        arr.render_to_string(cpp)
        expected_output = "int my_array[5] = {\n    1,\n    2,\n    0\n};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_cpp_array_declaration(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        arr = CppArray(name="my_class_member_array", type="int", array_size=None, is_class_member=True)
        arr.render_to_string_declaration(cpp)
        expected_output = "int my_class_member_array[];"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_cpp_array_implementation(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        arr = CppArray(name="m_my_static_array", type="int", array_size=None,
                       is_class_member=True, is_static=True)
        arr.add_array_items(["1", "2", "0"])
        arr.render_to_string_implementation(cpp)
        expected_output = "static int m_my_static_array[] = {1, 2, 0};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_missing_type(self):
        arr = CppArray(name="my_array", array_size=5)
        self.assertRaises(RuntimeError, arr.render_to_string, None)

    def test_missing_name(self):
        arr = CppArray(type="int", array_size=5)
        self.assertRaises(RuntimeError, arr.render_to_string, None)

    def test_class_member_missing_name(self):
        arr = CppArray(type="int", is_class_member=True)
        self.assertRaises(RuntimeError, arr.render_to_string_declaration, None)

    def test_class_member_static_without_name(self):
        arr = CppArray(type="int", is_class_member=True, is_static=True)
        self.assertRaises(RuntimeError, arr.render_to_string_implementation, None)


if __name__ == "__main__":
    unittest.main()
