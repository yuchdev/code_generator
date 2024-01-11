from code_generation.java.language_element import JavaLanguageElement

__doc__ = """"""


class JavaFunction(JavaLanguageElement):
    available_properties_names = {
        "name",
        "return_type",
        "arguments",
        "is_static",
        "is_final",
        "is_abstract",
        "is_synchronized",
        "is_native",
        "is_strictfp",
        "access_specifier",
        "documentation",
        "implementation",
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        self.name = ""
        self.return_type = ""
        self.arguments = []
        self.is_static = False
        self.is_final = False
        self.is_abstract = False
        self.is_synchronized = False
        self.is_native = False
        self.is_strictfp = False
        self.documentation = ""
        self.access_specifier = "public"
        self.implementation = None
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(JavaFunction, self).__init__(properties)
        self.init_class_properties(
            current_class_properties=self.available_properties_names,
            input_properties_dict=properties,
        )

    def _sanity_check(self):
        if not self.name:
            raise RuntimeError("Method name is not set")
        if not isinstance(self.name, str):
            raise RuntimeError(f"Method name is not a string, but {type(self.name)}")
        if not isinstance(self.return_type, str):
            raise RuntimeError(
                f"Return type is not a string, but {type(self.return_type)}"
            )
        if self.arguments is not None and not isinstance(self.arguments, list):
            raise RuntimeError(f"Arguments are not a list, but {type(self.arguments)}")

    def args_str(self):
        if self.arguments is None or not self.arguments:
            return ""
        return ", ".join(str(arg) for arg in self.arguments)

    def add_argument(self, argument):
        """
        Add an argument to the method
        :param argument: The argument to add
        """
        self.arguments.append(argument)

    def _render_documentation(self, java):
        if self.documentation:
            docstring_lines = ["/**"]
            docstring_lines.extend(
                [f" * {line}" for line in self.documentation.splitlines()]
            )
            docstring_lines.append(" */")
            for line in docstring_lines:
                java(line)

    def _render_access_specifier(self):
        return self.access_specifier if self.access_specifier else ""

    def _render_static(self):
        return "static" if self.is_static else ""

    def _render_final(self):
        return "final" if self.is_final else ""

    def _render_synchronized(self):
        return "synchronized" if self.is_synchronized else ""

    def _render_native(self):
        return "native" if self.is_native else ""

    def _render_strictfp(self):
        return "strictfp" if self.is_strictfp else ""

    def _render_modifiers(self):
        modifiers = [
            self._render_access_specifier(),
            self._render_static(),
            self._render_final(),
            self._render_synchronized(),
            self._render_native(),
            self._render_strictfp(),
        ]
        return " ".join(modifier for modifier in modifiers if modifier)

    def render_to_string(self, java):
        self._sanity_check()
        self._render_documentation(java)
        with java.block(
            f"{self._render_modifiers()} {self.return_type} {self.name}({self.args_str()})"
        ):
            if self.implementation is not None:
                self.implementation(java)
