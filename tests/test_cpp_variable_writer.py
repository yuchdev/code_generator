import unittest
import io

from code_generation.core.code_generator import CppFile
from code_generation.cpp.cpp_variable import CppVariable

__doc__ = """Unit tests for C++ code generator
"""


class TestCppVariableStringIo(unittest.TestCase):
    """
    Test C++ variable generation by writing to StringIO
    """

    def test_cpp_var(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        variables = CppVariable(name="var1",
                                type="char*",
                                is_class_member=False,
                                is_static=False,
                                is_const=True,
                                initialization_value='0')
        variables.render_to_string(cpp)
        print(writer.getvalue())
        self.assertEqual('const char* var1 = 0;\n', writer.getvalue())

    def test_is_constexpr_const_raises(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        var = CppVariable(name="COUNT", type="int", is_class_member=True, is_const=True,
                          is_constexpr=True, initialization_value='0')
        self.assertRaises(ValueError, var.render_to_string, cpp)

    def test_is_constexpr_no_implementation_raises(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        var = CppVariable(name="COUNT", type="int", is_class_member=True, is_constexpr=True)
        self.assertRaises(ValueError, var.render_to_string, cpp)

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        variables = CppVariable(name="COUNT",
                                type="int",
                                is_class_member=False,
                                is_constexpr=True,
                                initialization_value='0')
        variables.render_to_string(cpp)
        self.assertIn('constexpr int COUNT = 0;', writer.getvalue())

    def test_is_constexpr_render_to_string_declaration(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        variables = CppVariable(name="COUNT",
                                type="int",
                                is_class_member=True,
                                is_constexpr=True,
                                initialization_value='0')
        variables.render_to_string_declaration(cpp)
        self.assertIn('constexpr int COUNT = 0;', writer.getvalue())

    def test_is_extern_static_raises(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        var = CppVariable(name="var1", type="char*", is_static=True, is_extern=True)
        self.assertRaises(ValueError, var.render_to_string, cpp)

    def test_is_extern_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        v = CppVariable(name="var1", type="char*", is_extern=True)
        v.render_to_string(cpp)
        self.assertIn('extern char* var1;', writer.getvalue())


if __name__ == "__main__":
    unittest.main()
