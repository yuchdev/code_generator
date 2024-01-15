from code_generation.java.file_writer import JavaFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.array_generator import JavaArray

__doc__ = """Example of generating Java array

Expected output:
public class MyClass
{
    public static int[] my_array = {1, 2, 0};
    public static int[] empty_array = new int[0];
}

"""

java = JavaFile('java_array.java')

java_class = JavaClass(name="MyClass")

java_array = JavaArray(name="my_array", type="int")
java_array.add_items(["1", "2", "0"])
java_class.add_variable(java_array)

java_array_empty = JavaArray(name="empty_array", type="int", values=[])
java_class.add_variable(java_array_empty)

java_class.render_to_string(java)
