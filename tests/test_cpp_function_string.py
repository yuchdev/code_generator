import unittest
import io
from textwrap import dedent

from code_generation.code_generator import CppFile
from code_generation.cpp_function import CppFunction

__doc__ = """
Unit tests for C++ code generator
"""


def handle_to_factorial(_, cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')


class TestCppFunctionStringIo(unittest.TestCase):
    """
    Test C++ function generation by writing to StringIO
    """

    @staticmethod
    def handle_to_factorial(_, cpp):
        cpp('return n < 1 ? 1 : (n * factorial(n - 1));')

    def test_is_constexpr_raises_error_when_implementation_value_is_none(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int", is_constexpr=True)
        self.assertRaises(RuntimeError, func.render_to_string, cpp)

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int",
                           implementation_handle=TestCppFunctionStringIo.handle_to_factorial, is_constexpr=True)
        func.add_argument('int n')
        func.render_to_string(cpp)
        self.assertIn(dedent("""\
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }"""), writer.getvalue())

    def test_is_constexpr_render_to_string_declaration(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int",
                           implementation_handle=TestCppFunctionStringIo.handle_to_factorial, is_constexpr=True)
        func.add_argument('int n')
        func.render_to_string_declaration(cpp)
        self.assertIn(dedent("""\
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }"""), writer.getvalue())

    def test_README_example(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        factorial_function = CppFunction(name='factorial', ret_type='int', is_constexpr=True,
                                         implementation_handle=handle_to_factorial,
                                         documentation='/// Calculates and returns the factorial of p @n.')
        factorial_function.add_argument('int n')
        factorial_function.render_to_string(cpp)
        self.assertIn(dedent("""\
            /// Calculates and returns the factorial of p @n.
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }"""), writer.getvalue())


if __name__ == "__main__":
    unittest.main()
