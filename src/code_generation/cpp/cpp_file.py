from code_generation.core.code_generator import CodeFile

__doc__ = """
"""


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
