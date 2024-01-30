from code_generation.java.source_file import JavaSourceFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.function_generator import JavaFunction
from code_generation.java.variable_generator import JavaVariable

__doc__ = """Example of generating Java class

Expected output:
public class MyClass {

    /**
     * Example Javadoc method
     */
    public final synchronized MyClassMethod() 
    {
        return 42;
    }
}

"""

java = JavaSourceFile('java_method.java')
java_class = JavaClass(name="MyClass")


def method_implementation(c):
    c("return 42;")


java_class.add_method(
    JavaFunction(
        name="MyClassMethod",
        is_final=True,
        is_synchronized=True,
        implementation=method_implementation,
        documentation="Example Javadoc method"
    )
)

java_class.render_to_string(java)
