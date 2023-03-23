from code_generation.core.code_file import CodeFile

__doc__ = """"""


from code_generation.java.language_element import JavaLanguageElement


class JavaArray(JavaLanguageElement):

    available_properties_names = {
        'type',
        'array_size',
        'is_const',
        'const',
        'is_class_member',
        'is_dynamic',
        'dynamic',
        'items'
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        """
        :param properties:
        """
        self.type = ''
        self.is_const = False
        self.is_class_member = False
        self.dynamic = False
        self.array_size = 0
        self.items = []
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(JavaArray, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.available_properties_names,
                                   input_properties_dict=properties)

    def _sanity_check(self):
        """
        Check if all required properties are set
        """
        if not self.type:
            raise RuntimeError('Array type is not set')
        if not isinstance(self.type, str):
            raise RuntimeError(f'Array type is not a string, but {type(self.type)}')
        if self.array_size is not None and not isinstance(self.array_size, int):
            raise RuntimeError(f'Array size is not an integer, but {type(self.array_size)}')
        if self.items is not None and not isinstance(self.items, list):
            raise RuntimeError(f'Array items are not a list, but {type(self.items)}')
        if self.is_class_member and not self.name:
            raise RuntimeError('Class member array name is not set')
        if self.array_size and self.items:
            raise RuntimeError('Array size is defined and array has items')
        if self.array_size and not self.dynamic:
            raise RuntimeError('Array size is defined but array is not dynamic')

    def values_str(self):
        """
        String representation of array items
        {1, 2, 3}
        Can be used for multidimensional arrays as well
        {{1, 2, 3}, {4, 5, 6}}
        """
        if self.items is None or not self.items:
            return ''
        return f"{{ {', '.join(str(item) for item in self.items)} }}"

    def __str__(self):
        """
        String representation of array
        """
        return self.values_str()

    def _render_static(self, java):
        """
        Render arrays without 'new' keyword
        int[] anArray;
        int[] arrayWithItems = {1, 2, 3};
        """
        if self.items is None or not self.items:
            java(f"{self.type}[] {self.name};")
        else:
            java(f"{self.type}[] {self.name} = {self.values_str()};")

    def _render_dynamic(self, java):
        """
        Render arrays with 'new' keyword
        """
        java(f"{self.type}[] {self.name} = new {self.type}[{self.array_size}];")

    def render_to_string(self, java):
        self._sanity_check()
        if self.dynamic:
            self._render_dynamic(java)
        else:
            self._render_static(java)
