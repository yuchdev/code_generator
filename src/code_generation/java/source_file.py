__doc__ = """The module encapsulates C++ code generation logics for main Java language primitives:
classes, methods, variables, enums.
"""

from code_generation.core.source_file import SourceFile
from code_generation.core.code_formatter import ANSICodeFormatter


class JavaSourceFile(SourceFile):

    Formatter = ANSICodeFormatter

    def __init__(self, filename, writer=None):
        SourceFile.__init__(self, filename, writer)
