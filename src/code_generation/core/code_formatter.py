from enum import Enum, auto

__doc__ = """Formatters for different styles of code generation
"""


class CodeFormat(Enum):
    DEFAULT = auto()
    ANSI_CPP = auto()
    HTML = auto()
    CUSTOM = auto()


class CodeFormatter:
    """
    Base class for code close of different styles
    """
    default_endline = "\n"
    default_indent = " " * 4
    default_postfix = ""

    def __init__(self, indent=None, endline=None, postfix=None):
        """
        :param indent: sequence of symbols used for indentation (4 spaces, tab, etc.)
        :param endline: symbol used for line ending
        :param postfix: optional terminating symbol (e.g. ; for classes)
        """
        self.indent = self.default_indent if indent is None else indent
        self.endline = self.default_endline if endline is None else endline
        self.postfix = self.default_postfix if postfix is None else postfix


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
        @param: owner - SourceFile where text is written to
        @param: text - text opening C++ close
        @param indent: code indentation
        @param endline: custom endline sequence
        @param: postfix - optional terminating symbol (e.g. ; for classes)
        """
        super().__init__(indent, endline, postfix)
        self.owner = owner
        if self.owner.last is not None:
            with self.owner.last:
                pass
        self.owner.line("".join(text))
        self.owner.last = self

    def line(self, text, indent_level=0, endline=None):
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
        self.owner.line("{")
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
        self.owner.line("}" + self.postfix)


class HTMLCodeFormatter(CodeFormatter):
    """
    Class representing HTML close and its formatting style.
    It supports HTML DOM-tree style, like that:
    // HTML code
    <element attributes>
        // HTML content
    </element>
    """

    # Tab (indentation) symbol is 2 spaces
    html_indent = "  "

    def __init__(self, owner, element, *attrs, **kwattrs):
        """
        HTML code line
        Note that some attributes like 'class' are conflicting with Python's 'class' keyword.
        For such attributes prefer passing by list of strings `attrs`, e.g. `['class="class1"', 'id="id1"']`
        For other attributes prefer passing by dictionary `kwattrs`, e.g. `{id="id1"}`
        @param: owner - SourceFile where text is written to
        @param: element - HTML element name
        @param: attrs - optional opening tag content, e.g. attributes ['class="class1"', 'id="id1"']
        @param: kwattrs - optional opening tag attributes, e.g. {id="id1"}
        """
        super().__init__(indent=self.html_indent)
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
        self.owner.line(f"<{self.element}{self.attributes}>")
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
        self.owner.line(f"</{self.element}>")


class CodeFormatterFactory:
    """
    Factory class for code formatters
    """

    @staticmethod
    def create(code_format, owner, text, *args, **kwargs):
        """
        Create a new code formatter
        :param owner: source file where formatter is created
        :param text: code to format
        :param code_format: code formatter type
        :param args: formatter arguments
        :param kwargs: formatter keyword arguments
        :return: new code formatter
        """
        if code_format == CodeFormat.ANSI_CPP:
            return ANSICodeFormatter(owner=owner, text=text, *args, **kwargs)
        elif code_format == CodeFormat.HTML:
            return HTMLCodeFormatter(owner=owner, text=text, *args, **kwargs)
        elif code_format == CodeFormat.CUSTOM:
            return CodeFormatter(*args, **kwargs)
        elif code_format == CodeFormat.DEFAULT:
            # TODO: leave default formatter for respective source file
            return CodeFormatter(*args, **kwargs)
        else:
            raise ValueError(f"Unknown code format: {code_format}")
