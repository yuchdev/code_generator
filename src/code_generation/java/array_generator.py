from code_generation.java.language_element import JavaLanguageElement

__doc__ = """"""


class JavaArray(JavaLanguageElement):

    available_properties_names = {
        'name',
        'values',
        'is_class_member',
        'add_counter'
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        """
        :param properties:
        """
        self.name = ''
        self.values = []
        self.is_class_member = False
        self.add_counter = True
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(JavaArray, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.available_properties_names,
                                   input_properties_dict=properties)

    def _sanity_check(self):
        if not self.name:
            raise RuntimeError('Enum name is not set')
        if not isinstance(self.name, str):
            raise RuntimeError(f'Enum name is not a string, but {type(self.name)}')
        if self.values is not None and not isinstance(self.values, list):
            raise RuntimeError(f'Enum values are not a list, but {type(self.values)}')

    def values_str(self):
        if self.values is None or not self.values:
            return ''
        return ', '.join(str(value) for value in self.values)

    def __str__(self):
        return self.values_str()

    def add_item(self, item):
        """
        Add a single item to the enum
        :param item: The item to add
        """
        self.values.append(item)

    def add_items(self, items):
        """
        Add multiple items to the enum
        :param items: The items to add as a list
        """
        self.values.extend(items)

    def render_to_string(self, java):
        self._sanity_check()
        with java.block(f'enum {self.name}', postfix=';'):
            counter = 0
            for value in self.values:
                java(f'{value} = {counter},')
                counter += 1
            if self.add_counter:
                last_element = f'{self.name}Count = {counter}'
                java(last_element)
