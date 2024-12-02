from nicegui_router import page, ui, theme, component, use_state

customTheme = theme(
    {
        'primary': '#FF5733', # orange
        'secondary': '#33FF57', # green
        'accent': '#3357FF'
    }, font="Lato")

@page(theme=customTheme)
def counter():
    @component
    def customCounter():
        count, setCount = use_state(0)
        return ui.button(f"Count: {count}").on("click", lambda: setCount(count + 1))

    with ui.header():
        title = ui.label("Example 2")
        ui.space()
        customCounter()
    ui.markdown("Custom component with state reactivity.")