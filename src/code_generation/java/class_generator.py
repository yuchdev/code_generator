from code_generation.java.language_element import JavaLanguageElement


__doc__ = """"""


class JavaClass(JavaLanguageElement):
    """
    The Python class that generates string representation for Java class.
    Usually contains a number of child elements - internal classes, enums, methods and variables.
    Available properties:
    documentation - string, '/** Example Javadoc */'
    parent_class - string, the name of the parent class (if any)

    Example of usage:

    # Python code
    java_class = JavaClass(name='MyClass')
    java_class.add_variable(JavaVariable(name='myVariable', type='int', is_static=True, is_final=True, value='10'))
    java_class.add_method(JavaFunction(name='getVar', return_type='int', is_static=True, implementation='return myVariable;'))

    # Generated Java code
    public class MyClass {
        static final int myVariable = 10;

        public static int getVar() {
            return myVariable;
        }
    }
    """

    available_properties_names = {
        "documentation",
        "parent_class",
        "is_record",
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        self.documentation = None
        self.parent_class = None
        self.is_record = False

        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super().__init__(properties)
        self.init_class_properties(
            current_class_properties=self.available_properties_names,
            input_properties_dict=properties,
        )

        self.internal_class_elements = []
        self.internal_variable_elements = []
        self.internal_enum_elements = []
        self.internal_method_elements = []

    def _parent_class(self):
        return self.parent_class if self.parent_class else ""

    def _render_documentation(self, java):
        if self.documentation:
            docstring_lines = ["/**"]
            docstring_lines.extend(
                [f" * {line}" for line in self.documentation.splitlines()]
            )
            docstring_lines.append(" */")
            for line in docstring_lines:
                java(line)

    def _render_class_type(self):
        return "class" if not self.is_record else "record"

    def inherits(self):
        return f"extends {self._parent_class()}" if self.parent_class else ""

    def class_interface(self, java):
        self._render_internal_classes_declaration(java)
        self._render_enum_section(java)
        self._render_methods_declaration(java)

    def _render_internal_classes_declaration(self, java):
        for class_item in self.internal_class_elements:
            class_item.declaration().render_to_string(java)
            java.newline()

    def _render_enum_section(self, java):
        for enum_item in self.internal_enum_elements:
            enum_item.render_to_string(java)
            java.newline()

    def _render_variables_declaration(self, java):
        for var_item in self.internal_variable_elements:
            var_item.render_to_string(java)
            java.newline()

    def _render_methods_declaration(self, java):
        for method_item in self.internal_method_elements:
            method_item.render_to_string(java)
            java.newline()

    def private_class_members(self, java):
        self._render_variables_declaration(java)

    def add_variable(self, java_variable):
        java_variable.ref_to_parent = self
        self.internal_variable_elements.append(java_variable)

    def add_method(self, java_method):
        java_method.ref_to_parent = self
        self.internal_method_elements.append(java_method)

    def add_internal_class(self, java_class):
        java_class.ref_to_parent = self
        self.internal_class_elements.append(java_class)

    def render_to_string(self, java):
        self._render_documentation(java)
        with java.block(
            f"public {self._render_class_type()} {self.name} {self.inherits()}"
        ):
            self.class_interface(java)
            self.private_class_members(java)
