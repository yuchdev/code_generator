from code_generation.cpp_generator import CppLanguageElement

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
    value = 255))
 
// Generated C++ declaration
struct MyClass
{
    static const size_t m_var;
}
 
// Generated C++ definition
const size_t MyClass::m_var = 255;
 
 
That module uses and highly depends on code_generator.py as it uses
code generating and formatting primitives implemented there.
 
The main object referenced from code_generator.py is CppFile, 
which is passed as a parameter to render_to_string(cpp) Python method
 
It could also be used for composing more complicated C++ code,
that does not supported by cpp_generator
 
It support:

- functional calls:
cpp('int a = 10;')
 
- 'with' semantic:
with cpp.block('class MyClass', ';')
    class_definition(cpp)
 
- append code to the last string without EOL:
cpp.append(', p = NULL);')
 
- empty lines:
cpp.newline(2)
 
For detailed information see code_generator.py documentation.
"""


# noinspection PyUnresolvedReferences
class CppVariable(CppLanguageElement):
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
    is_static - boolean, 'static' prefix
    is_extern - boolean, 'extern' prefix
    is_const - boolean, 'const' prefix
    is_constexpr - boolean, 'constexpr' prefix
    value - string, value to be initialized with.
        'a = value;' for automatic variables, 'a(value)' for the class member
    documentation - string, '/// Example doxygen'
    is_class_member - boolean, for appropriate definition/declaration rendering
    """
    availablePropertiesNames = {'type',
                                'is_static',
                                'is_extern',
                                'is_const',
                                'is_constexpr',
                                'value',
                                'documentation',
                                'is_class_member'} | CppLanguageElement.availablePropertiesNames

    def __init__(self, **properties):
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppVariable, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)
        if self.is_const and self.is_constexpr:
            raise RuntimeError("Variable object can be either 'const' or 'constexpr', not both")
        if self.is_constexpr and not self.value:
            raise RuntimeError("Variable object must be initialized when 'constexpr'")
        if self.is_static and self.is_extern:
            raise RuntimeError("Variable object can be either 'extern' or 'static', not both")

    def is_static(self):
        """
        @return: 'static' prefix, can't be used with 'extern'
        """
        return 'static ' if self.is_static else ''

    def is_extern(self):
        """
        @return: 'extern' prefix, can't be used with 'static'
        """
        return 'extern ' if self.is_extern else ''

    def is_const(self):
        """
        @return: 'const' prefix, can't be used with 'constexpr'
        """
        return 'const ' if self.is_const else ''

    def is_constexpr(self):
        """
        @return: 'constexpr' prefix, can't be used with 'const'
        """
        return 'constexpr ' if self.is_constexpr else ''

    def value(self):
        """
        @return: string, value to be initialized with
        """
        return self.value if self.value else ''

    def assignment(self, value):
        """
        Generates assignment statement for the variable, e.g.
        a = 10;
        b = 20;
        """
        return f'{self.name} = {value};'

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
        int a = 10;
        const double b = M_PI;
        """
        if self.is_class_member and not (self.is_static and self.is_const):
            raise RuntimeError('For class member variables use definition() and declaration() methods')
        else:
            if self.documentation:
                cpp(dedent(self.documentation))
            cpp(f'{self.is_static}{self.is_extern}{self.is_const}{self.is_constexpr}'
                f'{self.type} {self.assignment(self.init_with())};')

    def render_to_string_declaration(self, cpp):
        """
        Generates declaration for the class member variables, for example
        int m_var;
        """
        if not self.is_class_member:
            raise RuntimeError('For automatic variable use its render_to_string() method')

        if self.documentation and self.is_class_member:
            cpp(dedent(self.documentation))
        cpp(f'{self.is_static}{self.is_extern}{self.is_const}{self.is_constexpr}'
            f'{self.type} {self.name if not self.is_constexpr else self.assignment(self.value())};')

    def render_to_string_implementation(self, cpp):
        """
        Generates definition for the class member variable.
        Output depends on the variable type

        Generates something like
        int MyClass::m_my_static_var = 0;

        for static class members, and
        m_var(0)
        for non-static class members.
        That string could be used in constructor initialization string
        """
        if not self.is_class_member:
            raise RuntimeError('For automatic variable use its render_to_string() method')

        # generate definition for the static class member
        if not self.is_constexpr:
            if self.is_static:
                cpp(f'{self.is_static}{self.is_extern}{self.is_const}{self.is_constexpr}'
                    f'{self.type} {self.fully_qualified_name()} = {self.value()};')
            # generate definition for non-static static class member, e.g. m_var(0)
            # (string for the constructor initialization list)
            else:
                cpp(f'{self.name}({self.value()})')
