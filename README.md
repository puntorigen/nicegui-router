# nicegui-router

File-based routing and theming for NiceGUI, bringing structured navigation and consistent page themes.

## Features
- **File-Based Routing**: Automatically organize your application routes using a file-based structure, making navigation in NiceGUI applications clean and scalable.
- **Theming Support**: Apply consistent UI themes across your NiceGUI application for a uniform user experience.
- **WebSocket and HTTP Route Decorators**: Easy route handling with support for WebSockets and RESTful HTTP methods.
- **JWT Authentication**: Built-in support for authenticated routes to secure your application.
- **Dynamic Route Loading**: Dynamically register routes from specified directories, streamlining development workflow.
- **Custom Error Handling**: Log and manage route errors efficiently.
- **NiceGUI Integration**: Seamlessly integrated with the NiceGUI environment for web application development.

## Usage

This package is designed to simplify the development of applications using NiceGUI by enabling file-based routing and consistent theming. Below is a demonstration of how to set up a simple application using `nicegui-router`.

### Example Project Structure

```plaintext
my_nicegui_app/
├── main.py
└── routes
    ├── home.py
    └── about.py
    └── counter.py
```

### Example Code

#### `main.py`
```python
from nicegui_router import Server
from pathlib import Path

# Initialize the router with the directory containing your route files
server = Server(
    title='Example Server', 
    routes_dir=Path(__file__).parent / "routes"
)

# Get the Fastapi app instance (for advanced use cases)
app = server.app

# Start the server if the script is run directly
if __name__ == '__main__':
    server.listen(port=8080)
```

#### `routes/index.py`
```python
from nicegui_router import page, ui

@page('/')
def home():
    ui.markdown("Welcome to the Home Page!")
```

#### `routes/about.py`
```python
from nicegui_router import page, ui, theme

customTheme = theme(
    {
        'primary': '#FF5733', # orange
        'secondary': '#33FF57', # green
        'accent': '#3357FF'
    }, font="Lato")

@page(theme=customTheme)
def about():
    ui.markdown("About Us Page themed with custom colors.")
```

#### `routes/counter.py`
```python
from nicegui_router import page, ui, theme, component, use_state

customTheme = theme(
    {
        'primary': '#FF5733', # orange
        'secondary': '#33FF57', # green
        'accent': '#3357FF'
    }, font="Lato")

@page(theme=customTheme)
def counter():
    # custom component with state reactivity support
    @component
    def customCounter():
        count, setCount = use_state(0)
        return ui.button(f"Count: {count}").on("click", lambda: setCount(count + 1))

    with ui.header():
        title = ui.label("Example 2")
        ui.space()
        customCounter()
    ui.markdown("Custom component with state reactivity.")
```

### Starting the Server
To start the server, simply run the following command in your terminal from the project's root directory:
```bash
python example/main.py
```

Navigate to `http://localhost:8080` to see your NiceGUI application in action.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.