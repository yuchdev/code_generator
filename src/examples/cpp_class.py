from code_generation.cpp.source_file import CppSourceFile
from code_generation.cpp.class_generator import CppClass
from code_generation.cpp.variable_generator import CppVariable

__doc__ = """Example of generating C++ class and struct

Expected output:
struct MyClass
{
    static size_t GetVar();
    static const size_t m_var;
};

static const size_t MyClass::m_var = 255;

size_t MyClass::GetVar()
{
    return m_var;
}

"""

cpp = CppSourceFile('class.cpp')
cpp_class = CppClass(name="MyClass", is_struct=True)

cpp_class.add_variable(
    CppVariable(
        name="m_var",
        type="size_t",
        is_static=True,
        is_const=True,
        value="255"
    )
)


def method_body(c):
    c('return m_var;')


cpp_class.add_method(
    CppClass.CppMethod(
        name="GetVar",
        ret_type="size_t",
        is_static=True,
        implementation=method_body
    )
)

cpp_class.render_to_string(cpp)
