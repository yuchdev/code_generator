__doc__ = """Formatters for different styles of code generation
"""


class ANSICodeStyle:
    """
    Class represents C++ {} close and its formatting style.
    It supports ANSI C style with braces on the new lines, like that:
    // C++ code
    {
        // C++ code
    };
    finishing postfix is optional (e.g. necessary for classes, unnecessary for namespaces)
    """

    # EOL symbol
    endline = "\n"
 
    # Tab (indentation) symbol
    indent = "\t"
 
    def __init__(self, owner, text, postfix):
        """
        @param: owner - CodeFile where text is written to
        @param: text - text opening C++ close
        @param: postfix - optional terminating symbol (e.g. ; for classes)
        """
        self.owner = owner
        if self.owner.last is not None:
            with self.owner.last:
                pass
        self.owner.write("".join(text))
        self.owner.last = self
        self.postfix = postfix
        
    def __enter__(self):
        """
        Open code block
        """
        self.owner.write("{")
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
        self.owner.write("}" + self.postfix)


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
