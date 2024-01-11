from code_generation.java.language_element import JavaLanguageElement


__doc__ = """"""


class JavaEnum(JavaLanguageElement):
    available_properties_names = {
        "name",
        "values",
        "is_class_member",
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        """
        :param properties:
        """
        self.name = ""
        self.values = []
        self.is_class_member = False
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(JavaEnum, self).__init__(properties)
        self.init_class_properties(
            current_class_properties=self.available_properties_names,
            input_properties_dict=properties,
        )

    def _sanity_check(self):
        """
        Check if all required properties are set
        """
        if not self.name:
            raise RuntimeError("Enum name is not set")
        if not isinstance(self.name, str):
            raise RuntimeError(f"Enum name is not a string, but {type(self.name)}")
        if self.values is not None and not isinstance(self.values, list):
            raise RuntimeError(f"Enum values are not a list, but {type(self.values)}")
        if self.is_class_member and not self.name:
            raise RuntimeError("Class member enum name is not set")

    def values_str(self):
        """
        String representation of enum values
        Can be used for multiple values as well
        VALUE1, VALUE2, VALUE3
        """
        if self.values is None or not self.values:
            return ""
        return ", ".join(str(value) for value in self.values)

    def __str__(self):
        """
        String representation of enum
        """
        return self.values_str()

    def _render_static(self, java):
        """
        Render static enums
        """
        if self.values is None or not self.values:
            java(f"enum {self.name} {{}}")
        else:
            java(f"enum {self.name} {{ {self.values_str()} }};")

    def render_to_string(self, java):
        self._sanity_check()
        self._render_static(java)
