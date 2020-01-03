C++ Code Generator
==============

Simple and straightforward code generator for creating C++ code. It also could be used for generating code in any programming language. Written in Python, works both with Python 2 and 3

Every C++ element could render its current state to a string that could be evaluated as 
a legal C++ construction.
Some elements could be rendered to a pair of representations (i.e. declaration and definition)
 
# Usage example

## Python code
`cpp_class = CppClass(name = 'MyClass', is_struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    is_static = True,
    is_const = True,
    initialization_value = 255))`
 
## Generated C++ declaration
`struct MyClass
{
    static const size_t m_var;
}
 
// Generated C++ definition
const size_t MyClass::m_var = 255;`
 
 
That module uses and highly depends on code_generator.py model as it uses
code generating and formatting primitives implemented there.
 
The main object referenced from code_generator.py is CppFile, 
that passed as a parameter to render_to_string(cpp) Python method
 
It could be used for composing more complicated C++ constructuions,
that does not supported by cpp_generator
 
It supports 
- functional calls:
`cpp('int a = 10;')`
 
- 'with; symantic:
`with cpp.block('class MyClass', ';')
    class_definition(cpp)`
 
- append to the last string without EOL:
`cpp.append(', p = NULL);')`
 
- empty lines:
`cpp.newline(2)`
 
