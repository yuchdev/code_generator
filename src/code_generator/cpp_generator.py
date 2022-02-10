__doc__ = """The module encapsutates C++ code generation logics for main C++ language primitives:
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

from textwrap import dedent


###########################################################################
# declaration/Implementation helpers
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


# C++ language element generators
class CppLanguageElement(object):
    """
    The base class for all C++ language elements.
    Contains dynamic storage for element properties
    (e.g. is_static for the variable is_virtual for the class method etc)
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
        void MyClass::NestedClass::Method()
        """
        full_qualified_name = ''
        parent = self.ref_to_parent
        # walk though all existing parents
        while parent:
            full_qualified_name = f'{parent.name}::{full_qualified_name}'
            parent = parent.ref_to_parent
        return full_qualified_name


class CppFunction(CppLanguageElement):
    """
    The Python class that generates string representation for C++ function or method
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
    int GetAnswer()
    {
        return 42;
    }
    """
    availablePropertiesNames = {'ret_type',
                                'is_static',
                                'is_const',
                                'is_constexpr',
                                'is_virtual',
                                'is_pure_virtual',
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

    # noinspection PyUnresolvedReferences
    def __sanity_check(self):
        """
        Check whether attributes compose a correct C++ code
        """
        if not self.is_method and (self.is_static or self.is_const or self.is_virtual or self.is_pure_virtual):
            raise RuntimeError('Non-member function could not be static, const or (pure)virtual')
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
        By default method is rendered as a declaration mutual with implementation,
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
        self.__sanity_check()
        if self.documentation and self.is_constexpr:
            cpp(dedent(self.documentation))
        with cpp.block('{0}{1}{2} {3}({4}){5}{6}'.format(
                'virtual ' if self.is_virtual else '',
                'constexpr ' if self.is_constexpr else '',
                self.ret_type if self.ret_type else '',
                self.name,
                ', '.join(self.arguments),
                ' const ' if self.is_const else '',
                ' = 0' if self.is_pure_virtual else '')):
            self.implementation(cpp)

    def render_to_string_declaration(self, cpp):
        """
        Special case for a method declaration string representation.
        Generates just a function signature terminated by ';'
        Example:
        int GetX() const;
        """
        # check all properties for the consistency
        self.__sanity_check()
        if self.is_constexpr:
            if self.documentation:
                cpp(dedent(self.documentation))
            with cpp.block('{0}constexpr {1} {2}({3}){4}{5}'.format(
                    'virtual ' if self.is_virtual else '',
                    self.ret_type if self.ret_type else '',
                    self.name,
                    ', '.join(self.arguments),
                    ' const ' if self.is_const else '',
                    ' = 0' if self.is_pure_virtual else '')):
                self.implementation(cpp)
        else:
            cpp('{0}{1} {2}({3}){4}{5};'.format('virtual ' if self.is_virtual else '',
                                                self.ret_type if self.ret_type else '',
                                                self.name,
                                                ', '.join(self.arguments),
                                                ' const ' if self.is_const else '',
                                                ' = 0' if self.is_pure_virtual else ''))

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
        self.__sanity_check()
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


class CppEnum(CppLanguageElement):
    """
    The Python class that generates string representation for C++ enum
    All enum elements are explicitly initialized with incremented values

    Available properties:
    prefix - string, prefix added to every enum element, 'e' by default ('eItem1')

    Example of usage:
    # Python code
    enum_elements = CppEnum(name = 'Items')
    for item in ['Chair', 'Table', 'Shelve']:
        enum_elements.add_item(enum_elements.name)

    // Generated C++ code
    enum Items
    {
        eChair = 0,
        eTable = 1,
        eShelve = 2,
        eItemsCount = 3
    }
    """
    availablePropertiesNames = {'prefix'} | CppLanguageElement.availablePropertiesNames

    def __init__(self, **properties):
        # check properties
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppEnum, self).__init__(properties)

        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)

        # place enum items here
        self.enum_items = []

    def add_item(self, item):
        """
        @param: item - string representation for the enum element
        """
        self.enum_items.append(item)

    def add_items(self, items):
        """
        @param: items - list of strings
        """
        self.enum_items.extend(items)

    # noinspection PyUnresolvedReferences
    def render_to_string(self, cpp):
        """
        Generates a string representation for the enum
        It always contains a terminating value that shows count of enum elements
        enum MyEnum
        {
            eItem1 = 0,
            eItem2 = 1,
            eMyEnumCount = 2
        }
        """
        counter = 0
        with cpp.block('enum {0}'.format(self.name), ';'):
            for item in self.enum_items:
                cpp('{0}{1} = {2},'.format(self.prefix if self.prefix else 'e', item, counter))
                counter += 1
            last_element = '{0}{1}Count'.format(self.prefix if self.prefix else 'e', self.name)
            cpp(last_element)


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
    initialization_value - string, value to be initialized with.
        'a = value;' for automatic variables, 'a(value)' for the class member
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
        if self.is_const and self.is_constexpr:
            raise RuntimeError("Variable object can be either 'const' or 'constexpr', not both")
        if self.is_constexpr and not self.initialization_value:
            raise RuntimeError("Variable object must be initialized when 'constexpr'")
        if self.is_static and self.is_extern:
            raise RuntimeError("Variable object can be either 'extern' or 'static', not both")

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
            cpp('{0}{1}{2} {3}{4};'.format('static ' if self.is_static else 'extern ' if self.is_extern else '',
                                           'const ' if self.is_const else 'constexpr ' if self.is_constexpr else '',
                                           self.type,
                                           self.name,
                                           ' = {0}'.format(
                                               self.initialization_value) if self.initialization_value else ''))

    def render_to_string_declaration(self, cpp):
        """
        Generates declaration for the class member variables, for example
        int m_var;
        """
        if not self.is_class_member:
            raise RuntimeError('For automatic variable use its render_to_string() method')

        if self.documentation and self.is_class_member:
            cpp(dedent(self.documentation))
        cpp('{0}{1}{2} {3};'.format(
            'static ' if self.is_static else '',
            'const ' if self.is_const else 'constexpr ' if self.is_constexpr else '',
            self.type,
            self.name if not self.is_constexpr else '{} = {}'.format(self.name, self.initialization_value)))

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
        if self.is_static:
            cpp('{0}{1} {2}{3} {4};'.format('const ' if self.is_const else '',
                                            self.type,
                                            '{0}'.format(self.parent_qualifier()),
                                            self.name,
                                            ' = {0}'.format(
                                                self.initialization_value if self.initialization_value else '')))

        # generate definition for non-static static class member
        # (string for the constructor initialization list)
        else:
            cpp('{0}({1})'.format(self.name, self.initialization_value if self.initialization_value else ''))


# noinspection PyUnresolvedReferences
class CppArray(CppLanguageElement):
    """
    The Python class that generates string representation for C++ array (automatic or class member)
    For example:

    int arr[] = {1,2,2};
    double doubles[5] = {1.0,2.0};

    class MyClass
    {
        int m_arr1[10];
        static double m_arr2[];
        ...
    }
    Available properties:

    type - string, variable type
    is_static - boolean, 'static' prefix
    is_const - boolean, 'const' prefix
    arraySize - integer, size of array if required
    is_class_member - boolean, for appropriate definition/declaration rendering
    newline_align - in the array definition rendering place every item on the new string
    """
    availablePropertiesNames = {'type',
                                'is_static',
                                'is_const',
                                'arraySize',
                                'is_class_member',
                                'newline_align'} | CppLanguageElement.availablePropertiesNames

    def __init__(self, **properties):
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppArray, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)
        # array elements
        self.items = []

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

    def add_array_item(self, item):
        """
        If variable is an array it could contain a number of items
        @param: item - string
        """
        self.items.append(item)

    def add_array_items(self, items):
        """
        If variable is an array it could contain a number of items
        @param: items - list of strings
        """
        self.items.extend(items)

    def __render_value(self, cpp):
        """
        Render to string array items
        """
        if not self.items:
            raise RuntimeError('Empty arrays do not supported')
        for item in self.items[:-1]:
            cpp('{0},'.format(item))
        cpp('{0}'.format(self.items[-1]))

    def render_to_string(self, cpp):
        """
        Generates definition for the C++ array.
        Output depends on the array type

        Generates something like
        int my_array[5] = {1, 2, 0};
        const char* my_array[] = {"Hello", "World"};

        That method is used for generating automatic (non-class members) arrays
        For class members use render_to_string_declaration/render_to_string_implementation methods
        """
        if self.is_class_member and not (self.is_static and self.is_const):
            raise RuntimeError('For class member variables use definition() and declaration() methods')

        # newline-formatting of array elements makes sense only if array is not empty
        if self.newline_align and self.items:
            with cpp.block('{0}{1}{2} {3}{4} = '.format('static ' if self.is_static else '',
                                                        'const ' if self.is_const else '',
                                                        self.type,
                                                        self.name,
                                                        '[{0}]'.format(self.arraySize if self.arraySize else '')), ';'):
                # iterate over array items
                self.__render_value(cpp)
        else:
            cpp('{0}{1}{2} {3}{4} = {5};'.format('static ' if self.is_static else '',
                                                 'const ' if self.is_const else '',
                                                 self.type,
                                                 self.name,
                                                 '[{0}]'.format(self.arraySize if self.arraySize else ''),
                                                 '{{{0}}}'.format(', '.join(self.items)) if self.items else 'NULL'))

    def render_to_string_declaration(self, cpp):
        """
        Generates declaration for the C++ array.
        Non-static arrays-class members do not supported

        Example:
        static int my_class_member_array[];
        """
        if not self.is_class_member:
            raise RuntimeError('For automatic variable use its render_to_string() method')

        cpp('{0}{1}{2} {3}{4};'.format('static ' if self.is_static else '',
                                       'const ' if self.is_const else '',
                                       self.type,
                                       self.name,
                                       '[{0}]'.format(self.arraySize if self.arraySize else '')))

    def render_to_string_implementation(self, cpp):
        """
        Generates definition for the C++ array.
        Output depends on the array type

        Example:
        int MyClass::m_my_static_array[] =
        {
            ...
        };

        Non-static arrays-class members do not supported
        """
        if not self.is_class_member:
            raise RuntimeError('For automatic variable use its render_to_string() method')

        # generate definition for the static class member arrays only
        # other types does not supported
        if not self.is_static:
            raise RuntimeError('Only static arrays as class members are supported')

        # newline-formatting of array elements makes sense only if array is not empty
        if self.newline_align and self.items:
            with cpp.block('{0}{1}{2} {3}{4}{5} = '.format('static ' if self.is_static else '',
                                                           'const ' if self.is_const else '',
                                                           self.type,
                                                           '{0}'.format(self.parent_qualifier()),
                                                           self.name,
                                                           '[{0}]'.format(self.arraySize if self.arraySize else '')),
                           ';'):
                # iterate over array items
                self.__render_value(cpp)
        else:
            cpp('{0}{1}{2} {3}{4}{5} = {6};'.format('static ' if self.is_static else '',
                                                    'const ' if self.is_const else '',
                                                    self.type,
                                                    '{0}'.format(self.parent_qualifier()),
                                                    self.name,
                                                    '[{0}]'.format(self.arraySize if self.arraySize else ''),
                                                    '{{{0}}}'.format(', '.join(self.items)) if self.items else 'NULL'))


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

    def __init__(self, **properties):
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
        class_type = 'struct' if self.is_struct else 'class'
        with cpp.block('{0} {1} {2}'.format(class_type,
                                            self.name,
                                            ' : public {0}'.format(self.parent_class) if self.parent_class else ''),
                       ';'):

            # in case of struct all members meant to be public
            if not self.is_struct:
                cpp.label('public')
            self.class_interface(cpp)
            cpp.newline()

            # in case of struct all members meant to be public
            if not self.is_struct:
                cpp.label('private')
            self.private_class_members(cpp)

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
