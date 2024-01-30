from code_generation.cpp.source_file import CppSourceFile
from code_generation.cpp.function_generator import CppFunction

__doc__ = """Example of generating C++ function

Expected output:
int factorial(int n)
{
    return n < 1 ? 1 : (n * factorial(n - 1));
}
"""


def handle_to_factorial(cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')


cpp = CppSourceFile('function.cpp')
func = CppFunction(name="factorial", ret_type="int", implementation=handle_to_factorial)
func.add_argument('int n')
func.render_to_string(cpp)
