import os

from code_generation.core.code_generator import CppFile
from code_generation.cpp.cpp_variable import CppVariable
from code_generation.cpp.cpp_enum import CppEnum
from code_generation.cpp.cpp_array import CppArray
from code_generation.cpp.cpp_function import CppFunction
from code_generation.cpp.cpp_class import CppClass

__doc__ = """Do not call this script unless generator logic is changed
"""

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


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

    functions = [CppFunction(name='GetParam', ret_type='int', implementation_handle=lambda _, cpp: cpp("return 1;")),
                 CppFunction(name='Calculate', ret_type='void', implementation_handle=lambda _, cpp: cpp("return;")),
                 CppFunction(name='GetAnswer', ret_type='int', implementation_handle=function_body),
                 CppFunction(name='Help', ret_type='char *', documentation='/// Returns the help documentation.', implementation_handle=lambda _, cpp: cpp("return nullptr;")),
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

    my_class.add_variable(CppVariable(name="m_var3",
                                      type="int",
                                      is_constexpr=True,
                                      is_static=True,
                                      is_class_member=True,
                                      initialization_value=42))

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

    my_class.add_method(CppClass.CppMethod(name="GetParam",
                                    ret_type="int",
                                    is_const=True,
                                    implementation_handle=method_body))

    my_class.add_method(CppClass.CppMethod(name="VirtualMethod",
                                    ret_type="int",
                                    is_virtual=True, implementation_handle=method_body))

    my_class.add_method(CppClass.CppMethod(name="PureVirtualMethod",
                                    ret_type="void",
                                    is_virtual=True,
                                    is_pure_virtual=True))

    example_class.add_method(CppClass.CppMethod(
        name="DoNothing",
        documentation="""\
            /**
             * Example multiline documentation.
             */""",
        ret_type="void", implementation_handle=lambda _, cpp: cpp("return;")),
    )

    my_class.declaration().render_to_string(my_class_h)
    example_class.declaration().render_to_string(my_class_h)
    my_class.definition().render_to_string(my_class_cpp)
    example_class.definition().render_to_string(my_class_cpp)
    my_class_cpp.close()
    my_class_h.close()


def generate_factorial(output_dir='.'):
    cpp = CppFile(os.path.join(output_dir, 'factorial.cpp'))
    h = CppFile(os.path.join(output_dir, 'factorial.h'))

    def handle_to_factorial(_, cpp_file):
        cpp_file('return n < 1 ? 1 : (n * factorial(n - 1));')

    func = CppFunction(name="factorial", ret_type="int",
                       implementation_handle=handle_to_factorial,
                       is_constexpr=True)
    func.add_argument('int n')
    func.render_to_string(cpp)
    func.render_to_string_declaration(h)
    cpp.close()
    h.close()


def generate_reference_code():
    """
    Generate model data for C++ generator
    Do not call unless generator logic is changed
    """
    asset_dir = os.path.join(PROJECT_DIR, 'new_assets')
    generate_enum(output_dir=asset_dir)
    generate_var(output_dir=asset_dir)
    generate_array(output_dir=asset_dir)
    generate_func(output_dir=asset_dir)
    generate_class(output_dir=asset_dir)
    generate_factorial(output_dir=asset_dir)


if __name__ == "__main__":
    generate_reference_code()
