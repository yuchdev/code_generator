from code_generation.cpp_generator import CppLanguageElement, CppDeclaration, CppImplementation
from code_generation.cpp_function import CppFunction
from textwrap import dedent


class CppClass(CppLanguageElement):
    """
    The Python class that generates string representation for C++ class or struct.
    Usually contains a number of child elements - internal classes, enums, methods and variables.
    Available properties:
    is_struct - boolean, use 'struct' keyword for class declaration, 'class' otherwise
    documentation - string, '/// Example doxygen'

    Example of usage:

    # Python code
    cpp_class = CppClass(name = 'MyClass', is_struct = True)
    cpp_class.add_variable(CppVariable(name = "m_var",
        type = 'size_t',
        is_static = True,
        is_const = True,
        initialization_value = 255))

    def handle(cpp): cpp('return m_var;')

    cpp_class.add_method(CppFunction(name = "GetVar",
        ret_type = 'size_t',
        is_static = True,
        implementation_handle = handle))

    // Generated C++ declaration
    struct MyClass
    {
        static const size_t m_var;
        static size_t GetVar();
    }

    // Generated C++ definition
    const size_t MyClass::m_var = 255;

    size_t MyClass::GetVar()
    {
        return m_var;
    }
    """
    availablePropertiesNames = {'is_struct',
                                'documentation',
                                'parent_class'} | CppLanguageElement.availablePropertiesNames

    class CppMethod(CppFunction):
        """
        The Python class that generates string representation for C++ method
        Parameters are passed as plain strings('int a', 'void p = NULL' etc)
        Available properties:
        ret_type - string, return value for the method ('void', 'int'). Could not be set for constructors
        is_static - boolean, static method prefix
        is_const - boolean, const method prefix, could not be static
        is_virtual - boolean, virtual method postfix, could not be static
        is_pure_virtual - boolean, ' = 0' method postfix, could not be static
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
        int MyClass::GetAnswer()
        {
            return 42;
        }
        """
        availablePropertiesNames = {'ret_type',
                                    'is_static',
                                    'is_constexpr',
                                    'is_virtual',
                                    'is_inline',
                                    'is_pure_virtual',
                                    'is_const',
                                    'is_override',
                                    'is_final',
                                    'implementation_handle',
                                    'documentation'} | CppLanguageElement.availablePropertiesNames

        def __init__(self, **properties):
            # arguments are plain strings
            # e.g. 'int* a', 'const string& s', 'size_t sz = 10'
            self.arguments = []
            self.implementation_handle = properties.get('implementation_handle')
            self.documentation = properties.get('documentation')

            # check properties
            input_property_names = set(properties.keys())
            self.check_input_properties_names(input_property_names)
            super().__init__(**properties)
            self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                       input_properties_dict=properties)

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
            if self.is_inline and (self.is_virtual or self.is_pure_virtual):
                raise RuntimeError('Inline method could not be virtual')
            if self.is_constexpr and (self.is_virtual or self.is_pure_virtual):
                raise RuntimeError('Constexpr method could not be virtual')
            if self.is_const and self.is_static:
                raise RuntimeError('Static method could not be const')
            if self.is_const and self.is_virtual:
                raise RuntimeError('Virtual method could not be const')
            if self.is_const and self.is_pure_virtual:
                raise RuntimeError('Pure virtual method could not be const')
            if self.is_override and not self.is_virtual:
                raise RuntimeError('Override method should be virtual')
            if self.is_inline and (self.is_virtual or self.is_pure_virtual):
                raise RuntimeError('Inline method could not be virtual')
            if self.is_final and not self.is_virtual:
                raise RuntimeError('Final method should be virtual')
            if self.is_static and self.is_virtual:
                raise RuntimeError('Static method could not be virtual')
            if self.is_pure_virtual and not self.is_virtual:
                raise RuntimeError('Pure virtual method is also a virtual method')
            if not self.ref_to_parent:
                raise RuntimeError('Method object could be a child of a CppClass only. Use CppClass.add_method()')
            if self.is_constexpr and not self.implementation_handle:
                raise RuntimeError("Method object must be initialized when 'constexpr'")

        def add_argument(self, argument):
            """
            @param: argument string representation of the C++ function argument ('int a', 'void p = NULL' etc)
            """
            self.arguments.append(argument)

        def args(self):
            """
            @return: string arguments
            """
            return ", ".join(self.arguments)

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
                           f'{self.ret_type()} {self.fully_qualified_name()}({self.args()})'
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
                    f'{self.ret_type()} {self.name}({self.args()})'
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
            with cpp.block(f'{self.is_virtual()}{self.is_constexpr()}{self.is_inline()}'
                           f'{self.ret_type()} {self.fully_qualified_name()}({self.args()})'
                           f'{self.is_const()}{self.is_override()}{self.is_final()}{self.is_pure_virtual()}'):
                self.implementation(cpp)

    def __init__(self, **properties):
        self.is_struct = False
        self.documentation = None
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppClass, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)

        # aggregated classes
        self.internal_class_elements = []

        # class members
        self.internal_variable_elements = []

        # array class members
        self.internal_array_elements = []

        # class methods
        self.internal_method_elements = []

        # class enums
        self.internal_enum_elements = []

    def parent_class(self):
        """
        @return: parent class object
        """
        return self.parent_class if self.parent_class else ""

    def inherits(self):
        """
        @return: string representation of the inheritance
        """
        return f' : public {self.parent_class()}'

    ########################################
    # ADD CLASS MEMBERS
    def add_enum(self, enum):
        """
        @param: enum CppEnum instance
        """
        enum.ref_to_parent = self
        self.internal_enum_elements.append(enum)

    def add_variable(self, cpp_variable):
        """
        @param: cpp_variable CppVariable instance
        """
        cpp_variable.ref_to_parent = self
        cpp_variable.is_class_member = True
        self.internal_variable_elements.append(cpp_variable)

    def add_array(self, cpp_variable):
        """
        @param: cpp_variable CppVariable instance
        """
        cpp_variable.ref_to_parent = self
        cpp_variable.is_class_member = True
        self.internal_array_elements.append(cpp_variable)

    def add_internal_class(self, cpp_class):
        """
        Add nested class
        @param: cpp_class CppClass instance
        """
        cpp_class.ref_to_parent = self
        self.internal_class_elements.append(cpp_class)

    def add_method(self, method):
        """
        @param: method CppFunction instance
        """
        method.ref_to_parent = self
        method.is_method = True
        self.internal_method_elements.append(method)

    ########################################
    # RENDER CLASS MEMBERS
    def render_internal_classes_declaration(self, cpp):
        """
        Generates section of nested classes
        Could be placed both in 'private:' or 'public:' sections
        """
        for classItem in self.internal_class_elements:
            classItem.declaration().render_to_string(cpp)
            cpp.newline()

    def render_enum_section(self, cpp):
        """
        Render to string all contained enums
        """
        for enumItem in self.internal_enum_elements:
            enumItem.render_to_string(cpp)
            cpp.newline()

    def render_variables_declaration(self, cpp):
        """
        Render to string all contained variable class members
        """
        for varItem in self.internal_variable_elements:
            varItem.declaration().render_to_string(cpp)
            cpp.newline()

    def render_array_declaration(self, cpp):
        """
        Render to string all contained array class members
        """
        for arrItem in self.internal_array_elements:
            arrItem.declaration().render_to_string(cpp)
            cpp.newline()

    def render_methods_declaration(self, cpp):
        """
        Generates all class methods declaration
        Should be placed in 'public:' section
        """
        for funcItem in self.internal_method_elements:
            funcItem.render_to_string_declaration(cpp)
            cpp.newline()

    def render_static_members_implementation(self, cpp):
        """
        Generates definition for all static class variables
        int MyClass::my_static_array[] = {}
        """
        # generate definition for static variables
        static_vars = [variable for variable in self.internal_variable_elements if variable.is_static]
        for varItem in static_vars:
            varItem.definition().render_to_string(cpp)
            cpp.newline()
        for arrItem in self.internal_array_elements:
            arrItem.definition().render_to_string(cpp)
            cpp.newline()

        # do the same for nested classes
        for classItem in self.internal_class_elements:
            classItem.render_static_members_implementation(cpp)
            cpp.newline()

    def render_methods_implementation(self, cpp):
        """
        Generates all class methods declaration
        Should be placed in 'public:' section
        """
        # generate methods implementation section
        for funcItem in self.internal_method_elements:
            funcItem.render_to_string_implementation(cpp)
            cpp.newline()
        # do the same for nested classes
        for classItem in self.internal_class_elements:
            classItem.render_static_members_implementation(cpp)
            cpp.newline()

    ########################################
    # GROUP GENERATED SECTIONS
    def class_interface(self, cpp):
        """
        Generates section that generally used as an 'open interface'
        Generates string representation for enums, internal classes and methods
        Should be placed in 'public:' section
        """
        self.render_enum_section(cpp)
        self.render_internal_classes_declaration(cpp)
        self.render_methods_declaration(cpp)

    def private_class_members(self, cpp):
        """
        Generates section of class member variables.
        Should be placed in 'private:' section
        """
        self.render_variables_declaration(cpp)
        self.render_array_declaration(cpp)

    def render_to_string(self, cpp):
        """
        Render to string both declaration and definition.
        A rare case enough, because the only code generator handle is used.
        Typically class declaration is rendered to *.h file, and definition to *.cpp
        """
        self.render_to_string_declaration(cpp)
        self.render_to_string_implementation(cpp)

    # noinspection PyUnresolvedReferences
    def render_to_string_declaration(self, cpp):
        """
        Render to string class declaration.
        Typically handle to header should be passed as 'cpp' param
        """
        if self.documentation:
            cpp(dedent(self.documentation))

        with cpp.block(f'{self.class_type()} {self.name} {self.inherits()}', postfix=';'):

            # in case of struct all members meant to be public
            if not self.is_struct:
                cpp.label('public')
            self.class_interface(cpp)
            cpp.newline()

            # in case of struct all members meant to be public
            if not self.is_struct:
                cpp.label('private')
            self.private_class_members(cpp)

    def class_type(self):
        """
        @return: 'class' or 'struct' keyword
        """
        return 'struct' if self.is_struct else 'class'

    def render_to_string_implementation(self, cpp):
        """
        Render to string class definition.
        Typically handle to *.cpp file should be passed as 'cpp' param
        """
        cpp.newline(2)
        self.render_static_members_implementation(cpp)
        self.render_methods_implementation(cpp)

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