import importlib.util, os, hashlib, jwt
import warnings, logging
from typing import TypedDict, Optional, Union, Literal, Sequence, List, Dict, Any
from fastapi import FastAPI, APIRouter, Request, Response, WebSocket
from fastapi.routing import APIRoute, BaseRoute, APIWebSocketRoute
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
from nicegui import ui, app as nicegui_app
from nicegui.language import Language
from .route_decorator import _route_decorator, SECRET_KEY, ALGORITHM
from .logging import setup_logger
from contextlib import asynccontextmanager

from fastapi.openapi.models import (
    OAuthFlows as OAuthFlowsModel,
    SecurityScheme as SecuritySchemeModel,
)
from fastapi.openapi.models import OAuthFlowPassword as OAuthFlowPasswordModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

warnings.filterwarnings("ignore")

# Setup the logger
logger = setup_logger(__name__)
# logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define a TypedDict for NiceGUI configuration
class NiceGUIConfig(TypedDict, total=False):
    title: str
    viewport: str
    favicon: Optional[Union[str, Path]]
    dark: Optional[bool]
    language: Language
    binding_refresh_interval: float
    reconnect_timeout: float
    mount_path: str
    on_air: Optional[Union[str, Literal[True]]]
    tailwind: bool
    prod_js: bool
    storage_secret: Optional[str]
    show_welcome_message: bool

class OpenAPIArgs(TypedDict, total=False):
    title: str
    version: str
    openapi_version: str
    summary: Optional[str]
    description: Optional[str]
    routes: Sequence[BaseRoute]
    webhooks: Optional[Sequence[BaseRoute]]
    tags: Optional[List[Dict[str, Any]]]
    servers: Optional[List[Dict[str, Union[str, Any]]]]
    terms_of_service: Optional[str]
    contact: Optional[Dict[str, Union[str, Any]]]
    license_info: Optional[Dict[str, Union[str, Any]]]
    separate_input_output_schemas: bool

class DynamicRouterLoader:
    def __init__(
        self,
        routes_dir: str,
        ui: NiceGUIConfig = None,
        auth_path: str = "/login",
        static_path: Optional[str] = None,
        on_startup: Optional[callable] = None,
        on_shutdown: Optional[callable] = None,
        **fastapi_kwargs,
    ):
        # Create the lifespan events handler
        #@asynccontextmanager
        #async def lifespan_events(app: FastAPI):
        #    try:
        #        if on_startup:
        #            await on_startup()
        #        yield
        #    finally:
        #        if on_shutdown:
        #            await on_shutdown()
        # Pass the kwargs to the FastAPI instance
        self.routes_dir = routes_dir
        self.app = FastAPI(
            generate_unique_id_function=self.custom_generate_unique_id, 
            #lifespan=lifespan_events,
            **fastapi_kwargs
        )
        # set on_startup and on_shutdown on nicegui app
        if on_startup:
            nicegui_app.on_startup(on_startup)
        if on_shutdown:
            nicegui_app.on_shutdown(on_shutdown)
        if static_path:
            nicegui_app.add_static_files("/static", static_path)
        # Set the routes directory and authentication path
        _route_decorator.set_routes_dir(self.routes_dir)
        _route_decorator.set_auth_path(auth_path)

        self.nicegui_config = ui or {}
        self.error_messages = {}
        self._setup_exception_handler()
        self._setup_cors()
        self._load_routes()

        # Add error middleware to handle error routes if there are any
        if self.error_messages:
            self._setup_error_endpoint()

        # Add OAuth2 scheme to the app's OpenAPI schema
        valid_keys = OpenAPIArgs.__annotations__.keys()
        filtered_kwargs = {k: v for k, v in fastapi_kwargs.items() if k in valid_keys}

        # Add OAuth2 scheme to the app's OpenAPI schema
        self.app.openapi_schema = self.custom_openapi(auth_path, **filtered_kwargs)
        # assign nicegui at the end
        self._assign_ui()

    def custom_openapi(self, auth_path, **fastapi_kwargs):
        if self.app.openapi_schema:
            return self.app.openapi_schema

        # add version to fastapi_kwargs if not present
        if "version" not in fastapi_kwargs:
            fastapi_kwargs["version"] = "0.1.0"

        openapi_schema = get_openapi(routes=self.app.routes, **fastapi_kwargs)

        # Add security scheme
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {"password": {"tokenUrl": auth_path, "scopes": {}}},
            }
        }

        self.app.openapi_schema = openapi_schema
        return self.app.openapi_schema

    def custom_generate_unique_id(self, route: APIRoute) -> str:
        """
        Generate a unique operation ID based on the module name, function name, and HTTP method.
        """
        # Create a unique string based on the route's endpoint, method, and path
        base_id = f"{route.endpoint.__module__}_{route.endpoint.__name__}_{route.methods}_{route.path}"
        # print(f"Generated unique ID: {base_id}")

        # Hash the base_id to ensure uniqueness and avoid any collisions
        return hashlib.sha256(base_id.encode()).hexdigest()

    def _setup_exception_handler(self):
        @self.app.exception_handler(Exception)
        async def uncaught_exception_handler(request: Request, exc: Exception):
            DEBUG = True  # Set this to False in production
            if DEBUG:
                logger.exception(f"Caught exception: {str(exc)}")
                return Response(
                    content=f"Caught exception: {str(exc)}", status_code=500
                )
            return Response(content="Internal Server Error", status_code=500)

    def _setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Adjust this as needed for your application
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_error_endpoint(self):
        @self.app.get("/route_errors")
        async def route_errors():
            return {"errors": self.error_messages}

    async def _error_middleware(self, request: Request, call_next):
        path = request.url.path
        if path in self.app.router.routes:
            route = self.app.router.routes[path]
            if "error" in route.name.lower():
                return await route.endpoint(request)
        return await call_next(request)

    def _load_routes(self):
        for root, dirs, files in os.walk(self.routes_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    #print(f"Loading routes from: {os.path.join(root, file)}")
                    self._import_and_register_router(root, file)

        # Register WebSocket routes
        for module_name, ws_routes in _route_decorator.websocket_routes.items():
            for full_path, func, auth_required, kwargs in ws_routes:
                if auth_required:
                    # Wrap with authentication if required
                    async def wrapper(websocket: WebSocket, **path_params):
                        token = websocket.cookies.get('access_token')
                        if token is None:
                            await websocket.close(code=1008)  # Policy violation
                            return
                        try:
                            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        except jwt.PyJWTError:
                            await websocket.close(code=1008)
                            return
                        return await func(websocket=websocket, **path_params)
                    self.app.add_api_websocket_route(full_path, wrapper, **kwargs)
                else:
                    self.app.add_api_websocket_route(full_path, func, **kwargs)
                logger.info(f"Registered WebSocket route: {full_path}")

        # Print all registered routes after loading
        logger.info("\n*** Dynamic API Routes ***")
        logger.info("Registered routes:")
        for route in self.app.routes:
            if isinstance(route, APIRoute):
                # Handle standard HTTP routes
                _methods = ",".join(route.methods)
                logger.info(f"{route.name}: {route.path} ({_methods})")
            elif isinstance(route, APIWebSocketRoute):
                # Handle WebSocket routes
                _methods = "WEBSOCKET"
                logger.info(f"{route.name}: {route.path} ({_methods})")
            else:
                # Handle any other types of routes if necessary
                logger.warning(f"Unknown route type: {type(route)} for route: {route}")
        logger.info("\n*** End of Registered API Routes ***\n")

    def _import_and_register_router(self, root: str, file: str):
        # Create module name based on the file path
        module_path = os.path.join(root, file)
        module_name = (
            os.path.relpath(module_path, self.routes_dir)
            .replace(os.sep, ".")
            .replace(".py", "")
        )

        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module) 
 
            # Get the router specific to this module
            #deco_prefix = _route_decorator._compute_prefix(self.routes_dir, root, file)
            #print("trying to get router for module_name: ", module_name) 
            router = _route_decorator.get_router(module_name)
            #router = _route_decorator.get_router(deco_prefix+module_name)

            # Register the router with the NiceGUI APIRouter if it exists
            if router and isinstance(router, APIRouter):
                # Compute the prefix from the directory structure and file name
                prefix = self._compute_prefix(root, file)

                # Register the router with the FastAPI app
                self.app.include_router(
                    router,
                    prefix=prefix,
                    generate_unique_id_function=self.custom_generate_unique_id,
                )

        except Exception as exc:
            error_message = f"Error loading module {module_name}: {str(exc)}"
            logger.exception(error_message)
            self.error_messages[module_name] = error_message

    def _register_error_route(self, file: str, root: str, error_message: str):
        """
        Registers a simple error route that displays the error message.
        """
        prefix = self._compute_prefix(root, file)
        route_path = f"{prefix}/{file.replace('.py', '')}".rstrip("/")

        async def error_route():
            return {"error": error_message}

        self.app.add_api_route(
            route_path, error_route, methods=["GET", "POST", "PUT", "DELETE"]
        )
        logger.warn(f"Registered error route for {file}: {route_path}")

    def _compute_prefix(self, root: str, file: str) -> str:
        # Compute the directory part of the prefix
        dir_prefix = os.path.relpath(root, self.routes_dir).replace(os.sep, "/")
        if dir_prefix == ".":
            dir_prefix = ""

        # Return the directory prefix only, without including the file name
        return f"/{dir_prefix}".rstrip("/")

    def _assign_ui(self):
        """Start the FastAPI server with NiceGUI."""
        # Assign the NiceGUI server to FastAPI with the given configuration
        ui.run_with(app=self.app, reconnect_timeout=5.0, binding_refresh_interval=0.5, **self.nicegui_config)

    def listen(self, host:str="127.0.0.1", port:int=8000):
        import uvicorn, sys
        calling_script = Path(sys.argv[0]).stem
        module_reference = f"{calling_script}:app"
        uvicorn.run(module_reference, host=host, port=port, reload=True)
