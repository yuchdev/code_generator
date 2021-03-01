import unittest
import filecmp
import os

from code_generator import *
from cpp_generator import *


__doc__ = '''
Unit tests for C++ code generator
'''


class TestCppGenerator(unittest.TestCase):
    '''
    Test C++ code generation
    '''

    def test_cpp_variables(self):
        '''
        Test C++ variables generation
        '''
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
                                 is_const=False)]

        for var in variables:
            var.render_to_string(cpp)
        cpp.close()
        expected_cpp = ['var.cpp']
        self.assertEqual(filecmp.cmpfiles('.', 'tests', expected_cpp)[0], expected_cpp)
        os.remove(cpp.filename)

    def test_cpp_arrays(self):
        '''
        Test C++ variables generation
        '''
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
        cpp.close()
        expected_cpp = ['array.cpp']
        self.assertEqual(filecmp.cmpfiles('.', 'tests', expected_cpp)[0], expected_cpp)
        os.remove(cpp.filename)

    def test_cpp_function(self):
        '''
        Test C++ functions generation
        '''
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
        expected_cpp = ['func.cpp']
        expected_h = ['func.h']
        cpp.close()
        hpp.close()
        self.assertEqual(filecmp.cmpfiles('.', 'tests', expected_cpp)[0], expected_cpp)
        self.assertEqual(filecmp.cmpfiles('.', 'tests', expected_h)[0], expected_h)
        os.remove(cpp.filename)
        os.remove(hpp.filename)

    def test_cpp_enum(self):
        '''
        Test C++ enums generation
        '''
        cpp = CppFile('enum.cpp')
        enum_elements = CppEnum(name='Items')
        for item in ['Chair', 'Table', 'Shelve']:
            enum_elements.add_item(item)
        enum_elements.render_to_string(cpp)

        enum_elements_custom = CppEnum(name='Items', prefix='it')
        for item in ['Chair', 'Table', 'Shelve']:
            enum_elements_custom.add_item(item)
        enum_elements_custom.render_to_string(cpp)

        cpp.close()
        expected_cpp = ['enum.cpp']
        self.assertEqual(filecmp.cmpfiles('.', 'tests', expected_cpp)[0], expected_cpp)
        os.remove(cpp.filename)

    def test_cpp_class(self):
        '''
        Test C++ classes generation
        '''
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

        my_class_cpp.close()
        my_class_h.close()
        expected_cpp = ['class.cpp']
        expected_h = ['class.h']
        self.assertEqual(filecmp.cmpfiles('.', 'tests', expected_cpp)[0], expected_cpp)
        self.assertEqual(filecmp.cmpfiles('.', 'tests', expected_h)[0], expected_h)
        os.remove(my_class_cpp.filename)
        os.remove(my_class_h.filename)


# Generate test data
def generate_enum():
    '''
    Generate model data (C++ enum)
    Do not call unless generator logic is changed
    '''
    cpp = CppFile('tests/enum.cpp')
    enum_elements = CppEnum(name='Items')
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements.add_item(item)
    enum_elements.render_to_string(cpp)

    enum_elements_custom = CppEnum(name='Items', prefix='it')
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements_custom.add_item(item)
    enum_elements_custom.render_to_string(cpp)
    cpp.close()


def generate_var():
    '''
    Generate model data (C++ variables)
    Do not call unless generator logic is changed
    '''
    cpp = CppFile('tests/var.cpp')
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
                             is_const=False)]

    for var in variables:
        var.render_to_string(cpp)

    cpp.close()


def generate_array():
    cpp = CppFile('tests/array.cpp')
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


def generate_func():
    '''
    Generate model data (C++ functions)
    Do not call unless generator logic is changed
    '''
    cpp = CppFile('tests/func.cpp')
    hpp = CppFile('tests/func.h')

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
    cpp.close()
    hpp.close()


def generate_class():
    '''
    Generate model data (C++ classes)
    Do not call unless generator logic is changed
    '''
    my_class_cpp = CppFile('tests/class.cpp')
    my_class_h = CppFile('tests/class.h')
    my_class = CppClass(name='MyClass', ref_to_parent=None)

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

    my_class.declaration().render_to_string(my_class_h)
    my_class.definition().render_to_string(my_class_cpp)
    my_class_cpp.close()
    my_class_h.close()


def generate_reference_code():
    '''
    Generate model data for C++ generator
    Do not call unless generator logic is changed
    '''
    generate_enum()
    generate_var()
    generate_array()
    generate_func()
    generate_class()


if __name__ == "__main__":
    unittest.main()