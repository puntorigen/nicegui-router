# Simplifying Web Development with NiceGUI-Router: A Modern Approach to FastAPI and NiceGUI Integration

## Introduction

Building modern web applications requires a delicate balance between functionality, maintainability, and developer experience. While FastAPI and NiceGUI are powerful tools individually, combining them effectively can be challenging. Enter NiceGUI-Router: a game-changing package that brings file-based routing, React-like state management, and seamless FastAPI integration to your NiceGUI applications.

## Why NiceGUI-Router?

NiceGUI-Router revolutionizes Python web development by bringing modern web development patterns to the FastAPI and NiceGUI ecosystem:

1. **File-Based Routing**: 
   - Organize your application logically with a file structure that directly maps to your URL routes
   - Automatic route inference based on file names and directory structure
   - Support for nested routes and dynamic parameters

2. **React-like State Management**: 
   - Manage UI state effortlessly with familiar React-inspired hooks
   - Reactive components that automatically update when state changes
   - Encapsulated component state for better code organization

3. **FastAPI Integration**: 
   - Seamless integration with FastAPI's powerful features
   - Full support for dependency injection and path parameters
   - Automatic OpenAPI documentation generation

4. **Theme Management**: 
   - Comprehensive theming system with support for custom colors and fonts
   - Global and per-page theme configuration
   - CSS customization and external resource integration

5. **Authentication & Security**:
   - Built-in authentication decorators for both pages and API endpoints
   - Secure token-based authentication
   - Route protection with automatic redirect to login

## Getting Started

First, install nicegui-router using pip:

```bash
pip install nicegui-router
```

### Project Structure

Create a modern web application with this intuitive structure:

```
my_app/
├── main.py                 # Server configuration and startup
├── requirements.txt        # Project dependencies
└── routes/                # All your application routes
    ├── __init__.py
    ├── index.py          # Home page (/)
    ├── about.py          # About page (/about)
    ├── blog/             # Blog section (/blog/*)
    │   ├── __init__.py
    │   ├── index.py     # Blog listing (/blog)
    │   └── [id].py      # Individual blog post (/blog/123)
    └── api/              # API endpoints
        ├── __init__.py
        └── items.py      # REST API endpoints (/api/items)
```

### Server Configuration

In `main.py`, initialize your application:

```python
from nicegui_router import Server
from pathlib import Path

server = Server(
    title="My Modern App",           # OpenAPI title
    version="1.0.0",                 # API version
    routes_dir=Path(__file__).parent / "routes",
    ui={
        "title": "My Application",
        "favicon": "path/to/favicon.ico",  # Optional
        "storage_secret": "YOUR_SECRET_KEY",
    },
    # Optional startup/shutdown handlers
    on_startup=lambda: print("Server starting..."),
    on_shutdown=lambda: print("Server shutting down..."),
)

if __name__ == "__main__":
    server.listen(port=3000)
```

## Creating Pages with File-Based Routing

### Home Page (routes/index.py)

Create a welcoming home page with navigation:

```python
from nicegui_router import page, ui, theme

# Define a custom theme for this page
home_theme = theme({
    'primary': '#2196F3',
    'secondary': '#FFC107',
    'accent': '#E91E63'
}, font="Roboto")

@page("/", theme=home_theme)
def home():
    with ui.header().classes('flex justify-between items-center p-4'):
        ui.label("Welcome!").classes('text-2xl font-bold')
        with ui.row().classes('gap-4'):
            ui.link("About", "/about").classes('text-white')
            ui.link("Blog", "/blog").classes('text-white')
    
    with ui.column().classes('p-4 gap-4'):
        ui.markdown("""
        # Welcome to My App
        
        This is a modern web application built with NiceGUI-Router.
        Explore our features and enjoy the seamless experience!
        """)
        
        with ui.row().classes('gap-4'):
            ui.button("Get Started", on_click=lambda: ui.navigate.to("/about"))
            ui.button("View Demo", on_click=lambda: ui.navigate.to("/demo"))
```

### Dynamic Blog Post Page (routes/blog/[id].py)

Demonstrate dynamic routing with path parameters:

```python
from nicegui_router import page, ui
from typing import Optional

@page("/blog/{post_id}")
def blog_post(post_id: str):
    with ui.column().classes('p-4 gap-4'):
        ui.label(f"Blog Post {post_id}").classes('text-2xl font-bold')
        ui.markdown(f"This is the content of blog post {post_id}")
        ui.button("Back to Blog", on_click=lambda: ui.navigate.to("/blog"))
```

## State Management with React-like Hooks

Create reactive components with encapsulated state:

```python
from nicegui_router import page, ui, component, use_state, theme

@page("/demo")
def demo():
    @component
    def Counter():
        # Initialize state with use_state hook
        count, set_count = use_state(0)
        
        with ui.card().classes('p-4'):
            ui.label(f"Count: {count}").classes('text-xl')
            with ui.row().classes('gap-2'):
                ui.button("Increment", on_click=lambda: set_count(count + 1))
                ui.button("Reset", on_click=lambda: set_count(0))
    
    @component
    def TodoList():
        todos, set_todos = use_state([])
        new_todo, set_new_todo = use_state("")
        
        def add_todo():
            if new_todo:
                set_todos([*todos, new_todo])
                set_new_todo("")
        
        with ui.card().classes('p-4'):
            ui.label("Todo List").classes('text-xl mb-4')
            with ui.row().classes('gap-2'):
                ui.input(value=new_todo, on_change=lambda e: set_new_todo(e.value))
                ui.button("Add", on_click=add_todo)
            
            with ui.column().classes('gap-2 mt-4'):
                for todo in todos:
                    ui.label(todo)
    
    with ui.column().classes('p-4 gap-4'):
        ui.label("State Management Demo").classes('text-2xl font-bold')
        Counter()
        TodoList()
```

## API Integration with FastAPI

NiceGUI-Router seamlessly integrates with FastAPI's routing system:

```python
from nicegui_router import get, post, put, delete
from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Awesome Item",
                "description": "This is a fantastic item",
                "price": 29.99
            }
        }

items_db = []  # Simple in-memory storage

@get("/api/items", output=List[Item])
def get_items():
    """
    Retrieve all items from the database.
    """
    return items_db

@post("/api/items", input=Item, output=Item)
def create_item(item: Item):
    """
    Create a new item in the database.
    """
    item.id = len(items_db) + 1
    items_db.append(item)
    return item

@put("/api/items/{item_id}", input=Item, output=Item)
def update_item(item_id: int, item: Item):
    """
    Update an existing item by ID.
    """
    if 0 <= item_id - 1 < len(items_db):
        item.id = item_id
        items_db[item_id - 1] = item
        return item
    raise HTTPException(status_code=404, detail="Item not found")
```

## Authentication and Protected Routes

Implement secure authentication with built-in decorators:

```python
from nicegui_router import page_auth, get_auth, post_auth, create_access_token
from pydantic import BaseModel

class LoginData(BaseModel):
    username: str
    password: str

@post("/api/login")
def login(data: LoginData):
    # Validate credentials (replace with your auth logic)
    if data.username == "admin" and data.password == "secret":
        # Create and return JWT token
        token = create_access_token({"sub": data.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@page_auth("/dashboard")
def dashboard():
    """This page is only accessible to authenticated users."""
    with ui.column().classes('p-4 gap-4'):
        ui.label("Welcome to Dashboard").classes('text-2xl font-bold')
        ui.label("This is a protected page")

@get_auth("/api/protected")
def protected_data():
    """This endpoint requires authentication."""
    return {"message": "This is protected data"}
```

## Theme Management

Create beautiful, consistent UI with the theme system:

```python
from nicegui_router import theme, page, ui

# Create a modern theme with custom colors and font
modern_theme = theme(
    {
        'primary': '#1976D2',    # Material Blue
        'secondary': '#26A69A',  # Material Teal
        'accent': '#9C27B0',    # Material Purple
        'dark': '#121212',      # Dark background
        'positive': '#21BA45',  # Success green
        'negative': '#C10015',  # Error red
        'info': '#31CCEC',     # Info blue
        'warning': '#F2C037'   # Warning yellow
    },
    font="Inter",  # Modern sans-serif font
    # Add custom CSS
    css=[
        "body { font-family: 'Inter', sans-serif; }",
        ".custom-shadow { box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }"
    ],
    # Add external resources
    head=[
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">',
    ]
)

@page("/styled", theme=modern_theme)
def styled_page():
    with ui.column().classes('p-4 gap-4'):
        ui.label("Styled Page").classes('text-2xl font-bold')
        
        with ui.card().classes('custom-shadow p-4'):
            ui.label("This card uses our custom theme!")
            ui.button("Themed Button", on_click=lambda: ui.notify("Clicked!"))
```

## Documentation Generation

NiceGUI-Router automatically generates OpenAPI documentation for your API endpoints. Access the interactive documentation at:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

The documentation includes:
- Endpoint descriptions and parameters
- Request/response schemas
- Authentication requirements
- Example requests and responses

## Conclusion

NiceGUI-Router brings the best of modern web development practices to the Python ecosystem. By combining the simplicity of file-based routing, the power of React-like state management, and the robustness of FastAPI, it provides an excellent foundation for building modern web applications.

Key benefits:
- 🚀 Rapid development with intuitive APIs
- 📁 Organized codebase with file-based routing
- 💻 Modern state management with React-like hooks
- 🎨 Beautiful UI with comprehensive theming
- 🔒 Built-in security features
- 📚 Automatic API documentation

Whether you're building a small dashboard or a complex web application, NiceGUI-Router's intuitive API and powerful features will help you create maintainable and scalable applications with ease.

Ready to get started? Visit our GitHub repository for more examples and detailed documentation. Join our growing community of developers who are already using NiceGUI-Router to build amazing web applications!
