import unittest
import io

from code_generation.java.file_writer import JavaFile
from code_generation.java.array_generator import JavaArray


class TestJavaArrayStringIo(unittest.TestCase):
    """
    Test Java array generation by writing to StringIO
    """

    def test_java_array(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        arr = JavaArray(name="myArray", values=["1", "2", "0"])
        arr.render_to_string(java)
        expected_output = "int[] myArray = {1, 2, 0};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_java_array_with_empty_values(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        arr = JavaArray(name="emptyArray", values=[])
        arr.render_to_string(java)
        expected_output = "int[] emptyArray = new int[0];"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_java_array_add_item(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        arr = JavaArray(name="myArray")
        arr.add_item("item1")
        arr.add_item("item2")
        arr.render_to_string(java)
        expected_output = "String[] myArray = {\"item1\", \"item2\"};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_java_array_add_items(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        arr = JavaArray(name="myArray")
        arr.add_items(["item1", "item2", "item3"])
        arr.render_to_string(java)
        expected_output = "String[] myArray = {\"item1\", \"item2\", \"item3\"};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_missing_name(self):
        arr = JavaArray(values=["1", "2", "3"])
        self.assertRaises(RuntimeError, arr.render_to_string, None)

    def test_invalid_values_type(self):
        arr = JavaArray(name="myArray", values="invalid")
        self.assertRaises(RuntimeError, arr.render_to_string, None)


if __name__ == "__main__":
    unittest.main()
