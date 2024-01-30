from code_generation.core.code_formatter import CodeFormat, CodeFormatterFactory

__doc__ = """
Simple and straightforward code generator that could be used for generating code 
on any programming language and to be a 'building block' for creating more complicated
code generators.

Thanks to Eric Reynolds, the code mainly based on his article published on
https://www.codeproject.com/Articles/571645/Really-simple-Cplusplus-code-generation-in-Python
Used under the Code Project Open License
https://www.codeproject.com/info/cpol10.aspx
 
Examples of usage:

1.
# Python code
cpp = SourceFile('example.cpp')
cpp('int i = 0;')
 
// Generated C++ code
int i = 0;
 
2.
# Python code
cpp = CppSourceFile('example.cpp')
with cpp.block('class A', ';'):
    cpp.label('public')
    cpp('int m_classMember1;')
    cpp('double m_classMember2;')
 
// Generated C++ code
class A
{
public:
    int m_classMember1;
    double m_classMember2;
};

Class `ANSICodeStyle` is responsible for code formatting. 
Re-implement it if you wish to apply any other formatting style.
"""


class SourceFile:
    """
    The class is a main instrument of code generation

    It can generate plain strings using functional calls
    Ex:
    code = SourceFile(python_src_file)
    code('import os, sys')

    Is supports 'with' semantic for indentation blocks creation
    Ex:
    # Python code
    with code('for i in range(0, 5):'):
        code('lst.append(i*i)')
        code('print(lst)')

    # Generated code:
    for i in range(0, 5):
        lst.append(i*i)
        print(lst)

    It can append code without line ending:
    Ex.
    # Python code
    cpp = SourceFile('ex.cpp')
    cpp('class Derived')
    cpp.append(' : public Base')

    // Generated C++ code
    class Derived : public Base

    And finally, it can insert a number of empty lines
    cpp.newline(3)
    """

    def __init__(self, filename, formatter=None, writer=None):
        """
        Creates a new source file
        @param: filename source file to create (rewrite if exists)
        @param: formatter code formatter to define rules of code indentation and line ending
        @param: writer optional writer to write output to
        """
        self.current_indent = 0
        self.last = None
        self.filename = filename
        if not isinstance(formatter, CodeFormat) and formatter is not None:
            raise TypeError(f"code_format must be an instance of {CodeFormat.__name__}")
        formatter = formatter if formatter is not None else CodeFormat.DEFAULT
        # Problem...
        self.code_formatter = CodeFormatterFactory.create(formatter, owner=self)
        self.out = writer if writer is not None else open(filename, "w")

    def close(self):
        """
        File created, just close the handle
        """
        self.out.close()
        self.out = None

    def write(self, text, indent=0, endline=True):
        """
        Write a new line with line ending
        """
        self.out.write(self.code_formatter.line(text, indent, endline))

    def append(self, x):
        """
        Append to the existing line without line ending
        """
        self.out.write(x)

    def __call__(self, text, indent=0, endline=True):
        """
        Supports 'object()' semantic, i.e.
        cpp('#include <iostream>')
        inserts appropriate line
        """
        self.write(text, indent, endline)

    def block(self, text, postfix=None):
        """
        Returns a stub for C++ {} close
        Supports 'with' semantic, i.e.
        with cpp.block(class_name, ';'):
        """
        if postfix is None:
            postfix = self.code_formatter.postfix
        return self.code_formatter(self, text, postfix)

    def endline(self, count=1):
        """
        Insert an endline
        """
        self.write(text=self.code_formatter.endline * count, indent=0, endline=False)

    def newline(self, n=1):
        """
        Insert one or several empty lines
        """
        for _ in range(n):
            self.write(text="", indent=0)
