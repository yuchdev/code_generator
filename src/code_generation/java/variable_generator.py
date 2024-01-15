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
    value - string, initialization value to be assigned
    documentation - string, '/** Example Javadoc */'
    """

    available_properties_names = {
        "type",
        "name",
        "value",
        "access_modifier",
        "is_static",
        "static",
        "is_final",
        "final",
        "documentation",
        "is_transient",
        "transient",
        "is_volatile",
        "volatile",
        "is_synthetic",
        "synthetic",
        "custom_annotations",
        "custom_modifiers",
        "is_class_member",
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        self.type = ""
        self.name = ""
        self.value = ""
        self.is_static = False
        self.is_final = False
        self.is_volatile = False
        self.is_transient = False
        self.is_synthetic = False
        self.custom_annotations = []
        self.custom_modifiers = []
        self.access_modifier = None
        self.documentation = ""

        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super().__init__(properties)
        self.init_class_properties(
            current_class_properties=self.available_properties_names,
            input_properties_dict=properties,
        )

        # strip documentation of /** and */ because it's added in _render_documentation
        self.documentation = self.documentation.strip("/**").strip("*/")

    def _sanity_check(self):
        # Basic checks
        if not self.name:
            raise ValueError("Variable name is not set")
        if not self.type:
            raise ValueError("Variable type is not set")

        # Check for incompatible modifiers
        if self.is_static and self.is_transient:
            raise ValueError("Cannot use 'static' and 'transient' modifiers together")
        if self.is_static and self.is_final:
            raise ValueError("Cannot use 'static' and 'final' modifiers together")
        if self.is_static and self.is_synthetic:
            raise ValueError("Cannot use 'static' and 'synthetic' modifiers together")
        if self.is_final and self.is_volatile:
            raise ValueError("Cannot use 'final' and 'volatile' modifiers together")

        # Check for valid access modifiers
        valid_access_modifiers = ["public", "protected", "private", "", None]
        if self.access_modifier not in valid_access_modifiers:
            raise ValueError(f"Invalid access modifier: {self.access_modifier}")

    def _render_type(self):
        return f"{self.type} "

    def _render_value(self):
        return f" = {self.value}" if self.value else ""

    def _render_static(self):
        return "static " if self.is_static else ""

    def _render_final(self):
        return "final " if self.is_final else ""

    def _render_volatile(self):
        return "volatile " if self.is_volatile else ""

    def _render_transient(self):
        return "transient " if self.is_transient else ""

    def _render_synthetic(self):
        return "synthetic " if self.is_synthetic else ""

    def _render_documentation(self):
        return f"/**\n{self.documentation}\n*/" if self.documentation else ""

    def _render_access_modifier(self):
        return self.access_modifier if self.access_modifier is not None else ""

    def _render_modifiers(self):
        modifiers = [
            self._render_static(),
            self._render_final(),
            self._render_volatile(),
            self._render_transient(),
            self._render_synthetic(),
        ]
        return " ".join(modifier for modifier in modifiers if modifier)

    def _render_custom_annotations(self):
        return " ".join(self.custom_annotations) if self.custom_annotations else ""

    def _render_custom_modifiers(self):
        return " ".join(self.custom_modifiers) if self.custom_modifiers else ""

    def render_to_string(self, java):
        self._sanity_check()
        java(
            f"{self._render_custom_annotations()}"
            f"{self._render_custom_modifiers()}"
            f"{self._render_documentation()}"
            f"{self._render_modifiers()}"
            f"{self._render_type()}"
            f"{self.name}"
            f"{self._render_value()};"
        )
