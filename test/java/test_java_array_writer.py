import unittest
import io

from code_generation.java.source_file import JavaSourceFile
from code_generation.java.array_generator import JavaArray
from test.comparing_tools import normalize_code, debug_dump, is_debug


class TestJavaArrayStringIo(unittest.TestCase):
    """
    Test Java array generation by writing to StringIO
    """

    def test_simple_case(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        arr = JavaArray(name="myArray", type="int", values=["1", "2", "0"])
        arr.render_to_string(java)
        expected_output = "int[] myArray = {1, 2, 0};"
        actual_output = writer.getvalue().strip()

        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_with_empty_values(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        arr = JavaArray(name="emptyArray", type='int', values=[])
        arr.render_to_string(java)
        actual_output = writer.getvalue().strip()
        expected_output = "int[] emptyArray = new int[0];"

        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_add_item(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        arr = JavaArray(name="myArray", type='String', quoted=True)
        arr.add_item("item1")
        arr.add_item("item2")
        arr.render_to_string(java)
        actual_output = writer.getvalue().strip()
        expected_output = "String[] myArray = {\"item1\", \"item2\"};"

        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_add_items(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        arr = JavaArray(name="myArray", type='String', quoted=True)
        arr.add_items(["item1", "item2", "item3"])
        arr.render_to_string(java)
        actual_output = writer.getvalue().strip()
        expected_output = "String[] myArray = {\"item1\", \"item2\", \"item3\"};"
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_missing_name(self):
        arr = JavaArray(values=["1", "2", "3"], type='int')
        self.assertRaises(RuntimeError, arr.render_to_string, None)

    def test_missing_type(self):
        arr = JavaArray(name="myArray", values=["1", "2", "3"])
        self.assertRaises(RuntimeError, arr.render_to_string, None)

    def test_invalid_values_type(self):
        arr = JavaArray(name="myArray", values="invalid")
        self.assertRaises(RuntimeError, arr.render_to_string, None)


if __name__ == "__main__":
    unittest.main()
