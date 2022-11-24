import unittest
import filecmp
import os
import io

from code_generation.code_generator import *
from code_generation.cpp_generator import *

__doc__ = """
Unit tests for C++ code generator
"""


def handle_to_factorial(_, cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')


class TestCppFunctionGenerator(unittest.TestCase):

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
                           implementation_handle=TestCppFunctionGenerator.handle_to_factorial, is_constexpr=True)
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
                           implementation_handle=TestCppFunctionGenerator.handle_to_factorial, is_constexpr=True)
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
                                         documentation='/// Calculates and returns the factorial of p n.')
        factorial_function.add_argument('int n')
        factorial_function.render_to_string(cpp)
        self.assertIn(dedent("""\
            /// Calculates and returns the factorial of p n.
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }"""), writer.getvalue())


class TestCppVariableGenerator(unittest.TestCase):

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


class TestCppGenerator(unittest.TestCase):
    """
    Test C++ code generation
    """

    def test_cpp_variables(self):
        generate_var(output_dir='.')
        expected_cpp = ['var.cpp']
        self.assertEqual(filecmp.cmpfiles('.', 'tests/test_assets', expected_cpp)[0], expected_cpp)
        os.remove(expected_cpp[0])

    def test_cpp_arrays(self):
        generate_array(output_dir='.')
        expected_cpp = ['array.cpp']
        self.assertEqual(filecmp.cmpfiles('.', 'tests/test_assets', expected_cpp)[0], expected_cpp)
        os.remove(expected_cpp[0])

    def test_cpp_function(self):
        generate_func(output_dir='.')
        expected_cpp = ['func.cpp']
        expected_h = ['func.h']
        self.assertEqual(filecmp.cmpfiles('.', 'tests/test_assets', expected_cpp)[0], expected_cpp)
        self.assertEqual(filecmp.cmpfiles('.', 'tests/test_assets', expected_h)[0], expected_h)
        os.remove(expected_cpp[0])
        os.remove(expected_h[0])

    def test_cpp_enum(self):
        generate_enum(output_dir='.')
        expected_cpp = ['enum.cpp']
        self.assertEqual(filecmp.cmpfiles('.', 'tests/test_assets', expected_cpp)[0], expected_cpp)
        os.remove(expected_cpp[0])

    def test_cpp_class(self):
        generate_class(output_dir='.')
        expected_cpp = ['class.cpp']
        expected_h = ['class.h']
        self.assertEqual(filecmp.cmpfiles('.', 'tests/test_assets', expected_cpp)[0], expected_cpp)
        self.assertEqual(filecmp.cmpfiles('.', 'tests/test_assets', expected_h)[0], expected_h)
        os.remove(expected_cpp[0])
        os.remove(expected_h[0])


# Generate test data
def generate_enum(output_dir='.'):
    """
    Generate model data (C++ enum)
    Do not call unless generator logic is changed
    """
    cpp = CppFile(os.path.join(output_dir, 'enum.cpp'))
    enum_elements = CppEnum(name='Items')
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements.add_item(item)
    enum_elements.render_to_string(cpp)

    enum_elements_custom = CppEnum(name='Items', prefix='it')
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements_custom.add_item(item)
    enum_elements_custom.render_to_string(cpp)

    enum_elements_custom = CppEnum(name='Items', prefix='')
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements_custom.add_item(item)
    enum_elements_custom.render_to_string(cpp)

    enum_elements_custom = CppEnum(name='Items', prefix='', add_counter=False)
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements_custom.add_item(item)
    enum_elements_custom.render_to_string(cpp)

    enum_elements_custom = CppEnum(name='Items', add_counter=False)
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements_custom.add_item(item)
    enum_elements_custom.render_to_string(cpp)

    cpp.close()


def generate_var(output_dir='.'):
    """
    Generate model data (C++ variables)
    Do not call unless generator logic is changed
    """
    cpp = CppFile(os.path.join(output_dir, 'var.cpp'))
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
                 CppVariable(name="var4",
                             type="int",
                             documentation='// A number',
                             is_class_member=False,
                             is_static=False,
                             is_const=False),
                 ]

    for var in variables:
        var.render_to_string(cpp)

    cpp.close()


def generate_array(output_dir='.'):
    cpp = CppFile(os.path.join(output_dir, 'array.cpp'))
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

    cpp.close()


def generate_func(output_dir='.'):
    """
    Generate model data (C++ functions)
    Do not call unless generator logic is changed
    """
    cpp = CppFile(os.path.join(output_dir, 'func.cpp'))
    hpp = CppFile(os.path.join(output_dir, 'func.h'))

    def function_body(_, cpp1):
        cpp1('return 42;')

    functions = [CppFunction(name='GetParam', ret_type='int'),
                 CppFunction(name='Calculate', ret_type='void'),
                 CppFunction(name='GetAnswer', ret_type='int', implementation_handle=function_body),
                 CppFunction(name='Help', ret_type='char *', documentation='/// Returns the help documentation.'),
                 ]
    for func in functions:
        func.render_to_string(hpp)
    for func in functions:
        func.render_to_string_declaration(hpp)
    for func in functions:
        func.render_to_string_implementation(cpp)
    cpp.close()
    hpp.close()


def generate_class(output_dir='.'):
    """
    Generate model data (C++ classes)
    Do not call unless generator logic is changed
    """
    my_class_cpp = CppFile(os.path.join(output_dir, 'class.cpp'))
    my_class_h = CppFile(os.path.join(output_dir, 'class.h'))
    my_class = CppClass(name='MyClass', ref_to_parent=None)
    example_class = CppClass(
        name='Example',
        documentation="""\
            /// An example
            /// class with
            /// multiline documentation""",
    )

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

    example_class.add_variable(CppVariable(
        name="m_var1",
        documentation="/// A number.",
        type="int"),
    )

    a2 = CppArray(name='array2', type='char*', is_const=True, is_static=True, )
    a2.add_array_item('"Item1"')
    a2.add_array_item('"Item2"')
    a3 = CppArray(name='array3', type='char*', is_static=True, is_const=True, newline_align=True)
    a3.add_array_item('"ItemNewline1"')
    a3.add_array_item('"ItemNewline2"')

    my_class.add_array(a2)
    my_class.add_array(a3)

    def method_body(_, cpp1):
        cpp1('return m_var1;')

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

    example_class.add_method(CppFunction(
        name="DoNothing",
        documentation="""\
            /**
             * Example multiline documentation.
             */""",
        ret_type="void"),
    )

    my_class.declaration().render_to_string(my_class_h)
    example_class.declaration().render_to_string(my_class_h)
    my_class.definition().render_to_string(my_class_cpp)
    example_class.definition().render_to_string(my_class_cpp)
    my_class_cpp.close()
    my_class_h.close()


def generate_reference_code():
    """
    Generate model data for C++ generator
    Do not call unless generator logic is changed
    """
    generate_enum(output_dir='test_assets')
    generate_var(output_dir='test_assets')
    generate_array(output_dir='test_assets')
    generate_func(output_dir='test_assets')
    generate_class(output_dir='test_assets')


if __name__ == "__main__":
    unittest.main()
