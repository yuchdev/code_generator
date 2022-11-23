from code_generator import code_generator
from code_generator import cpp_generator

# Create a new code file
cpp = code_generator.CodeFile('example.cpp')
cpp('int i = 0;')

# Create a new variabel 'x'
x_variable = cpp_generator.CppVariable(
    name='x',
    type='int const&',
    is_static=True,
    is_constexpr=True,
    initialization_value='42')
x_variable.render_to_string(cpp)

# Create a new variabel 'name'
name_variable = cpp_generator.CppVariable(
    name='name',
    type='char*',
    is_extern=True)
name_variable.render_to_string(cpp)


# Generated C++ code
"""
int i = 0;
static constexpr int const& x = 42;
extern char* name;
"""
