import sys
from code_generation.code_style import ANSICodeStyle

__doc__ = """
Simple and straightforward code generator that could be used for generating code 
on any programming language and to be a 'building block' for creating more complicated
code generator.
Thanks to Eric Reynolds, the code mainly based on his article published on
https://www.codeproject.com/Articles/571645/Really-simple-Cplusplus-code-generation-in-Python
However, it was both significantly extended since then and also simplified.
 
Used under the Code Project Open License
https://www.codeproject.com/info/cpol10.aspx
 
Examples of usage:
 
1.
# Python code
cpp = CodeFile('example.cpp')
cpp('int i = 0;')
 
// Generated C++ code
int i = 0;
 
2.
# Python code
cpp = CppFile('example.cpp')
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


class CodeFile:
    """
    The class is a main instrument of code generation
    
    It can generate plain strings using functional calls
    Ex:
    code = CodeFile(python_src_file)
    code('import os, sys')
 
    Is supports 'with' semantic for indentation blocks creation
    Ex:
    # Python code
    with code('for i in range(0, 5):'):
        code('lst.append(i*i)')
 
    # Generated code:
    for i in range(0, 5):
        lst.append(i*i)
 
    It can append code to the last line:
    Ex.
    # Python code
    cpp = CodeFile('ex.cpp')
    cpp('class Derived')
    cpp.append(' : public Base')
 
    // Generated code
    class Derived : public Base
 
    And finally, it can insert a number of empty lines
    cpp.newline(3)
    """
    # Current formatting style (assigned as a class attribute to generate all files uniformly)
    Formatter = ANSICodeStyle
 
    def __init__(self, filename, writer=None):
        """
        Creates a new source file
        @param: filename source file to create (rewrite if exists)
        @param: writer optional writer to write output to
        """
        self.current_indent = 0
        self.last = None
        self.filename = filename
        if writer:
            self.out = writer
        else:
            self.out = open(filename, "w")
 
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
        self.out.write('{0}{1}{2}'.format(self.Formatter.indent * (self.current_indent+indent),
                                          text,
                                          self.Formatter.endline if endline else ''))
 
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
        
    def block(self, text, postfix=''):
        """
        Returns a stub for C++ {} close
        Supports 'with' semantic, i.e.
        cpp.block(class_name, ';'):
        """
        return CodeFile.Formatter(self, text, postfix)

    def endline(self, count=1):
        """
        Insert an endline
        """
        self.write(CodeFile.Formatter.endline * count, endline=False)

    def newline(self, n=1):
        """
        Insert one or several empty lines
        """
        for _ in range(n):
            self.write('')
 

class CppFile(CodeFile):
    """
    This class extends CodeFile class with some specific C++ constructions
    """
    def __init__(self, filename, writer=None):
        """
        Create C++ source file
        """
        CodeFile.__init__(self, filename, writer)
        
    def label(self, text):
        """
        Could be used for access specifiers or ANSI C labels, e.g.
        private:
        a:
        """
        self.write('{0}:'.format(text), -1)


def cpp_example():
    cpp = CppFile('example.cpp')
    with cpp.block('class A', ';'):
        cpp.label('public')
        cpp('int m_classMember1;')
        cpp('double m_classMember2;')


def main():
    cpp_example()
    return 0


if __name__ == '__main__':
    sys.exit(main())

