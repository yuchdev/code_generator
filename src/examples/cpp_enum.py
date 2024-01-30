from code_generation.cpp.source_file import CppSourceFile
from code_generation.cpp.enum_generator import CppEnum

__doc__ = """Example of generating C++ enum and enum class

Expected output:
    enum MyEnum
    {
        eItem1 = 0,
        eItem2 = 1,
        eItem3 = 2,
        eMyEnumCount = 3
    };

    enum class MyEnumClass
    {
        eItem1 = 0,
        eItem2 = 1,
        eItem3 = 2,
        eMyEnumCount = 3
    };

"""

cpp = CppSourceFile('array.cpp')
enum = CppEnum(name="MyEnum", prefix="e")
enum.add_items(["Item1", "Item2", "Item3"])
enum.render_to_string(cpp)

enum = CppEnum(name="MyEnumClass", prefix="e", enum_class=True)
enum.add_items(["Item1", "Item2", "Item3"])
enum.render_to_string(cpp)
