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
    ├── __init__.py
    ├── home.py
    └── about.py
```

### Example Code

#### `main.py`
```python
from nicegui_router import Server

# Initialize the router with the directory containing your route files
server = Server(title='Example Server', routes_dir='routes')

# Get the Fastapi app instance (for advanced use cases)
app = server.app

# Start the server if the script is run directly
if __name__ == '__main__':
    server.listen(host='0.0.0.0', port=8080)
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
from nicegui_router import page, ui, ThemeBuild

@page(theme=ThemeBuild(theme={'primary': '#FF5733', 'secondary': '#33FF57', 'accent': '#3357FF'}))
def about():
    ui.markdown("About Us Page themed with custom colors.")
```

### Starting the Server
To start the server, simply run the following command in your terminal from the project's root directory:
```bash
python example/main.py
```

Navigate to `http://localhost:8080` to see your NiceGUI application in action.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.