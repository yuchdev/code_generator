__doc__ = """The module encapsulates C++ code generation logics for main Java language primitives:
classes, methods, variables, enums.
"""

from code_generator.core.code_style import ANSICodeStyle


class JavaFile:

    Formatter = ANSICodeStyle

    def __init__(self, filename, writer=None):
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

    def block(self, element, **attributes):
        """
        Returns a stub for HTML element
        Supports 'with' semantic, i.e.
        html.block(element='p', id='id1', name='name1'):
        """
        return self.Formatter(self, element=element, **attributes)

    def endline(self, count=1):
        """
        Insert an endline
        """
        self.write(self.Formatter.endline * count, endline=False)

    def newline(self, n=1):
        """
        Insert one or several empty lines
        """
        for _ in range(n):
            self.write('')


class JavaLanguageElement(object):
    """
    The base class for all Java language elements.
    Contains dynamic storage for element properties
    """
    availablePropertiesNames = {'name', 'ref_to_parent'}

    def __init__(self, properties):
        """
        @param: properties - Basic Java element properties (name, ref_to_parent)
        class is a parent for method or a member variable
        """
        self.name = properties.get('name')
        self.ref_to_parent = properties.get('ref_to_parent')
