from code_generation.java.language_element import JavaLanguageElement


__doc__ = """"""


class JavaVariable(JavaLanguageElement):
    """
    The Python class that generates string representation for Java variable
    For example:
    class MyClass {
        int var1;
        double var2;
        ...
    }

    Available properties:
    type - string, variable type
    is_static - boolean, 'static' prefix
    is_final - boolean, 'final' prefix
    initialization_value - string, initialization value to be assigned
    documentation - string, '/** Example Javadoc */'
    """

    available_properties_names = {
        'type',
        'is_static',
        'is_final',
        'initialization_value',
        'documentation'
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        self.type = ''
        self.is_static = False
        self.is_final = False
        self.initialization_value = ''
        self.documentation = ''

        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super().__init__(properties)
        self.init_class_properties(
            current_class_properties=self.available_properties_names,
            input_properties_dict=properties
        )

    def render_to_string(self, java):
        if self.documentation:
            java(f"/**\n{self.documentation}\n*/")
        java(f"{self._render_static()}{self._render_final()}{self.type} {self.name};")

    def render_to_string_declaration(self, java):
        if self.documentation:
            java(f"/**\n{self.documentation}\n*/")
        java(f"{self._render_static()}{self._render_final()}{self.type} {self.name};")

    def render_to_string_implementation(self, java):
        if self.is_static:
            java(f"{self._render_static()}final {self.type} {self.name} = {self.initialization_value};")

    def _render_static(self):
        return "static " if self.is_static else ""

    def _render_final(self):
        return "final " if self.is_final else ""
