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

    available_properties_names = (
            {
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
            } | JavaLanguageElement.available_properties_names)

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

    def render_custom_annotations(self, java):
        if self.custom_annotations:
            for annotation in self.custom_annotations:
                java(f"@{annotation}")

    def render_custom_modifiers(self, java):
        if self.custom_modifiers:
            for modifier in self.custom_modifiers:
                java(f"{modifier} ")

    def render_documentation(self, java):
        if self.documentation:
            java("/**")
            java(f" * {self.documentation}")
            java(" */")

    def render_to_string(self, java):
        self._sanity_check()
        self.render_custom_annotations(java)
        self.render_custom_modifiers(java)
        self.render_documentation(java)
        java(
            f"{self._modifiers()}"
            f"{self._type()}"
            f"{self.name}"
            f"{self._value()};"
        )

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

    def _type(self):
        return f"{self.type} "

    def _value(self):
        return f" = {self.value}" if self.value else ""

    def _static(self):
        return "static " if self.is_static else ""

    def _final(self):
        return "final " if self.is_final else ""

    def _volatile(self):
        return "volatile " if self.is_volatile else ""

    def _transient(self):
        return "transient " if self.is_transient else ""

    def _synthetic(self):
        return "synthetic " if self.is_synthetic else ""

    def _access_modifier(self):
        return self.access_modifier if self.access_modifier is not None else ""

    def _modifiers(self):
        modifiers = [
            self._static(),
            self._final(),
            self._volatile(),
            self._transient(),
            self._synthetic(),
        ]
        # leave only non-empty elements
        modifiers = [mod for mod in modifiers if mod]
        return " ".join(modifier for modifier in modifiers if modifier)
