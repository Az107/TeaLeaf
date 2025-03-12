import re
import json
import typing
import inspect
from TeaLeaf.Html.Component import Component
from uuid import uuid4


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


class Session(dict):
    def has(self, attr):
       return self.get(attr) is not None

    def __getattr__(self, attr):
            try:
                return self[attr]  # Acceder como diccionario
            except KeyError:
                raise AttributeError(f"'Session' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        self[attr] = value  # Guardar en el diccionario


class HttpRequest:
    def __init__(self,
        method="GET",
        path="/",
        args={},
        headers: dict[str,str] = {},
        body:str|bytes|None = None
    ):
        self.method=method
        self.path=path
        self.args=args
        self.headers=headers
        self.body=body

    def to_str(self) -> str:
        return ""


    def form(self) -> dict[str,str]|None:
        if self.body is None:
            return None
        if type(self.body) is not str:
            return None

        formData = {}
        if len(self.body) == 0:
            return None
        elements = self.body.split("&")
        if len(elements) == 0:
            return None

        for element in elements:
            print(f">{element}<")
            k,v = element.split("=",1)
            formData[k] = v

        return formData


    def json(self) -> dict|None:
        body = ""
        if self.body is None:
            return None
        if hasattr(self.body,"read") and type(self.body) is bytes:
            body_buffer = self.body
            body = body_buffer.read(self.headers["content_length"]).decode("utf-8")
            body_buffer.close()
        else:
            body = self.body
        try:
            return json.loads(body)
        except Exception:
            return None

def match_path(routes: dict[str, typing.Callable], path: str) -> tuple[dict[str, str | object ], typing.Callable] | None:
    """Busca la primera ruta cuyo regex haga match con la path y devuelve su valor."""
    for regex, value in routes.items():
        match = re.match(regex,path)
        if match:
            return match.groupdict() ,value
    return None


class Server:
    def __init__(self):
        self.routes = {}
        self.sessions: dict[str, Session] = {}


    def __create_session__(self):
        return str(uuid4())

    def route(self, path):
        def decorator(func):
            path_regex = path_to_regex(path)
            self.routes[path_regex] = func
            return func
        return decorator


    def add_path(self,path,func):
        path_regex = path_to_regex(path)
        self.routes[path_regex] = func


    def handle_request(self, request: HttpRequest):
        #handler = self.routes.get(request.path)
        handler_and_match = match_path(self.routes, request.path)

        if handler_and_match:
            params, handler = handler_and_match
            params["req"] = request

            headers = []
            _cookies = request.headers.get("Cookie") or ""
            cookies = {k.strip(): v.strip() for k, v in (c.split("=", 1) for c in _cookies.split(";") if "=" in c)}
            if cookies.get("TeaLeaf-Session") is None:
                session_id = self.__create_session__()
                header_session_cookie = ('Set-Cookie', f'TeaLeaf-Session={session_id}')
                headers.append(header_session_cookie)
                self.sessions[session_id] = Session()
            else:
                session_id = cookies["TeaLeaf-Session"]
                if self.sessions.get(session_id) is None:
                    self.sessions[session_id] = Session()

            session = self.sessions[session_id]
            params["session"] = session
            sig = inspect.signature(handler)
            params = {k: v for k, v in params.items() if k in sig.parameters}
            response = handler(**params)
            res_code = '200 OK'
            if type(response) is tuple:
                res_len = len(response) - 1
                res_body = response[res_len]
                response = response[:res_len]
                for res_item in response:
                    if type(res_item) is str or type(res_item) is int:
                        res_code = str(res_item)
                    elif type(res_item) is list and type(res_item[0] is tuple):
                        headers += res_item
                    else:
                        raise Exception("invalid type")

            else:
                res_body = response
            content_type = "text/plain"
            if isinstance(res_body, Component):
                content_type = "text/html"
                res_body = res_body.render()
            elif type(res_body) is dict or type(res_body) is list:
                content_type = "application/json"
                res_body = json.dumps(res_body)

            headers.append(('Content-Type', content_type))
            return res_code, headers, [res_body]
        return '404 Not Found', [('Content-Type', 'text/plain')], ["Not Found"]


    def serve(self, payload: str | Component):
        pass
