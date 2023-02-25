from code_generation.cpp.cpp_generator import CppLanguageElement, CppDeclaration, CppImplementation
from textwrap import dedent

__doc__ = """The module encapsulates C++ code generation logics for main C++ language primitives:
classes, methods and functions, variables, enums.
Every C++ element could render its current state to a string that could be evaluated as 
a legal C++ construction.

For detailed information see code_generator.py documentation.
"""


# noinspection PyUnresolvedReferences
class CppUsingType(CppLanguageElement):
    """
    The Python class that generates string representation for C++ variable (automatic or class member)
    For example:
    class MyClass
    {
        int m_var1;
        double m_var2;
        ...
    }
    Available properties:
    type - string, variable type
    initialization_value - string, initialization_value to be initialized with.
        'a = initialization_value;' for automatic variables, 'a(initialization_value)' for the class member
    documentation - string, '/// Example doxygen'
    is_class_member - boolean, for appropriate definition/declaration rendering
    """
    availablePropertiesNames = {'type',
                                'documentation',
                                'is_class_member'} | CppLanguageElement.availablePropertiesNames

    def __init__(self, **properties):
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppUsingType, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)

    def declaration(self):
        """
        @return: CppDeclaration wrapper, that could be used
        for declaration rendering using render_to_string(cpp) interface
        """
        return CppDeclaration(self)

    def definition(self):
        """
        @return: CppImplementation wrapper, that could be used
        for definition rendering using render_to_string(cpp) interface
        """
        return CppImplementation(self)

    def render_to_string(self, cpp):
        """
        Only automatic variables or static const class members could be rendered using this method
        Generates complete variable definition, e.g.
        """
        if self.documentation:
            cpp(dedent(self.documentation))
        cpp(f'using {self.name} = {self.type};')

    def render_to_string_declaration(self, cpp):
        """
        Generates declaration for the class member variables, for example
        int m_var;
        """
        if not self.is_class_member:
            raise RuntimeError(
                'For automatic variable use its render_to_string() method')

        if self.documentation and self.is_class_member:
            cpp(dedent(self.documentation))
        cpp(f'using {self.name} = {self.type};')

    def render_to_string_implementation(self, cpp):
        """
        Using has no implementation
        """
        return None
