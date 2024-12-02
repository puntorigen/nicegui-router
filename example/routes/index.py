from nicegui_router import page, ui

@page("/")
def home():
    ui.markdown("Welcome to the Home Page!")