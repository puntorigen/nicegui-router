from nicegui_router import page, ui

@page("/")
def home():
    ui.markdown("Welcome to the Home Page!")
    
    def item(title, url):
        # open page on click
        return ui.item(title, on_click=lambda: ui.navigate.to(url))

    with ui.list().props('dense separator'):
        item("About", "/about")
        item("Counter Example", "/counter")