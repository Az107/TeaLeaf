import re
from  io import BytesIO
import json
import typing
import inspect
from TeaLeaf.Html.Component import Component


def path_to_regex(path: str) -> str:
    """Convierte una ruta con llaves en una expresión regular con grupos capturables."""
    regex = re.sub(r"\{([^}]+)\}", r"(?P<\1>[^/]+)", path)
    return f"^{regex}$"

def extract_wildcards(path_regex: str, url: str) -> dict | None:
    """Extrae los valores de las wildcards dado un regex generado y una URL."""
    match = re.match(path_regex, url)
    if match:
        return match.groupdict()  # Devuelve un diccionario con los valores capturados
    return None

class HttpRequest:
    def __init__(self,
        method="GET",
        path="/",
        args={},
        headers={},
        body:str|bytes|BytesIO|None = None
    ):
        self.method=method
        self.path=path
        self.args=args
        self.headers=headers
        self.body=body

    def json(self) -> dict|None:
        body = ""
        print("[python] body: " + str(self.body))
        if self.body is None:
            print("no body")
            return None
        if type(self.body) == BytesIO:
            body_buffer: BytesIO = self.body
            body = body_buffer.read(self.headers["content_length"]).decode("utf-8")
            body_buffer.close()
        else:
            if type(self.body) == bytes:
                body = self.body.decode()
            else:
                body: str  = str(self.body)
        try:
            return json.loads(body)
        except Exception as e:
            print(e)
            print(self.body)
            return None

def match_path(routes: dict[str, typing.Callable], path: str) -> tuple[dict[str,str], typing.Callable] | None:
    """Busca la primera ruta cuyo regex haga match con la path y devuelve su valor."""
    for regex, value in routes.items():
        match = re.match(regex,path)
        if match:
            return match.groupdict() ,value
    return None


class Server:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(func):
            path_regex = path_to_regex(path)
            self.routes[path_regex] = func
            return func
        return decorator


    def add_path(self,path,func):
        path_regex = path_to_regex(path)
        self.routes[path_regex] = func


    def handle_request(self, request):
        #handler = self.routes.get(request.path)
        handler_and_match = match_path(self.routes, request.path)

        if handler_and_match:
            params, handler = handler_and_match
            params["req"] = request
            sig = inspect.signature(handler)
            params = {k: v for k, v in params.items() if k in sig.parameters}
            body = handler(**params)
            if isinstance(body, Component):
                body = body.render()
            if type(body) == dict:
                body = json.dumps(body)
            return '200 OK', [('Content-Type', 'text/html')], [body]
        return '404 Not Found', [('Content-Type', 'text/plain')], ["Not Found"]


    def serve(self, payload: str | Component):
        pass
