__doc__ = """Formatters for different styles of code generation
"""

import inspect
from enum import Enum, auto


class CodeFormat(Enum):
    DEFAULT = auto()
    ANSI_CPP = auto()
    HTML = auto()
    CUSTOM = auto()


class CodeFormatter:
    """
    Base class for code styles
    """
    default_endline = "\n"
    default_indent = " " * 4  # Default indentation is 4 spaces
    default_postfix = ""


class ANSICodeFormatter(CodeFormatter):
    """
    Class represents C++ {} close and its formatting style.
    It supports ANSI C style with braces on the new lines, like that:
    // C++ code
    {
        // C++ code
    };
    finishing postfix is optional (e.g. necessary for classes, unnecessary for namespaces)
    """

    def __init__(self, owner, text, indent=None, endline=None, postfix=None):
        """
        @param: owner - CodeFile where text is written to
        @param: text - text opening C++ close
        @param indent: code indentation
        @param endline: custom endline sequence
        @param: postfix - optional terminating symbol (e.g. ; for classes)
        """
        self.owner = owner
        if self.owner.last is not None:
            with self.owner.last:
                pass
        self.owner.write("".join(text))
        self.owner.last = self
        self.indent = self.set_option(indent)
        self.endline = self.set_option(endline)
        self.postfix = self.set_option(postfix)

    def set_option(self, option):
        """
        Set option to default value if it is None
        Helps to make sure that reasonable default value provided for the option
        :param option: usually, it is a string class attribute
        :return: option if it is not None, otherwise default value
        """
        attr_name = f"default_{inspect.currentframe().f_code.co_name}"
        return option if option is not None else getattr(self, attr_name)

    def write(self, text, indent_level=0, endline=None):
        """
        Write a new line with line ending
        """
        return (
            f"{self.indent * indent_level}"
            f"{text}"
            f"{self.endline if endline is None else endline}"
        )


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


class HTMLCodeFormatter(CodeFormatter):
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
        attributes = ""
        if "attributes" in kwattrs:
            if isinstance(kwattrs["attributes"], dict):
                attributes = "".join(
                    f' {key}="{value}"' for key, value in kwattrs["attributes"].items()
                )
            del kwattrs["attributes"]
        else:
            attributes = "".join(f" {attr}" for attr in attrs)
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
