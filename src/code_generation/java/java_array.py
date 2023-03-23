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
        if self.is_class_member and not self.name:
            raise RuntimeError('Class member array name is not set')
        if self.array_size and self.dynamic:
            raise RuntimeError('Array size is defined and array is dynamic')
        if self.array_size and self.items:
            raise RuntimeError('Array size is defined and array has items')

    def _render_static(self, java):
        if self.items is None or not self.items:
            values_str = ', '.join(f'{self.type}()' for _ in range(self.array_size))
        else:
            values_str = ', '.join(str(item) for item in self.items)
        java(f"{self.type}[] {self.name} = {{ {values_str} }};")

    def _render_dynamic(self, java):
        if self.items is None or not self.items:
            values_str = ', '.join(f'{self.type}()' for _ in range(self.array_size))
        else:
            values_str = ', '.join(str(item) for item in self.items)

        java(f"{self.type}[] {self.name} = new {self.type}[{len(self.items)}]{{ {values_str} }};")

    def render_to_string(self, java):
        self._sanity_check()
        if self.dynamic:
            self._render_dynamic(java)
        else:
            self._render_static(java)
