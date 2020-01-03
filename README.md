C++ Code Generator
==============

Simple and straightforward code generator for creating C++ code. It also could be used for generating code in any programming language. Written in Python, works both with Python 2 and 3

Every C++ element could render its current state to a string that could be evaluated as 
a legal C++ construction.
Some elements could be rendered to a pair of representations (i.e. declaration and definition)

### Special thanks

Thanks to Eric Reynolds, the idea of this project mainly based on his article published on
http://www.codeproject.com/Articles/571645/Really-simple-Cplusplus-code-generation-in-Python

However, this solution has been both simplified and extended compared to the initial idea.

## Usage examples

### Generate C++ code from Python code

#### 1 Creating variables

##### 1.1 Python code
```

cpp = CodeFile('example.cpp')
cpp('int i = 0;')
```

##### 1.2 Generated C++ code
```
int i = 0;
```
#### 2 Creating classes and structures

##### 2.1 Python code
```
cpp = CppFile('example.cpp')
with cpp.block('class A', ';'):
    cpp.label('public:')
    cpp('int m_classMember1;')
    cpp('double m_classMember2;')
```

##### 2.2 Generated C++ code
```
class A
{
public:
    int m_classMember1;
    double m_classMember2;
};
```

#### 3 Rendering `CppClass` objects to C++ declaration and implementation

##### 3.1 Python code

```cpp_class = CppClass(name = 'MyClass', is_struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    is_static = True,
    is_const = True,
    initialization_value = 255))
```
 
##### 3.2 Generated C++ declaration

```struct MyClass
{
    static const size_t m_var;
}
```
 
#### 3.3 Generated C++ implementation
```
const size_t MyClass::m_var = 255;
```

Module `cpp_generator.py` highly depends on parent `code_generator.py`, as it uses
code generating and formatting primitives implemented there.
 
The main object referenced from `code_generator.py` is `CppFile`, 
which is passed as a parameter to `render_to_string(cpp)` Python method

It could also be used for composing more complicated C++ code,
that does not supported by `cpp_generator`

Class `ANSICodeStyle` is responsible for code formatting. Re-implement it if you wish to apply any other formatting style.
 
 
It support:

- functional calls:
```
cpp('int a = 10;')
```
 
- `with` semantic:
```
with cpp.block('class MyClass', ';')
    class_definition(cpp)
```
 
- append code to the last string without EOL:
```
cpp.append(', p = NULL);')
```
 
- empty lines:
```
cpp.newline(2)
```
 
