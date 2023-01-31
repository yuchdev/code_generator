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


class CppEnum(CppLanguageElement):
    """
    The Python class that generates string representation for C++ enum
    All enum elements are explicitly initialized with incremented values

    Available properties:
    prefix - string, prefix added to every enum element, 'e' by default ('eItem1')
    add_counter - boolean, terminating value that shows count of enum elements added, 'True' by default.

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
    availablePropertiesNames = {'prefix',
                                'enum_class',
                                'add_counter'} | CppLanguageElement.availablePropertiesNames

    def __init__(self, **properties):
        self.enum_class = False
        # check properties
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppEnum, self).__init__(properties)

        self.init_class_properties(current_class_properties=self.availablePropertiesNames,
                                   input_properties_dict=properties)

        # place enum items here
        self.enum_items = []

    def _render_class(self):
        return 'class ' if self.enum_class else ''

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
        final_prefix = self.prefix if self.prefix is not None else 'e'
        with cpp.block(f'enum {self._render_class()}{self.name}', postfix=';'):
            for item in self.enum_items:
                cpp(f'{final_prefix}{item} = {counter},')
                counter += 1
            if self.add_counter in [None, True]:
                last_element = f'{final_prefix}{self.name}Count = {counter}'
                cpp(last_element)
