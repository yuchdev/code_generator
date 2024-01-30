from code_generation.java.source_file import JavaSourceFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.function_generator import JavaFunction
from code_generation.java.variable_generator import JavaVariable

__doc__ = """Example of generating Java class

Expected output:


"""

java = JavaSourceFile('java_variable.java')

java_class = JavaClass(name="MyClass")

java_class.add_variable(
    JavaVariable(
        name="m_my_member_variable",
        type="int",
        is_class_member=True,
        access_modifier="private",
        documentation="Example Javadoc class member"
    )
)

java_class.render_to_string(java)
