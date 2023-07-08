import unittest
import io
from textwrap import dedent

from code_generation.java.file_writer import JavaFile
from code_generation.java.function_generator import JavaFunction


class TestJavaFunctionStringIo(unittest.TestCase):
    """
    Test Java method generation by writing to StringIO
    """

    def test_java_method(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        method = JavaFunction(name="calculateSum",
                              return_type="int",
                              implementation_handle=lambda: "return a + b;")
        method.add_argument("int a")
        method.add_argument("int b")
        method.render_to_string(java)
        expected_output = dedent("""\
            public int calculateSum(int a, int b) {
                // Method implementation
                return a + b;
            }""")
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_render_to_string_declaration(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        method = JavaFunction(name="calculateSum",
                              return_type="int",
                              implementation_handle=lambda: "return a + b;")
        method.add_argument("int a")
        method.add_argument("int b")
        method.render_to_string(java)
        expected_output = dedent("""\
            public int calculateSum(int a, int b);""")
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_missing_name(self):
        method = JavaFunction(name=None, return_type="int")
        self.assertRaises(RuntimeError, method.render_to_string, None)

    def test_non_string_name(self):
        method = JavaFunction(name=123, return_type="int")
        self.assertRaises(RuntimeError, method.render_to_string, None)

    def test_non_string_return_type(self):
        method = JavaFunction(name="calculateSum", return_type=123)
        self.assertRaises(RuntimeError, method.render_to_string, None)

    def test_non_list_arguments(self):
        method = JavaFunction(name="calculateSum", return_type="int")
        method.arguments = "int a, int b"
        self.assertRaises(RuntimeError, method.render_to_string, None)


if __name__ == "__main__":
    unittest.main()
