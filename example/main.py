from nicegui_router import Server
from pathlib import Path

# Initialize the router with the directory containing your route files
server = Server(
    title="Example Server", 
    version="0.0.1",
    routes_dir=Path(__file__).parent / "routes",
    ui={
        "title": "Example Server",
        "storage_secret": "THIS_IS_A_SUPER_SECRET_KEY", 
        "prod_js": True,
    },
)

# Run the NiceGUI application with FastAPI
app = server.app

if __name__ == "__main__":
    server.listen(port=3000)