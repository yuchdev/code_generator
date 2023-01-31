import unittest
import filecmp
import io
from textwrap import dedent

from code_generation.code_generator import CppFile
from code_generation.cpp_variable import CppVariable
from code_generation.cpp_enum import CppEnum
from code_generation.cpp_array import CppArray
from code_generation.cpp_function import CppFunction
from code_generation.cpp_class import CppClass

__doc__ = """
Unit tests for C++ code generator
"""


def handle_to_factorial(_, cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')


class TestCppFunctionStringIo(unittest.TestCase):

    @staticmethod
    def handle_to_factorial(_, cpp):
        cpp('return n < 1 ? 1 : (n * factorial(n - 1));')

    def test_is_constexpr_raises_error_when_implementation_value_is_none(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int", is_constexpr=True)
        self.assertRaises(RuntimeError, func.render_to_string, cpp)

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int",
                           implementation_handle=TestCppFunctionStringIo.handle_to_factorial, is_constexpr=True)
        func.add_argument('int n')
        func.render_to_string(cpp)
        self.assertIn(dedent("""\
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }"""), writer.getvalue())

    def test_is_constexpr_render_to_string_declaration(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int",
                           implementation_handle=TestCppFunctionStringIo.handle_to_factorial, is_constexpr=True)
        func.add_argument('int n')
        func.render_to_string_declaration(cpp)
        self.assertIn(dedent("""\
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }"""), writer.getvalue())

    def test_README_example(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        factorial_function = CppFunction(name='factorial', ret_type='int', is_constexpr=True,
                                         implementation_handle=handle_to_factorial,
                                         documentation='/// Calculates and returns the factorial of p @n.')
        factorial_function.add_argument('int n')
        factorial_function.render_to_string(cpp)
        self.assertIn(dedent("""\
            /// Calculates and returns the factorial of p @n.
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }"""), writer.getvalue())


class TestCppVariableStringIo(unittest.TestCase):

    def test_cpp_var_via_writer(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        variables = CppVariable(name="var1",
                                type="char*",
                                is_class_member=False,
                                is_static=False,
                                is_const=True,
                                initialization_value='0')
        variables.render_to_string(cpp)
        self.assertEqual('const char* var1 = 0;\n', writer.getvalue())

    def test_is_constexpr_raises_error_when_is_const_true(self):
        self.assertRaises(RuntimeError, CppVariable, name="COUNT", type="int", is_class_member=True, is_const=True,
                          is_constexpr=True, initialization_value='0')

    def test_is_constexpr_raises_error_when_initialization_value_is_none(self):
        self.assertRaises(RuntimeError, CppVariable, name="COUNT", type="int", is_class_member=True, is_constexpr=True)

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

    def test_is_extern_raises_error_when_is_static_is_true(self):
        self.assertRaises(RuntimeError, CppVariable, name="var1", type="char*", is_static=True, is_extern=True)

    def test_is_extern_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        v = CppVariable(name="var1", type="char*", is_extern=True)
        v.render_to_string(cpp)
        self.assertIn('extern char* var1;', writer.getvalue())


class TestCppFileIo(unittest.TestCase):
    """
    Test C++ code generation
    """

    def test_cpp_variables(self):
        """
        Test C++ variables generation
        """
        cpp = CppFile('var.cpp')
        variables = [CppVariable(name="var1",
                                 type="char*",
                                 is_class_member=False,
                                 is_static=False,
                                 is_const=True,
                                 initialization_value='0'),
                     CppVariable(name="var2",
                                 type="int",
                                 is_class_member=False,
                                 is_static=True,
                                 is_const=False,
                                 initialization_value='0'),
                     CppVariable(name="var3",
                                 type="std::string",
                                 is_class_member=False,
                                 is_static=False,
                                 is_const=False),
                     CppVariable(name="var3",
                                 type="std::string",
                                 is_class_member=False,
                                 is_static=False,
                                 is_const=False)]

        for var in variables:
            var.render_to_string(cpp)
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'var.cpp'))
        cpp.close()

    def test_cpp_arrays(self):
        """
        Test C++ variables generation
        """
        cpp = CppFile('array.cpp')
        arrays = []
        a1 = CppArray(name='array1', type='int', is_const=True, arraySize=5)
        a1.add_array_items(['1', '2', '3'])
        a2 = CppArray(name='array2', type='const char*', is_const=True)
        a2.add_array_item('"Item1"')
        a2.add_array_item('"Item2"')
        a3 = CppArray(name='array3', type='const char*', is_const=True, newline_align=True)
        a3.add_array_item('"ItemNewline1"')
        a3.add_array_item('"ItemNewline2"')

        arrays.append(a1)
        arrays.append(a2)
        arrays.append(a3)

        for arr in arrays:
            arr.render_to_string(cpp)
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'array.cpp'))
        cpp.close()

    def test_cpp_function(self):
        """
        Test C++ functions generation
        """
        cpp = CppFile('func.cpp')
        hpp = CppFile('func.h')

        def function_body(_, cpp1):
            cpp1('return 42;')

        functions = [CppFunction(name='GetParam', ret_type='int'),
                     CppFunction(name='Calculate', ret_type='void'),
                     CppFunction(name='GetAnswer', ret_type='int', implementation_handle=function_body)]
        for func in functions:
            func.render_to_string(hpp)
        for func in functions:
            func.render_to_string_declaration(hpp)
        for func in functions:
            func.render_to_string_implementation(cpp)
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'func.cpp'))
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'func.h'))
        cpp.close()
        hpp.close()

    def test_cpp_enum(self):
        """
        Test C++ enums generation
        """
        cpp = CppFile('enum.cpp')
        enum_elements = CppEnum(name='Items')
        for item in ['Chair', 'Table', 'Shelve']:
            enum_elements.add_item(item)
        enum_elements.render_to_string(cpp)

        enum_elements_custom = CppEnum(name='Items', prefix='it')
        for item in ['Chair', 'Table', 'Shelve']:
            enum_elements_custom.add_item(item)
        enum_elements_custom.render_to_string(cpp)

        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'enum.cpp'))
        cpp.close()

    def test_cpp_class(self):
        """
        Test C++ classes generation
        """
        my_class_cpp = CppFile('class.cpp')
        my_class_h = CppFile('class.h')
        my_class = CppClass(name='MyClass')

        enum_elements = CppEnum(name='Items', prefix='wd')
        for item in ['One', 'Two', 'Three']:
            enum_elements.add_item(item)
        my_class.add_enum(enum_elements)

        nested_class = CppClass(name='Nested', is_struct=True)
        nested_class.add_variable(CppVariable(name="m_gcAnswer",
                                              type="size_t",
                                              is_class_member=True,
                                              is_static=True,
                                              is_const=True,
                                              initialization_value='42'))
        my_class.add_internal_class(nested_class)

        my_class.add_variable(CppVariable(name="m_var1",
                                          type="int",
                                          initialization_value='1'))

        my_class.add_variable(CppVariable(name="m_var2",
                                          type="int*"))

        a2 = CppArray(name='array2', type='char*', is_const=True, is_static=True, )
        a2.add_array_item('"Item1"')
        a2.add_array_item('"Item2"')
        a3 = CppArray(name='array3', type='char*', is_static=True, is_const=True, newline_align=True)
        a3.add_array_item('"ItemNewline1"')
        a3.add_array_item('"ItemNewline2"')

        my_class.add_array(a2)
        my_class.add_array(a3)

        def method_body(_, cpp):
            cpp('return m_var1;')

        my_class.add_method(CppFunction(name="GetParam",
                                        ret_type="int",
                                        is_method=True,
                                        is_const=True,
                                        implementation_handle=method_body))

        my_class.add_method(CppFunction(name="VirtualMethod",
                                        ret_type="int",
                                        is_method=True,
                                        is_virtual=True))

        my_class.add_method(CppFunction(name="PureVirtualMethod",
                                        ret_type="void",
                                        is_method=True,
                                        is_virtual=True,
                                        is_pure_virtual=True))

        my_class.declaration().render_to_string(my_class_h)
        my_class.definition().render_to_string(my_class_cpp)

        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'class.cpp'))
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'class.h'))
        my_class_cpp.close()
        my_class_h.close()


if __name__ == "__main__":
    unittest.main()
