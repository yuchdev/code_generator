from code_generation.java.file_writer import JavaFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.enum_generator import JavaEnum

__doc__ = """Example of generating Java enum

Expected output:

"""

java = JavaFile('java_enum.java')

java_class = JavaClass(name="MyClass")

java_enum = JavaEnum(name="MyEnum", values=["1", "2", "0"], is_class_member=True)
java_class.add_variable(java_enum)

java_class.render_to_string(java)
