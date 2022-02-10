C++ Code Generator
==============

Simple and straightforward code generator for creating C++ code. It also could be used for generating code in any programming language. Written in Python, works both with Python 2 and 3

Every C++ element could render its current state to a string that could be evaluated as 
a legal C++ construction.
Some elements could be rendered to a pair of representations (C++ classes and functions declaration and implementation)

### Special thanks

Thanks to Eric Reynolds, the idea of this project mainly based on his article published on
http://www.codeproject.com/Articles/571645/Really-simple-Cplusplus-code-generation-in-Python

However, this solution has been both simplified and extended compared to the initial idea.

## Usage examples

### Generate C++ code from Python code

#### Creating variables

##### Python code
```python
cpp = CodeFile('example.cpp')
cpp('int i = 0;')

x_variable = CppVariable(name='x', type='int const&', is_static=True, is_constexpr=True, initialization_value='42')
x_variable.render_to_string(cpp)

name_variable = CppVariable(name='name', type='char*', is_extern=True)
name_variable.render_to_string(cpp)
```

##### Generated C++ code
```c++
int i = 0;
static constexpr int const& x = 42;
extern char* name;
```

#### Creating functions

##### Python code
```python
def handle_to_factorial(self, cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')

cpp = CodeFile('example.cpp')

factorial_function = CppFunction(name='factorial',
    ret_type='int',
    is_constexpr=True,
    implementation_handle=handle_to_factorial,
    documentation='/// Calculates and returns the factorial of \p n.')
factorial_function.add_argument('int n')
factorial_function.render_to_string(cpp)
```

##### Generated C++ code
```c++
/// Calculates and returns the factorial of \p n.
constexpr int factorial(int n)
{
    return n <= 1 ? 1 : (n * factorial(n - 1));
}
```

#### Creating classes and structures

##### Python code
```python
cpp = CppFile('example.cpp')
with cpp.block('class A', ';'):
    cpp.label('public:')
    cpp('int m_classMember1;')
    cpp('double m_classMember2;')
```

##### Generated C++ code
```c++
class A
{
public:
    int m_classMember1;
    double m_classMember2;
};
```

#### Rendering `CppClass` objects to C++ declaration and implementation

##### Python code

```python
cpp_class = CppClass(name = 'MyClass', is_struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    is_static = True,
    is_const = True,
    initialization_value = 255))
```
 
##### Generated C++ declaration

```c++
struct MyClass
{
    static const size_t m_var;
}
```
 
#### Generated C++ implementation
```c++
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
```python
cpp('int a = 10;')
```
 
- `with` semantic:
```python
with cpp.block('class MyClass', ';')
    class_definition(cpp)
```
 
- append code to the last string without EOL:
```python
cpp.append(', p = NULL);')
```
 
- empty lines:
```python
cpp.newline(2)
```

## Maintainers

### Executing unit tests
The following command will execute the unit tests.

```bash
python -m unittest cpp_generator_tests.py
```

### Updating unit tests fixed data
After changing a unit test the fixed data needs to be updated to successfully pass the unit tests.

```bash
python -c 'cpp_generator_tests import generate_reference_code; generate_reference_code()'
```

After executing that command, the fixed data under `tests/test_assets` will be updated and will need to be committed to git.
 
