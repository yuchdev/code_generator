cpp = CodeFile('example.cpp')
cpp('int i = 0;')

x_variable = CppVariable(name='x', type='int const&', is_static=True, is_constexpr=True, initialization_value='42')
x_variable.render_to_string(cpp)

name_variable = CppVariable(name='name', type='char*', is_extern=True)
name_variable.render_to_string(cpp)


##### Generated C++ code
"""
int i = 0;
static constexpr int const& x = 42;
extern char* name;
"""
