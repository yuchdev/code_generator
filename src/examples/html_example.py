from code_generation.html.html_file import HtmlFile
from code_generation.html.html_element import HtmlElement

__doc__ = """Example of generating HTML file

Expected output example.html:

<html>
    <head lang="en">
        <meta charset="utf-8" />
    </head>
</html>

Expected output example2.html:

<html>
    <head lang="en">
        <meta charset="utf-8" />
        <meta viewport="width=device-width, initial-scale=1" />
    </head>
    <body>
        <div id="container">
            <div id="header">
                Header
            </div>
            <div id="content">
                Content
            </div>
        </div>
        <div>
        </div>
        <footer id="real-footer">
            Footer 2
        </footer>
    </body>
"""

html = HtmlFile("example.html")
with html.block("html"):
    with html.block("head", lang="en"):
        html('<meta charset="utf-8" />')

html = HtmlFile("example2.html")
with html.block("html"):
    with html.block("head", lang="en"):
        HtmlElement(
            name="meta", self_closing=True, charset="utf-8"
        ).render_to_string(html)
        HtmlElement(
            name="meta",
            self_closing=True,
            viewport="width=device-width, initial-scale=1",
        ).render_to_string(html)
    with html.block("body"):
        # with semantic
        with html.block("div", id="container"):
            with html.block("div", id="header"):
                html("Header")
            with html.block("div", id="content"):
                html("Content")
        # using content parameter
        HtmlElement(name="div", self_closing=False).render_to_string(
            html, content="Footer 1"
        )
        HtmlElement(
            name="footer", self_closing=False, id="real-footer"
        ).render_to_string(html, content="Footer 2")
