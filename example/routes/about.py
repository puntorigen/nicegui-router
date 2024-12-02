from nicegui_router import page, theme, ui

customTheme = theme(
    {
        'primary': '#FF5733', # orange
        'secondary': '#33FF57', # green
        'accent': '#3357FF'
    }, font="Lato")

@page(theme=customTheme)
def about():
    ui.markdown("**About Us Page** themed with custom fonts and colors.")
    ui.button("Click Me!").on("click", lambda: ui.notify("Hello!"))