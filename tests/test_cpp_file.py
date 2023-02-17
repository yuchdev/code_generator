import os
import unittest
import filecmp

from code_generation.core.code_generator import CppFile
from code_generation.cpp.cpp_variable import CppVariable
from code_generation.cpp.cpp_enum import CppEnum
from code_generation.cpp.cpp_array import CppArray
from code_generation.cpp.cpp_function import CppFunction
from code_generation.cpp.cpp_class import CppClass

__doc__ = """
Unit tests for C++ code generator
"""


class TestCppFileIo(unittest.TestCase):
    """
    Test C++ code generation by writing to file
    """

    def test_cpp_array(self):
        """
        Test C++ variables generation
        """
        cpp = CppFile('array.cpp')
        arrays = []
        a1 = CppArray(name='array1', type='int', is_const=True, array_size=5)
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
        self.assertTrue(os.path.exists('array.cpp'))
        if os.path.exists('array.cpp'):
            os.remove('array.cpp')

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

        def const_method_body(_, cpp):
            cpp('return m_var1;')

        def virtual_method_body(_, cpp):
            cpp('return 0;')

        def static_method_body(_, cpp):
            cpp('return 0;')

        my_class.add_method(CppClass.CppMethod(name="GetParam",
                                               ret_type="int",
                                               is_const=True,
                                               implementation_handle=const_method_body))

        my_class.add_method(CppClass.CppMethod(name="VirtualMethod",
                                               ret_type="int",
                                               is_virtual=True,
                                               implementation_handle=virtual_method_body))

        my_class.add_method(CppClass.CppMethod(name="PureVirtualMethod",
                                               ret_type="void",
                                               is_virtual=True,
                                               is_pure_virtual=True))

        my_class.add_method(CppClass.CppMethod(name="StaticMethodMethod",
                                               ret_type="int",
                                               is_static=True,
                                               implementation_handle=static_method_body))

        my_class.declaration().render_to_string(my_class_h)
        my_class.definition().render_to_string(my_class_cpp)

        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'class.cpp'))
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'class.h'))
        my_class_cpp.close()
        my_class_h.close()
        self.assertTrue(os.path.exists('class.cpp'))
        if os.path.exists('class.cpp'):
            os.remove('class.cpp')
        self.assertTrue(os.path.exists('class.h'))
        if os.path.exists('class.h'):
            os.remove('class.h')

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
        if os.path.exists('enum.cpp'):
            os.remove('enum.cpp')

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
        functions[2].render_to_string_implementation(cpp)

        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'func.cpp'))
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'func.h'))
        cpp.close()
        hpp.close()
        if os.path.exists('func.cpp'):
            os.remove('func.cpp')
        if os.path.exists('func.h'):
            os.remove('func.h')

    def test_cpp_variable(self):
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
        if os.path.exists('var.cpp'):
            os.remove('var.cpp')


if __name__ == "__main__":
    unittest.main()
