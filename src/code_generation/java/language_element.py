from code_generation.core.code_file import CodeFile

__doc__ = """This module encapsulates Java code generation logic for main Java language primitives:
classes, methods and functions, variables, enums. Every Java element can render its current state to a string
that can be evaluated as a legal Java construction.

Example:
# Python code
java_class = JavaClass(name = 'MyClass')
java_class.add_variable(JavaVariable(name = "m_var",
    type = 'int',
    is_static = True,
    is_final = True,
    value = 10)) 
java_class.add_method(JavaFunction(name = 'main',
    return_type = 'void',
    is_static = True,
    arguments = [JavaArgument(name = 'args', type = 'String[]')]))
java_class.render_to_file('MyClass.java')

// Generated Java code
public class MyClass 
{
    public static final int m_var = 10;
    static public void main(String[] args)
    {
        return;
    }
}
"""


class JavaFile(CodeFile):
    """
    This class extends CodeFile class with some specific Java constructions
    """

    def __init__(self, filename, writer=None):
        """
        Create Java source file
        """
        CodeFile.__init__(self, filename, writer)

    def access(self, text):
        """
        Could be used for Java class access specifiers
        private:
        """
        self.write('{0}:'.format(text), -1)


class JavaLanguageElement:
    """
    The base class for all Java language elements.
    Contains dynamic storage for element properties
    (e.g. is_static for the variable is_abstract for the class etc.)
    """
    available_properties_names = {'name', 'ref_to_parent'}

    def __init__(self, properties):
        """
        @param: properties - Basic Java element properties (name, ref_to_parent)
        class is a parent for method or a member variable
        """
        self.name = properties.get('name')
        self.ref_to_parent = properties.get('ref_to_parent')

    def check_input_properties_names(self, input_property_names):
        """
        Ensure that all properties that are passed to the JavaLanguageElement are recognized.
        Raise an exception otherwise
        """
        unknown_properties = input_property_names.difference(self.available_properties_names)
        if unknown_properties:
            raise AttributeError(
                f'Error: try to initialize {self.__class__.__name__} with unknown property: {repr(unknown_properties)}')

    def init_class_properties(self, current_class_properties, input_properties_dict, default_property_value=None):
        """
        @param: current_class_properties - all available properties for the Java element to be generated
        @param: input_properties_dict - values for the initialized properties (e.g. is_abstract=True)
        @param: default_property_value - value for properties that are not initialized
        (None by default, because of the same as False semantic)
        """
        # Set all defined properties values (all undefined will be left with defaults)
        for (property_name, property_value) in input_properties_dict.items():
            if property_name not in JavaLanguageElement.available_properties_names:
                setattr(self, property_name, property_value)

        # Set all available properties to DefaultValue if they are not already set
        for property_name in current_class_properties:
            if property_name not in JavaLanguageElement.available_properties_names and not hasattr(self, property_name):
                setattr(self, property_name, default_property_value)

    def render_to_string(self, java):
        """
        @param: java - handle that supports code generation interface (see code_file.py)
        Typically it is passed to all child elements so that they can render their content
        """
        raise NotImplementedError('JavaLanguageElement is an abstract class')

    def parent_qualifier(self):
        """
        Generate a string for class name qualifiers
        Should be used for method implementation and static class members' definition.
        E.g.
        void MyClass.MyMethod()
        static int MyClass.m_staticVar = 0;

        Supports for nested classes, e.g.
        void MyClass.NestedClass.
        """
        full_parent_qualifier = ''
        parent = self.ref_to_parent
        # walk through all existing parents
        while parent:
            full_parent_qualifier = f'{parent.name}.{full_parent_qualifier}'
            parent = parent.ref_to_parent
        return full_parent_qualifier

    def fully_qualified_name(self):
        """
        Generate a string for the fully qualified name of the element
        Ex.
        MyClass.NestedClass.Method()
        """
        return f'{self.parent_qualifier()}{self.name}'
