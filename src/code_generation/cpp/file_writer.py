from code_generation.core.code_formatter import CodeFormat
from code_generation.core.source_file import SourceFile

__doc__ = """
"""


class CppFile(SourceFile):
    """
    This class extends SourceFile class with some specific C++ constructions
    """

    default_formatter = CodeFormat.ANSI_CPP

    def __init__(self, filename, writer=None):
        """
        Create C++ source file
        """
        SourceFile.__init__(self, filename, writer)

    def label(self, text):
        """
        Could be used for access specifiers or ANSI C labels, e.g.
        private:
        a:
        """
        self.write("{0}:".format(text), -1)
