__doc__ = """The module encapsulates C++ code generation logics for main C++ language primitives:
classes, methods and functions, variables, enums.
Every C++ element could render its current state to a string that could be evaluated as 
a legal C++ construction.

Some elements could be rendered to a pair of representations (i.e. declaration and definition)

Example:
# Python code
cpp_class = CppClass(name = 'MyClass', is_struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    is_static = True,
    is_const = True,
    initialization_value = 255))

// Generated C++ declaration
struct MyClass
{
    static const size_t m_var;
}

// Generated C++ definition
const size_t MyClass::m_var = 255;

You can use CppFile for composing more complicated C++ code,
which is not supported by CppLanguageElement

It supports:

- functional calls:
cpp('int a = 10;')

- 'with' semantic:
with cpp.block('class MyClass', ';')
    class_definition(cpp)

- append code to the last string without EOL:
cpp.append(', p = NULL);')

- empty lines:
cpp.newline(2)

For more detailed information see CodeFile and CppFile documentation.
"""


###########################################################################
# Declaration/Implementation helpers
class CppDeclaration(object):
    """
    declaration/Implementation pair is used to split one element code generation to
    declaration and implementation parts
    E.g. method declaration
    struct Obj
    {
        int GetItem() const;
    }

    ... and method implementation
    int Obj::GetItem() const {...}

    That could be necessary to use unified render_to_string() interface, that is impossible for
    C++ primitives having two string representations (i.e. declaration and definition)
    """

    def __init__(self, cpp_element):
        self.cpp_element = cpp_element

    def render_to_string(self, cpp):
        self.cpp_element.render_to_string_declaration(cpp)


class CppImplementation(object):
    """
    See declaration description
    """

    def __init__(self, cpp_element):
        self.cpp_element = cpp_element

    def render_to_string(self, cpp):
        self.cpp_element.render_to_string_implementation(cpp)


class CppLanguageElement(object):
    """
    The base class for all C++ language elements.
    Contains dynamic storage for element properties
    (e.g. is_static for the variable is_virtual for the class method etc.)
    """
    availablePropertiesNames = {'name', 'ref_to_parent'}

    def __init__(self, properties):
        """
        @param: properties - Basic C++ element properties (name, ref_to_parent)
        class is a parent for method or a member variable
        """
        self.name = properties.get('name')
        self.ref_to_parent = properties.get('ref_to_parent')

    def check_input_properties_names(self, input_property_names):
        """
        Ensure that all properties that passed to the CppLanguageElement are recognized.
        Raise an exception otherwise
        """
        unknown_properties = input_property_names.difference(self.availablePropertiesNames)
        if unknown_properties:
            raise AttributeError(
                f'Error: try to initialize {self.__class__.__name__} with unknown property: {repr(unknown_properties)}')

    def init_class_properties(self, current_class_properties, input_properties_dict, default_property_value=None):
        """
        @param: current_class_properties - all available properties for the C++ element to be generated
        @param: input_properties_dict - values for the initialized properties (e.g. is_const=True)
        @param: default_property_value - value for properties that are not initialized
        (None by default, because of same as False semantic)
        """
        # Set all available properties to DefaultValue
        for propertyName in current_class_properties:
            if propertyName not in CppLanguageElement.availablePropertiesNames:
                setattr(self, propertyName, default_property_value)

        # Set all defined properties values (all undefined will be left with defaults)
        for (propertyName, propertyValue) in input_properties_dict.items():
            if propertyName not in CppLanguageElement.availablePropertiesNames:
                setattr(self, propertyName, propertyValue)

    def render_to_string(self, cpp):
        """
        @param: cpp - handle that supports code generation interface (see code_generator.py)
        Typically it is passed to all child elements so that render their content
        """
        raise NotImplementedError('CppLanguageElement is an abstract class')

    def parent_qualifier(self):
        """
        Generate string for class name qualifiers
        Should be used for methods implementation and static class members definition.
        Ex.
        void MyClass::MyMethod()
        int MyClass::m_staticVar = 0;

        Supports for nested classes, e.g.
        void MyClass::NestedClass::
        """
        full_parent_qualifier = ''
        parent = self.ref_to_parent
        # walk through all existing parents
        while parent:
            full_parent_qualifier = f'{parent.name}::{full_parent_qualifier}'
            parent = parent.ref_to_parent
        return full_parent_qualifier

    def fully_qualified_name(self):
        """
        Generate string for fully qualified name of the element
        Ex.
        MyClass::NestedClass::Method()
        """
        return f'{self.parent_qualifier()}{self.name}'
