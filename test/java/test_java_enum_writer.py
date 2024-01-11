import unittest
import io

from code_generation.java.file_writer import JavaFile
from code_generation.java.enum_generator import JavaEnum
from test.comparing_tools import normalize_code, debug_dump, is_debug


class TestJavaEnumStringIo(unittest.TestCase):
    """
    Test Java enum generation by writing to StringIO
    """

    def test_java_enum(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        enum = JavaEnum(name="Color", values=["RED", "GREEN", "BLUE"])
        enum.render_to_string(java)
        actual_output = writer.getvalue().strip()
        expected_output = "enum Color { RED, GREEN, BLUE };"
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_render_to_string_declaration(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        enum = JavaEnum(name="Color", values=["RED", "GREEN", "BLUE"])
        enum.render_to_string(java)
        expected_output = "enum Color;"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_missing_name(self):
        enum = JavaEnum(name=None, values=["RED", "GREEN", "BLUE"])
        self.assertRaises(RuntimeError, enum.render_to_string, None)

    def test_non_string_name(self):
        enum = JavaEnum(name=123, values=["RED", "GREEN", "BLUE"])
        self.assertRaises(RuntimeError, enum.render_to_string, None)

    def test_non_list_values(self):
        enum = JavaEnum(name="Color", values="RED, GREEN, BLUE")
        self.assertRaises(RuntimeError, enum.render_to_string, None)


if __name__ == "__main__":
    unittest.main()
