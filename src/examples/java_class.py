from code_generation.java.file_writer import JavaFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.function_generator import JavaFunction
from code_generation.java.variable_generator import JavaVariable

__doc__ = """Example of generating Java class

Expected output:
public class MyClass {
    /**
     * Example Javadoc class member
     */
    private int m_my_member_variable;

    /**
     * Example Javadoc method
     */
    public final synchronized MyClassMethod() 
    {
        m_my_member_variable = 10;
    }
}

"""

java = JavaFile('java_class.java')

java_class = JavaClass(name="MyClass")

java_class.add_variable(
    JavaVariable(
        name="m_my_member_variable",
        type="int",
        is_class_member=True,
        access_modifier="private",
        documentation="/** Example Javadoc class member */"
    )
)


def method_implementation(c):
    c("m_my_member_variable = 10;")


java_class.add_method(
    JavaFunction(
        name="MyClassMethod",
        is_final=True,
        is_synchronized=True,
        implementation=method_implementation,
        documentation="/** Example Javadoc method */"
    )
)

java_class.render_to_string(java)
