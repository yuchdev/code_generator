class HtmlElement:
    availablePropertiesNames = {'name', 'attributes', 'self_closing'}

    def __init__(self, **properties):
        """
        :param properties: Basic HTML element properties (name, self-closing, attributes)
        """
        self.name = properties.get('name')
        self.self_closing = properties.get('self_closing', False)
        self.attributes = properties.get('attributes', {})

        # If 'attributes' is present, set it to self.attributes and remove it from properties
        if 'attributes' in properties:
            self.attributes = properties['attributes']
            properties.pop('attributes')

        # Populate self.attributes with any remaining properties not already set
        for key, value in properties.items():
            if key not in ('name', 'self_closing'):
                self.attributes[key] = value

    def render_to_string(self, html, content=None):
        """
        Generates HTML code for the self-closing element
        """
        if self.self_closing:
            html('<{0} {1}/>'.format(self.name, ' '.join(self._render_attributes())))
        elif content is not None:
            with html.block(element=self.name, **self.attributes):
                html(content)

    def _render_attributes(self):
        """
        Renders attributes to string
        """
        rendered_attributes = ' '.join('{0}="{1}"'.format(key, value) for key, value in self.attributes.items())
        return f' {rendered_attributes}' if len(self.attributes) else ''
