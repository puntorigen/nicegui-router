from contextlib import contextmanager
from typing import TypedDict, Dict
from nicegui import ui

class ColorScheme(TypedDict):
    primary: str
    secondary: str
    accent: str
    dark: str
    positive: str
    negative: str
    info: str
    warning: str

class ThemeBuild:
    def __init__(
            self, 
            theme: ColorScheme, 
            font:str = None, 
            css: list[str] = [], 
            head: list[str] = [],
            body: list[str] = [],
            body_close: list[str] = [],
        ) -> None: 
        self.theme = theme
        self.css = css
        self.head = head
        self.font = font
        self.body = body
        self.body_close = body_close
        pass

    @contextmanager
    def build(self):
        # disable autofill background
        ui.add_css('''
            input:-webkit-autofill {
                -webkit-box-shadow: 0 0 0 1000px white inset !important;
                box-shadow: 0 0 0 1000px white inset !important;
                -webkit-text-fill-color: black !important;
            }
        ''')
        # Add AOS animations support
        ui.add_head_html('<link href="https://cdn.jsdelivr.net/npm/aos@2.3.1/dist/aos.css" rel="stylesheet">')
        ui.add_body_html('<script src="https://cdn.jsdelivr.net/npm/aos@2.3.1/dist/aos.js"></script>')
        # add custom css
        for css in self.css:
            ui.add_css(css)
        # add custom html tags (e.g. fonts, etc)
        for head in self.head:
            ui.add_head_html(head)
        for body in self.body:
            ui.add_body_html(body)
        # add font face as head html from google
        if self.font:
            ui.add_head_html(f'<link href="https://fonts.googleapis.com/css2?family={self.font}" rel="stylesheet">')
            ui.add_head_html(f'''
                <style>
                    body {{
                        font-family: '{self.font}', sans-serif;
                    }}
                </style>
            ''')
        # assign theme colors
        ui.colors(**self.theme)
        yield
        # add tags near the end of body
        for body_close in self.body_close:
            ui.add_body_html(body_close)
        # add AOS script
        ui.run_javascript('AOS.init();')

def theme(
        theme: ColorScheme, 
        font:str = None, 
        css: list[str] = [], 
        head: list[str] = [],
        body: list[str] = [],
        body_close: list[str] = [],
        name: str = "CustomTheme"
    ):
    """Dynamically generates a theme class.

    Args:
        theme (dict): The theme dictionary to be used.
        font (str): The font to be used.
        css (list[str]): CSS rules to apply.
        head (list[str]): Additional HTML elements for the head section.
        body (list[str]): Additional HTML elements for the body section.
        body_close (list[str]): Additional HTML elements before the body closing tag.
        name (str): The name for the generated class.

    Returns:
        type: A dynamically generated class extending ThemeBuild.
    """
    class GeneratedTheme(ThemeBuild):
        def __init__(self) -> None:
            super().__init__(
                theme=theme,
                font=font,
                css=css,
                head=head,
                body=body,
                body_close=body_close
            )
    
    # Rename the class to the desired name
    #GeneratedTheme.__name__ = "CustomTheme"
    return GeneratedTheme