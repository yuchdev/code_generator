__doc__ = """The module encapsulates C++ code generation logics for main Java language primitives:
classes, methods, variables, enums.
"""

from code_generation.core.code_file import CodeFile
from code_generation.core.code_style import ANSICodeStyle


class JavaFile(CodeFile):

    Formatter = ANSICodeStyle

    def __init__(self, filename, writer=None):
        CodeFile.__init__(self, filename, writer)
