# Pythonic Code Generator

Simple and straightforward generator for algorithmic creating of program code. 
In general, it could be used for generating code in any programming language,
however, at the moment it offers specific implementations for C++, Java and HTML.

Written in Python, used to work both with Python 2 and 3, however, 
implementation for Python 2 is deprecated and has not been supported for a while.

## Code Generation Usecases

Programmatic source code generation can have a wide range of use cases, including:

* Code generation for any repetitive tasks, such as generating getters and setters or creating CRUD operations
* Object serialization: Generating code to serialize and deserialize objects
* Language translations: Converting code from one programming language to another
* Formatting reports: Generating custom report files, such as HTML/CSS
* Database interactions: Generating code to interact with databases, such as generating SQL statements
* API generation: Generating API endpoints, requests and responses, and documentation for web services
* Mocking and testing: Generating code to create mock objects and test data
* Prototyping: Generating code to quickly prototype and experiment with new ideas.
* Integration with other systems: Generating code to integrate with other systems, such as web services or system RPC calls

Overall, programmatic source code generation can help improve development efficiency, reduce human error, and automate repetitive tasks.

## Installation

`pip install code_generation`

## Quick Start

### C++

TODO

```python
from code_generation import CppFile, CppFunction, CppVariable
```

## C++

The project initially was created to generate C++ code, and it is still the most mature implementation.
It is based on a bit of a different approach than other languages, because C++ language constructions
(like C++ classes and functions) include declarations and definitions (implementations). 
Declaration usually placed in header files (`*.h`), while definition is in source files (`*.cpp`).

Every C++ element could render its current state to a string that could be evaluated as 
a legal C++ construction, in two places: declaration and definition.

### Usage examples

#### Generate C++ code from Python code

##### Creating variables

###### Python code
```python
cpp = CodeFile('example.cpp')
cpp('int i = 0;')

x_variable = CppVariable(name='x', type='int const&', is_static=True, is_constexpr=True, initialization_value='42')
x_variable.render_to_string(cpp)

name_variable = CppVariable(name='name', type='char*', is_extern=True)
name_variable.render_to_string(cpp)
```

###### Generated C++ code
```c++
int i = 0;
static constexpr int const& x = 42;
extern char* name;
```

##### Creating functions

###### Python code
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

###### Generated C++ code
```c++
/// Calculates and returns the factorial of \p n.
constexpr int factorial(int n)
{
    return n <= 1 ? 1 : (n * factorial(n - 1));
}
```

##### Creating classes and structures

###### Python code
```python
cpp = CppFile('example.cpp')
with cpp.block('class A', ';'):
    cpp.label('public:')
    cpp('int m_classMember1;')
    cpp('double m_classMember2;')
```

###### Generated C++ code
```c++
class A
{
public:
    int m_classMember1;
    double m_classMember2;
};
```

##### Rendering `CppClass` objects to C++ declaration and implementation

###### Python code

```python
cpp_class = CppClass(name = 'MyClass', is_struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    is_static = True,
    is_const = True,
    initialization_value = 255))
```
 
###### Generated C++ declaration

```c++
struct MyClass
{
    static const size_t m_var;
}
```
 
###### Generated C++ implementation
```c++
const size_t MyClass::m_var = 255;
```

### Implementation Notes

#### CppFile

Module `core.code_generator` provides basic code generating and 
formatting functionality, that could be used for generating code in any language.
 
The main object referenced from `code_generator` is `CppFile`, 
which is passed as a parameter to `render_to_string(cpp)` Python method

It could also be used for composing more complicated C++ code,
that may be not supported by `cpp.*` classes.

It supports:

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

#### ANSICodeStyle

Class `ANSICodeStyle` is responsible for code formatting.
Re-implement it if you wish to apply any other formatting style.
 

## Java

TODO

## HTML

HTML code generation is implemented in `html.*` modules.
It was added to the project mostly to generate HTML reports.

## Maintenance

### Executing unit tests
The following command will execute the unit tests.

```bash
python -m unittest tests/test_cpp_file.py
python -m unittest tests/test_cpp_function_writer.py
python -m unittest tests/test_cpp_variable_writer.py
python -m unittest tests/test_html_writer.py
```

### Updating unit tests assets
After changing reference data for the unit test the test assets needs to be updated to successfully pass the unit tests.

```bash
python create_assets.py --assets test_assets
```

After executing that command, the fixed data under `tests/test_assets` will be updated and will need to be committed to git.
 
### Special thanks

Thanks to Eric Reynolds, for the initial idea of code generation in Python.
http://www.codeproject.com/Articles/571645/Really-simple-Cplusplus-code-generation-in-Python
