import unittest
import io
from textwrap import dedent

from code_generation.java.file_writer import JavaFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.variable_generator import JavaVariable
from code_generation.java.function_generator import JavaFunction


class TestJavaClassStringIo(unittest.TestCase):
    """
    Test Java class generation by writing to StringIO
    """

    def test_java_class(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        my_class = JavaClass(name="MyClass")
        var1 = JavaVariable(name="myVariable", type="int", value=10)
        method1 = JavaFunction(name="getVar", return_type="int", implementation="return myVariable;")
        my_class.add_variable(var1)
        my_class.add_method(method1)
        my_class.render_to_string(java)
        expected_output = dedent("""\
            public class MyClass
            {
                int myVariable = 10;
                int getVar()
                {
                    return myVariable;
                }
            }
        """)
        self.assertEqual(writer.getvalue(), expected_output)

    def test_java_class_with_parent_class(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        my_class = JavaClass(name="MyClass", parent_class="ParentClass")
        my_class.render_to_string(java)
        expected_output = "public class MyClass extends ParentClass {"
        self.assertTrue(writer.getvalue().strip().startswith(expected_output))

    def test_java_class_with_documentation(self):
        writer = io.StringIO()
        java = JavaFile(None, writer=writer)
        my_class = JavaClass(name="MyClass", documentation="/** Example Javadoc */")
        my_class.render_to_string(java)
        expected_output = dedent("""\
            /**
            * Example Javadoc
            */
            public class MyClass
            {""")
        self.assertTrue(writer.getvalue().strip().startswith(expected_output))

    def test_missing_name(self):
        my_class = JavaClass()
        self.assertRaises(RuntimeError, my_class.render_to_string, None)


if __name__ == "__main__":
    unittest.main()
