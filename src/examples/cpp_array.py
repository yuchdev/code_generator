from code_generation.cpp.source_file import CppSourceFile
from code_generation.cpp.array_generator import CppArray

__doc__ = """Example of generating C++ array

Expected output:
int my_array[5] = {1, 2, 0};

"""

cpp = CppSourceFile('array.cpp')
arr = CppArray(name="my_array", type="int", array_size=5)
arr.add_array_items(["1", "2", "0"])
arr.render_to_string(cpp)
