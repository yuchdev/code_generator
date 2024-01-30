import unittest
import io
from textwrap import dedent

from code_generation.java.source_file import JavaSourceFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.variable_generator import JavaVariable
from code_generation.java.function_generator import JavaFunction
from test.comparing_tools import normalize_code, debug_dump, is_debug


class TestJavaClassStringIo(unittest.TestCase):
    """
    Test Java class generation by writing to StringIO
    """

    def test_simple_case(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        my_class = JavaClass(name="MyClass")
        var1 = JavaVariable(name="myVariable", type="int", value=10)

        def body(j):
            j("return myVariable;")

        method1 = JavaFunction(name="getVar", return_type="int", implementation=body)
        my_class.add_variable(var1)
        my_class.add_method(method1)
        my_class.render_to_string(java)
        expected_output = dedent("""\
            public class MyClass 
            {
                public int getVar()
                {
                    return myVariable;
                }
                int myVariable = 10;
            }""")
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_with_parent_class(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        my_class = JavaClass(name="MyClass", parent_class="ParentClass")
        my_class.render_to_string(java)
        expected_line = "public class MyClass extends ParentClass"
        self.assertTrue(writer.getvalue().strip().startswith(expected_line))
        expected_output = dedent("""\
        public class MyClass extends ParentClass
        {
        }""")
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_with_documentation(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        my_class = JavaClass(name="MyClass", documentation="Example Javadoc")
        my_class.render_to_string(java)
        self.assertTrue(writer.getvalue().strip().startswith('/**'))

        expected_output = dedent("""\
            /**
             * Example Javadoc
             */
            public class MyClass 
            {
            }""")
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_multiline_documentation(self):
        writer = io.StringIO()
        java = JavaSourceFile(None, writer=writer)
        my_class = JavaClass(name="MyClass", documentation="Example multiline Javadoc\nSecond line")
        my_class.render_to_string(java)
        self.assertTrue(writer.getvalue().strip().startswith('/**'))

        expected_output = dedent("""\
            /**
             * Example multiline Javadoc
             * Second line
             */
            public class MyClass 
            {
            }""")
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "java")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_missing_name(self):
        my_class = JavaClass()
        self.assertRaises(AttributeError, my_class.render_to_string, None)


if __name__ == "__main__":
    unittest.main()
