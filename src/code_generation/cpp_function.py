from code_generation.cpp_generator import CppLanguageElement, CppDeclaration, CppImplementation
from textwrap import dedent


class CppFunction(CppLanguageElement):
    """
    The Python class that generates string representation for C++ function (not method!)
    Parameters are passed as plain strings('int a', 'void p = NULL' etc)
    Available properties:
    ret_type - string, return value for the method ('void', 'int'). Could not be set for constructors
    is_constexpr - boolean, const method prefix, could not be static
    documentation - string, '/// Example doxygen'
    implementation_handle - reference to a function that receives 'self' and C++ code generator handle
    (see code_generator.cpp) and generates method body without braces
    Ex.
    #Python code
    def functionBody(self, cpp): cpp('return 42;')
    f1 = CppFunction(name = 'GetAnswer',
                     ret_type = 'int',
                     documentation = '// Generated code',
                     implementation_handle = functionBody)

    // Generated code
    int GetAnswer()
    {
        return 42;
    }
    """
    availablePropertiesNames = {'ret_type',
                                'is_constexpr',
                                'implementation_handle',
                                'documentation',
                                'is_method'} | CppLanguageElement.availablePropertiesNames

    def __init__(self, **properties):

        # check properties
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppFunction, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)

        # arguments are plain strings
        # e.g. 'int* a', 'const string& s', 'size_t sz = 10'
        self.arguments = []
        self.implementation_handle = properties.get('implementation_handle')
        self.documentation = properties.get('documentation')

    def is_static(self):
        """
        Before function name, declaration only
        Static functions can't be const, virtual or pure virtual
        """
        return 'static' if self.is_static else ''

    def is_constexpr(self):
        """
        Before function name, declaration only
        Constexpr functions can't be const, virtual or pure virtual
        """
        return 'constexpr ' if self.is_constexpr else ''

    def is_virtual(self):
        """
        Before function name, could be in declaration or definition
        Virtual functions can't be static or constexpr
        """
        return 'virtual ' if self.is_virtual else ''

    def is_inline(self):
        """
        Before function name, could be in declaration or definition
        Inline functions can't be static, virtual or constexpr
        """
        return 'inline ' if self.is_inline else ''

    def ret_type(self):
        """
        Return type, could be in declaration or definition
        """
        return self.ret_type if self.ret_type else ''

    def is_pure_virtual(self):
        """
        After function name, declaration only
        Pure virtual functions must be virtual
        """
        return ' = 0' if self.is_pure_virtual else ''

    def is_const(self):
        """
        After function name, could be in declaration or definition
        Const functions can't be static, virtual or constexpr
        """
        return ' const' if self.is_const else ''

    def is_override(self):
        """
        After function name, could be in declaration or definition
        Override functions must be virtual
        """
        return ' override' if self.is_override else ''

    def is_final(self):
        """
        After function name, could be in declaration or definition
        Final functions must be virtual
        """
        return ' final' if self.is_final else ''

    # noinspection PyUnresolvedReferences
    def _sanity_check(self):
        """
        Check whether attributes compose a correct C++ code
        """
        if not self.is_method and (self.is_static or self.is_const or self.is_virtual or self.is_pure_virtual):
            raise RuntimeError('Non-member function could not be static, const or (pure)virtual')
        if self.is_method and self.is_inline and (self.is_virtual or self.is_pure_virtual):
            raise RuntimeError('Inline method could not be virtual')
        if self.is_method and self.is_constexpr and (self.is_virtual or self.is_pure_virtual):
            raise RuntimeError('Constexpr method could not be virtual')
        if self.is_method and self.is_const and self.is_static:
            raise RuntimeError('Static method could not be const')
        if self.is_method and self.is_const and self.is_virtual:
            raise RuntimeError('Virtual method could not be const')
        if self.is_method and self.is_const and self.is_pure_virtual:
            raise RuntimeError('Pure virtual method could not be const')
        if self.is_method and self.is_override and not self.is_virtual:
            raise RuntimeError('Override method should be virtual')
        if self.is_method and self.is_final and not self.is_virtual:
            raise RuntimeError('Final method should be virtual')
        if self.is_method and self.is_static and self.is_virtual:
            raise RuntimeError('Static method could not be virtual')
        if self.is_method and self.is_pure_virtual and not self.is_virtual:
            raise RuntimeError('Pure virtual method should have attribute is_virtual=True')
        if self.is_method and not self.ref_to_parent:
            raise RuntimeError('Method object could be a child of a CppClass only. Use CppClass.add_method()')
        if self.is_constexpr and not self.implementation_handle:
            raise RuntimeError("Method object must be initialized when 'constexpr'")

    def add_argument(self, argument):
        """
        @param: argument string representation of the C++ function argument ('int a', 'void p = NULL' etc)
        """
        self.arguments.append(argument)

    def implementation(self, cpp):
        """
        The method calls Python function that creates C++ method body if handle exists
        """
        if self.implementation_handle is not None:
            self.implementation_handle(self, cpp)

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
        By default method is rendered as a declaration together with implementation,
        like the method is implemented within the C++ class body, e.g.
        class A
        {
            void f()
            {
            ...
            }
        }
        """
        # check all properties for the consistency
        self._sanity_check()
        if self.documentation:
            cpp(dedent(self.documentation))
        with cpp.block(f'{self.is_virtual()}{self.is_constexpr()}{self.is_inline()}'
                       f'{self.ret_type()} {self.name}({", ".join(self.arguments)})'
                       f'{self.is_const()}{self.is_override()}{self.is_final()}{self.is_pure_virtual()}'):
            self.implementation(cpp)

    def render_to_string_declaration(self, cpp):
        """
        Special case for a method declaration string representation.
        Generates just a function signature terminated by ';'
        Example:
        int GetX() const;
        """
        # check all properties for the consistency
        self._sanity_check()
        if self.is_constexpr:
            if self.documentation:
                cpp(dedent(self.documentation))
            self.render_to_string(cpp)
        else:
            cpp(f'{self.is_virtual()}{self.is_inline()}'
                f'{self.ret_type()} {self.name}({", ".join(self.arguments)})'
                f'{self.is_const()}{self.is_override()}{self.is_final()}{self.is_pure_virtual()};')

    def render_to_string_implementation(self, cpp):
        """
        Special case for a method implementation string representation.
        Generates method string in the form
        Example:
        int MyClass::GetX() const
        {
        ...
        }
        Generates method body if self.implementation_handle property exists
        """
        # check all properties for the consistency
        self._sanity_check()
        if self.documentation and not self.is_constexpr:
            cpp(dedent(self.documentation))
        with cpp.block('{0}{1} {2}{3}({4}){5}{6}'.format(
                '/*virtual*/' if self.is_virtual else '',
                self.ret_type if self.ret_type else '',
                '{0}'.format(self.parent_qualifier()) if self.is_method else '',
                self.name,
                ', '.join(self.arguments),
                ' const ' if self.is_const else '',
                ' = 0' if self.is_pure_virtual else '')):
            self.implementation(cpp)
