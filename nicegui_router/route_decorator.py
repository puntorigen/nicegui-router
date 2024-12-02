import os, inspect, hashlib, jwt, asyncio
from functools import wraps
from datetime import datetime, timedelta
from nicegui import ui  # , APIRouter
from typing import Callable, Any, Dict, Optional, Annotated
from pydantic import BaseModel, create_model, Field
from fastapi import WebSocket, Request, Body, Depends, HTTPException, Header, Security, APIRouter
from fastapi.security import OAuth2PasswordBearer
from nicegui import ui  # , APIRouter
from .logging import setup_logger
from .theme import ThemeBuild
from .reactive import component

SECRET_KEY = "super-secret-key-for-jwt-make-it-unique-asap"
ALGORITHM = "HS256"

logger = setup_logger("route_decorator")


class RouteDecorator:
    def __init__(self):
        self.routers = {}
        self.websocket_routes = {}
        self.routes_dir = None
        self.auth_path = "/login"  # Default auth path

    def set_routes_dir(self, routes_dir: str):
        """Set the routes directory path for use in page routing."""
        self.routes_dir = routes_dir

    def set_auth_path(self, auth_path: str):
        """Set the authentication path to be used by auth decorators."""
        self.auth_path = auth_path

    def get_router(self, module_name: str = "") -> APIRouter:
        if module_name not in self.routers:
            self.routers[module_name] = APIRouter()
            # print(f"Created new router for module: {module_name}")
        return self.routers[module_name]
    
    def get_websocket_routes(self, module_name: str = "") -> list:
        if module_name not in self.websocket_routes:
            self.websocket_routes[module_name] = []
        return self.websocket_routes[module_name]

    # def get(self, path: str = None, **kwargs: Any) -> Callable: |||FOR REFERENCE
    # return self._create_route_decorator("get", path, **kwargs)

    # WEBSOCKET ROUTES DECORATORS
    def ws(self, path: str = None, **kwargs: Any) -> Callable:
        return self._create_websocket_route_factory(auth_required=False)(path, **kwargs)

    def ws_auth(self, path: str = None, **kwargs: Any) -> Callable:
        return self._create_websocket_route_factory(auth_required=True)(path, **kwargs)

    def _create_websocket_route_factory(self, auth_required: bool = False):
        def route_decorator(path: str = None, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                # Infer the correct module name from the calling context
                module_name = func.__module__
                caller_frame = inspect.stack()[1]
                caller_module = inspect.getmodule(caller_frame[0])
                module_name = caller_module.__name__ if caller_module else module_name

                # Get the root and file paths to compute the prefix
                module_path = os.path.abspath(caller_frame[1])
                root = os.path.dirname(module_path)
                file = os.path.basename(module_path).replace(".py", "")

                if self.routes_dir is None:
                    raise ValueError(
                        "routes_dir must be set using set_routes_dir before using the page decorator."
                    )

                # Compute the prefix using the copied _compute_prefix method
                prefix = self._compute_prefix(self.routes_dir, root, file)
                #print(f"prefix: {prefix}, path: {path}, file: {file}")

                # Combine the prefix with the provided or inferred path
                if not path:
                    full_path = f"{prefix}/".rstrip("/")
                else:
                    full_path = f"{prefix}/{path}".rstrip("/")

                full_path = full_path.replace("//", "/")
                if full_path == "":
                    full_path = "/"
                if file == "index" and not path:
                    full_path = "/"
                
                #print(f"full_path: {full_path}")

                # Generate a unique operation ID for the websocket
                operation_id = self._generate_operation_id(func, 'websocket', full_path, module_name)
                kwargs["name"] = operation_id  # 'name' is used for websockets

                # Save the route for later registration
                websocket_routes = self.get_websocket_routes(module_name)
                websocket_routes.append((full_path, func, auth_required, kwargs))
                logger.info(f"Prepared WebSocket route: {full_path} for module {module_name}")
                return func

            return decorator

        return route_decorator

    
    # NON-AUTHENTICATED ROUTES DECORATED
    def get(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory("get")(path, input, output, example, **kwargs)

    def post(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory("post")(
            path, input, output, example, **kwargs
        )

    def put(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory("put")(path, input, output, example, **kwargs)

    def delete(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory("delete")(
            path, input, output, example, **kwargs
        )

    # NICEGUI PAGES DECORATOR
    def page(self, path: str = "/", theme: Optional[ThemeBuild] = None, **kwargs: Any) -> Callable:
        def decorator(func: Callable) -> Callable:
            # Infer the correct module name from the calling context
            module_name = func.__module__
            caller_frame = inspect.stack()[1]
            caller_module = inspect.getmodule(caller_frame[0])
            module_name = caller_module.__name__ if caller_module else module_name

            # Get the root and file paths to compute the prefix
            module_path = os.path.abspath(caller_frame[1])
            root = os.path.dirname(module_path)
            file = os.path.basename(module_path).replace(".py", "")

            if self.routes_dir is None:
                raise ValueError(
                    "routes_dir must be set using set_routes_dir before using the page decorator."
                )

            # Compute the prefix using the copied _compute_prefix method
            prefix = self._compute_prefix(self.routes_dir, root, file)

            # Combine the prefix with the provided or inferred path
            if not path:
                full_path = f"{prefix}/".rstrip("/")
            else:
                full_path = f"{prefix}/{path}".rstrip("/")

            full_path = full_path.replace("//", "/")
            if full_path == "":
                full_path = "/"
            if file == "index" and not path:
                full_path = "/"

            logger.info(f"Registering page: GET {full_path} in module {module_name}")
            # Define the wrapped function to apply the theme if provided
            @wraps(func)
            async def wrapped_func(*args, **kwargsI):
                if theme:
                    with theme().build():
                        result = func(*args, **kwargsI)
                        if asyncio.iscoroutine(result):
                            return await result
                        else:
                            return result
                else:
                    result = func(*args, **kwargsI)
                    if asyncio.iscoroutine(result):
                        return await result
                    else:
                        return result

            # Register the page with NiceGUI
            ui.page(full_path, **kwargs)(wrapped_func)
            return wrapped_func

        return decorator

    def _compute_prefix(self, routes_dir: str, root: str, file: str) -> str:
        # Compute the directory part of the prefix
        dir_prefix = os.path.relpath(root, routes_dir).replace(os.sep, "/")
        if dir_prefix == ".":
            dir_prefix = ""
        # If the file is 'index', suppress the file name in the prefix
        prefix = ""
        if file != "index":
            prefix = f"/{dir_prefix}/{file}".rstrip("/")
        else:
            prefix = f"/{dir_prefix}".rstrip("/")

        return prefix.replace("//", "/")

    # SECURED ROUTES DECORATORS
    def get_auth(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory(
            "get", auth_required=True, login=self.auth_path
        )(path, input, output, example, **kwargs)

    def post_auth(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory(
            "post", auth_required=True, login=self.auth_path
        )(path, input, output, example, **kwargs)

    def put_auth(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory(
            "put", auth_required=True, login=self.auth_path
        )(path, input, output, example, **kwargs)

    def delete_auth(
        self,
        path: str = None,
        input: Any = None,
        output: Any = None,
        example: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Callable:
        return self._create_route_factory(
            "delete", auth_required=True, login=self.auth_path
        )(path, input, output, example, **kwargs)

    # FACTORY METHODS
    def _create_route_factory(
        self, method: str, auth_required: bool = False, login: str = "/login"
    ):
        def route_decorator(
            path: str = None,
            input: Any = None,
            output: Any = None,
            example: Dict[str, Any] = None,
            **kwargs: Any,
        ) -> Callable:
            def decorator(func: Callable) -> Callable:
                # Infer the path if not provided
                nonlocal path
                if not path:
                    path = self._infer_path(func)

                # if not running from the routes directory, skip the route registration
                if not self.routes_dir:
                    return func
                # Infer the correct module name from the calling context
                module_name = func.__module__
                caller_frame = inspect.stack()[1]
                caller_module = inspect.getmodule(caller_frame[0])
                module_name = caller_module.__name__ if caller_module else module_name
                # Get the root and file paths to compute the prefix
                # NEW SECTION
                module_path = os.path.abspath(caller_frame[1])
                root = os.path.dirname(module_path)
                file = os.path.basename(module_path).replace(".py", "")
                prefix = self._compute_prefix(self.routes_dir, root, file)
                full_path = os.path.join(self.routes_dir, path.lstrip("/"))
                method_name = full_path.split("/")[-1]
                if prefix == "":
                    prefix = "/"+method_name
                module_name = prefix[1:].replace("/", ".")
                #print(f"route: {prefix}, module_name: {module_name}, method_name: {method_name}")
                # Convert 'input' to a Pydantic model if provided
                #if input: 
                    #inputx = self._create_pydantic_model(input)
                    #request_body = Body(...)
                    #input = inputx
                    #func = self._wrap_func_with_request_model(
                    #    func, request_model, request_body
                    #)

                # Attach the 'output' model if provided
                if output:
                    response_model = self._create_pydantic_model(output, example)
                    kwargs["response_model"] = response_model
                    #kwargs["response_model_exclude_unset"] = True if "response_model_exclude_unset" not in kwargs else kwargs["response_model_exclude_unset"]
                    kwargs["response_model_exclude_unset"] = False

                @wraps(func)
                async def wrapped_func(
                    request: Request = Depends(dependency=None, use_cache=False),
                    *args,
                    **kwargs,
                ):
                    # try:
                    # Authentication check if required
                    # Inject the Request and token using Depends
                    # request: Request = kwargs.pop('request', None) or Request(scope=Depends())
                    # token: str = kwargs.pop('token', None) or await oauth2_scheme(request)
                    if auth_required:
                        token = await OAuth2PasswordBearer(tokenUrl="token")(request)
                        # token = kwargs.get("x_token")
                        logger.info(f"Verifying token: {token}")
                        if token is None:
                            raise HTTPException(
                                status_code=403, detail="Not authenticated"
                            )
                        try:
                            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        except jwt.PyJWTError:
                            raise HTTPException(
                                status_code=403, detail="Token is invalid or expired"
                            )
                        # print(f"Executing function: {func.__name__}, args: {args}, kwargs: {kwargs}")
                        kwargs["request"] = request

                    # Execute the original function
                    return await func(*args, **kwargs)
                    # except Exception as e:
                    #    raise HTTPException(status_code=500, detail=str(e))

                # Generate a unique operation ID
                operation_id = self._generate_operation_id(
                    func, method, full_path, module_name
                )

                # Assign the unique operation ID
                kwargs["operation_id"] = operation_id

                # Register the route only if it does not already exist
                router = self.get_router(module_name) 
                auth_flag = " (AUTH)" if auth_required else "" 

                if not any(r.path == path for r in router.routes):
                    logger.info(
                        f"Registering route: {method.upper()}{auth_flag} {prefix} in module {module_name}"
                    )
                    if auth_required:
                        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
                        kwargs["dependencies"] = [Depends(oauth2_scheme)]

                        @wraps(wrapped_func)
                        async def wrapper2(*args2, request: Request, **kwargs2):
                            # logger.info(f"args2: {args2}, kwargs2: {kwargs2}")
                            kwargs2["request"] = request
                            return await wrapped_func(*args2, **kwargs2)

                        getattr(router, method)(path, **kwargs)(wrapper2)  #
                        return wrapper2
                    else:
                        getattr(router, method)(path, **kwargs)(wrapped_func)

                else:
                    logger.warning(
                        f"Skipping duplicate route registration for route: {prefix}"
                    )

                return wrapped_func

            return decorator

        return route_decorator

    # HELPER METHODS
    def _wrap_func_with_request_model(
        self, func: Callable, model: Any, body: Body
    ) -> Callable:
        async def wrapper(input: model = Depends()): # type: ignore
            return await func(input)

        # Manually set the name and docstring
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__

        return wrapper

    def _create_pydantic_model(
        self, base: Any, example: Dict[str, Any] = None
    ) -> BaseModel:
        """Converts a simple Python class into a Pydantic model, optionally adding an example."""
        fields = {
            key: (value, Field(..., example=example.get(key) if example else None))
            for key, value in base.__annotations__.items()
        }
        return create_model(base.__name__, **fields)

    def _generate_operation_id(
        self, func: Callable, method: str, path: str, module_name: str
    ) -> str:
        """Generate a unique operation ID based on the module, function, method, and path."""
        function_name = func.__name__

        # Create a unique base ID
        base_id = f"{module_name}_{function_name}_{method}_{path}"
        return hashlib.sha256(base_id.encode()).hexdigest()

    def _infer_path(self, func: Callable) -> str:
        # Infer the path from the module's file name
        file_path = inspect.getfile(func)
        file_name = os.path.basename(file_path).replace(".py", "")
        # print(f"inferred path: {file_name}", file_path)
        return f"/{file_name}"


# Utility function to create a JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Create a global instance of RouteDecorator
_route_decorator = RouteDecorator()

# Export the decorators directly
get = _route_decorator.get
post = _route_decorator.post
put = _route_decorator.put
delete = _route_decorator.delete
page = _route_decorator.page
get_auth = _route_decorator.get_auth
post_auth = _route_decorator.post_auth
put_auth = _route_decorator.put_auth
delete_auth = _route_decorator.delete_auth
ws = _route_decorator.ws
ws_auth = _route_decorator.ws_auth