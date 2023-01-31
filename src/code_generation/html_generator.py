import sys


class HTMLStyle:
    """
    Class representing HTML close and its formatting style.
    It supports HTML DOM-tree style, like that:
    // HTML code
    <element attributes>
        // HTML content
    </element>
    """
    # EOL symbol
    endline = "\n"

    # Tab (indentation) symbol is 2 spaces
    indent = "  "

    def __init__(self, owner, element, *attrs, **kwattrs):
        """
        @param: owner - CodeFile where text is written to
        @param: element - HTML element name
        @param: attrs - optional opening tag content, like attributes ['class="class1"', 'id="id1"']
        @param: kwattrs - optional opening tag attributes, like class="class1", id="id1"
        """
        self.owner = owner
        if self.owner.last is not None:
            with self.owner.last:
                pass
        self.element = element
        attributes = "".join(f' {attr}' for attr in attrs)
        attributes += "".join(f' {key}="{value}"' for key, value in kwattrs.items())
        self.attributes = attributes
        self.owner.last = self

    def __enter__(self):
        """
        Open code block
        """
        self.owner.write(f"<{self.element}{self.attributes}>")
        self.owner.current_indent += 1
        self.owner.last = None

    def __exit__(self, *_):
        """
        Close code block
        """
        if self.owner.last is not None:
            with self.owner.last:
                pass
        self.owner.current_indent -= 1
        self.owner.write(f"</{self.element}>")


class HtmlFile:

    Formatter = HTMLStyle

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


def html_example():
    html = HtmlFile('ex.html')
    with html.block(element='p', id='id1', name='name1'):
        html('Text')


def main():
    html_example()
    return 0


if __name__ == '__main__':
    sys.exit(main())
