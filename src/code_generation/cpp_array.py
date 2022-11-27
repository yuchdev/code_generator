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
