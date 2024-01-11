from code_generation.java.language_element import JavaLanguageElement


__doc__ = """"""


class JavaFunction(JavaLanguageElement):

    available_properties_names = {
        'name',
        'return_type',
        'arguments',
        'is_static',
        'is_final',
        'is_abstract',
        'is_synchronized',
        'is_native',
        'is_strictfp',
        'access_specifier',
        'documentation',
        'implementation'
    } | JavaLanguageElement.available_properties_names

    def __init__(self, **properties):
        self.name = ''
        self.return_type = ''
        self.arguments = []
        self.is_static = False
        self.is_final = False
        self.is_abstract = False
        self.is_synchronized = False
        self.is_native = False
        self.is_strictfp = False
        self.documentation = ''
        self.access_specifier = 'public'
        self.implementation = None
        input_property_names = set(properties.keys())
        self.check_input_properties_names(input_property_names)
        super(JavaFunction, self).__init__(properties)
        self.init_class_properties(current_class_properties=self.available_properties_names,
                                   input_properties_dict=properties)

    def _sanity_check(self):
        if not self.name:
            raise RuntimeError('Method name is not set')
        if not isinstance(self.name, str):
            raise RuntimeError(f'Method name is not a string, but {type(self.name)}')
        if not isinstance(self.return_type, str):
            raise RuntimeError(f'Return type is not a string, but {type(self.return_type)}')
        if self.arguments is not None and not isinstance(self.arguments, list):
            raise RuntimeError(f'Arguments are not a list, but {type(self.arguments)}')

    def args_str(self):
        if self.arguments is None or not self.arguments:
            return ''
        return ', '.join(str(arg) for arg in self.arguments)

    def add_argument(self, argument):
        """
        Add an argument to the method
        :param argument: The argument to add
        """
        self.arguments.append(argument)

    def render_to_string(self, java):
        self._sanity_check()
        if self.documentation:
            java(f"/**\n{self.documentation}\n*/")
        if self.is_abstract:
            raise RuntimeError("Cannot generate implementation for abstract method.")
        if self.is_static:
            java('static', end=' ')
        if self.is_final:
            java('final', end=' ')
        if self.is_synchronized:
            java('synchronized', end=' ')
        if self.is_native:
            java('native', end=' ')
        if self.is_strictfp:
            java('strictfp', end=' ')
        with java.block(f'{self.access_specifier} {self.return_type} {self.name}({self.args_str()})'):
            if self.implementation:
                self.implementation(java)
