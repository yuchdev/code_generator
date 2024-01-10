import unittest
import io

from code_generation.java.file_writer import JavaFile
from code_generation.java.enum_generator import JavaEnum


class TestJavaEnumStringIo(unittest.TestCase):
    """
    Test Java enum generation by writing to StringIO
    """

    def test_java_enum(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        enum = JavaEnum(name="Color", values=["RED", "GREEN", "BLUE"])
        enum.render_to_string(java)
        expected_output = "enum Color {\n    RED,\n    GREEN,\n    BLUE\n}"
        self.assertEqual(expected_output, writer.getvalue().strip())

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
