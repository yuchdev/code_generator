from code_generation.cpp.language_element import CppLanguageElement


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

    NOTE: methods responsible for rendering of any element to string start from 'render_*'
    (e.g. render_value, render_to_string)
    Methods simply returning string representation of the element start from '_'
    """

    availablePropertiesNames = (
            {
                "prefix",
                "enum_class",
                "add_counter",
                "enum_items"
            } | CppLanguageElement.availablePropertiesNames)

    def __init__(self, **properties):
        """
        :param properties:
        """
        self.enum_class = False
        self.enum_items = []
        self.prefix = None
        self.add_counter = True

        # check properties
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(CppEnum, self).__init__(properties)

        self.init_class_properties(
            current_class_properties=self.availablePropertiesNames,
            input_properties_dict=properties,
        )

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
        final_prefix = self.prefix if self.prefix is not None else "e"
        with cpp.block(f"enum {self._enum_class()}{self.name}", postfix=";"):
            for item in self.enum_items:
                cpp(f"{final_prefix}{item} = {counter},")
                counter += 1
            if self.add_counter in [None, True]:
                last_element = f"{final_prefix}{self.name}Count = {counter}"
                cpp(last_element)

    def _enum_class(self):
        return "class " if self.enum_class else ""
