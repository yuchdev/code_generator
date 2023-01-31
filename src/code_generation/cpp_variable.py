from code_generation.cpp_generator import CppLanguageElement, CppDeclaration, CppImplementation
from textwrap import dedent

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
    initialization_value - string, initialization_value to be initialized with.
        'a = initialization_value;' for automatic variables, 'a(initialization_value)' for the class member
    documentation - string, '/// Example doxygen'
    is_class_member - boolean, for appropriate definition/declaration rendering
    """
    availablePropertiesNames = {'type',
                                'is_static',
                                'is_extern',
                                'is_const',
                                'is_constexpr',
                                'initialization_value',
                                'documentation',
                                'is_class_member'} | CppLanguageElement.availablePropertiesNames

    def __init__(self, **properties):
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppVariable, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)

    def _sanity_check(self):
        """
        @raise: ValueError, if some properties are not valid
        """
        if self.is_const and self.is_constexpr:
            raise ValueError("Variable object can be either 'const' or 'constexpr', not both")
        if self.is_constexpr and not self.initialization_value:
            raise ValueError("Variable object must be initialized when 'constexpr'")
        if self.is_static and self.is_extern:
            raise ValueError("Variable object can be either 'extern' or 'static', not both")

    def _render_static(self):
        """
        @return: 'static' prefix, can't be used with 'extern'
        """
        return 'static ' if self.is_static else ''

    def _render_extern(self):
        """
        @return: 'extern' prefix, can't be used with 'static'
        """
        return 'extern ' if self.is_extern else ''

    def _render_const(self):
        """
        @return: 'const' prefix, can't be used with 'constexpr'
        """
        return 'const ' if self.is_const else ''

    def _render_constexpr(self):
        """
        @return: 'constexpr' prefix, can't be used with 'const'
        """
        return 'constexpr ' if self.is_constexpr else ''

    def _render_init_value(self):
        """
        @return: string, initialization_value to be initialized with
        """
        return self.initialization_value if self.initialization_value else ''

    def assignment(self, value):
        """
        Generates assignment statement for the variable, e.g.
        a = 10;
        b = 20;
        """
        return f'{self.name} = {value}'

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
        self._sanity_check()
        if self.is_class_member and not (self.is_static and self.is_const):
            raise RuntimeError('For class member variables use definition() and declaration() methods')
        elif self.is_extern:
            cpp(f'{self._render_extern()}{self.type} {self.name};')
        else:
            if self.documentation:
                cpp(dedent(self.documentation))
            cpp(f'{self._render_static()}{self._render_const()}{self._render_constexpr()}'
                f'{self.type} {self.assignment(self._render_init_value())};')

    def render_to_string_declaration(self, cpp):
        """
        Generates declaration for the class member variables, for example
        int m_var;
        """
        if not self.is_class_member:
            raise RuntimeError('For automatic variable use its render_to_string() method')

        if self.documentation and self.is_class_member:
            cpp(dedent(self.documentation))
        cpp(f'{self._render_static()}{self._render_extern()}{self._render_const()}{self._render_constexpr()}'
            f'{self.type} {self.name if not self.is_constexpr else self.assignment(self._render_init_value())};')

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
                cpp(f'{self._render_static()}{self._render_const()}{self._render_constexpr()}'
                    f'{self.type} {self.fully_qualified_name()} = {self._render_init_value()};')
            # generate definition for non-static static class member, e.g. m_var(0)
            # (string for the constructor initialization list)
            else:
                cpp(f'{self.name}({self._render_init_value()})')
