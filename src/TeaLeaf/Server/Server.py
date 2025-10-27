import io
import re
import json
import typing
from typing import Dict, Optional
import inspect
from TeaLeaf.Html.Component import Component
from uuid import uuid4
import os



def path_to_regex(path: str) -> str:
    """
    Converts a path with curly braces and optional wildcards into a regex pattern.

    Examples:
        "/users/{id}"      -> "^/users/(?P<id>[^/]+)$"
        "/test/{id}/*"     -> "^/test/(?P<id>[^/]+)(?:/.*)?$"
        "/foo/*/bar"       -> "^/foo/.*/bar$"

    Args:
        path (str): The path pattern with placeholders and/or wildcards.

    Returns:
        str: The equivalent regex pattern.
    """

    # Sustituimos {param} por grupos con nombre
    regex = re.sub(r"\{([^}]+)\}", r"(?P<\1>[^/]+)", path)

    # Sustituimos '*' por un patrón que capture el resto del path
    regex = regex.replace("*", ".*")

    # Si acaba en '.*' (wildcard final), permitimos que sea opcional
    if regex.endswith(".*"):
        regex = regex[:-2] + "(?:.*)?"

    return f"^{regex}$"


def extract_wildcards(path_regex: str, url: str) -> dict | None:
    """
    Extracts wildcard values from a given regex pattern and a matching URL.

    Args:
        path_regex (str): The compiled regex pattern.
        url (str): The incoming request URL.

    Returns:
        dict | None: A dictionary of extracted values or None if no match.
    """
    match = re.match(path_regex, url)
    if match:
        return match.groupdict()  # Devuelve un diccionario con los valores capturados
    return None


class Session(dict):
    """
    A session object that behaves like a dictionary but allows attribute-style access.
    """

    def has(self, attr):
        """Checks if a session attribute exists."""
        return self.get(attr) is not None


    def __getattr__(self, attr):
        try:
            return self[attr]  # Acceder como diccionario
        except KeyError:
            raise AttributeError(f"'Session' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        self[attr] = value  # Guardar en el diccionario


class HttpRequest:
    """
    Represents an HTTP request with attributes for method, path, headers, and body.
    """

    def __init__(
        self,
        method: str = "GET",
        path: str = "/",
        args: dict[str, str] = {},
        headers: dict[str, str] = {},
        body: str | bytes | io.BufferedReader | None = None,
    ):
        self.method: str = method
        self.path: str = path
        self.args: dict[str, str] = args
        self.headers: dict[str, str] = headers
        self.body: str | bytes | io.BufferedReader | None = body

    def to_str(self) -> str:
        return ""


    def __body_to_text__(self) -> str  | None:
        if "content_length" not in self.headers:
            return None


        body_size = int(self.headers.get("content_length") or 0)
        if body_size == 0:
            return None
        if isinstance(self.body, io.BufferedReader):
            if not self.body.closed and self.body.readable():
                return self.body.read(body_size).decode("utf-8")
            else:
                return None
        elif isinstance(self.body, bytes):
            return self.body.decode("utf-8")
        elif isinstance(self.body, str):
            return self.body
        else:
            raise ValueError("Invalid body type")


    def form(self) -> dict[str, str] | None:
        """
        Parses form-encoded body data into a dictionary.

        Returns:
            dict[str, str] | None: A dictionary of form values or None if invalid.
        """

        body = self.__body_to_text__()
        if body is None:
            return None
        return dict(item.split("=", 1) for item in body.split("&") if "=" in item)

    def json(self) -> Optional[dict]:
        """
        Parses the request body as JSON.

        Returns:
            dict | None: A dictionary representation of the JSON body or None if invalid.
        """

        body = self.__body_to_text__()
        if body is None:
             return None
        try:
            return json.loads(body)
        except (json.JSONDecodeError, AttributeError):
            return None


def match_path(
    routes: dict[str, typing.Callable], path: str
) -> tuple[dict[str, str | object], typing.Callable] | None:
    """
    Matches a given path against registered route patterns.

    Args:
        routes (dict[str, Callable]): A dictionary mapping regex patterns to handlers.
        path (str): The request path.

    Returns:
        tuple[dict, Callable] | None: Matched parameters and handler function, or None if no match.
    """

    for regex, value in routes.items():
        match = re.match(regex, path)
        if match:
            return match.groupdict(), value
    return None


def return_helper():
    try:
        helper = open(os.path.dirname(__file__) + "/helper.js")
        return "200 Ok", helper.read()
    except Exception as e:
        print(e)
        return "404 Not Found", "Not Found"


class Server:
    """
    HTTP server handling routing and session management.
    """

    def __init__(self):
        self.routes = {}
        self.sessions: dict[str, Session] = {}
        self.add_path("/_engine/helper.js", return_helper)

    def __create_session__(self):  # TODO: move to Session class
        """Generates a unique session ID."""
        return str(uuid4())

    def route(self, path):
        """Registers a function as a handler for a given route pattern."""

        def decorator(func):
            self.add_path(path, func)
            return func

        return decorator

    def add_path(self, path, func):
        """Manually adds a route-handler mapping."""

        path_regex = path_to_regex(path)
        self.routes[path_regex] = func

    def __handle_session__(self, cookies: dict):
        header_session_cookie = None
        if cookies.get("TeaLeaf-Session") is None:
            session_id = self.__create_session__()
            header_session_cookie = ("Set-Cookie", f"TeaLeaf-Session={session_id}")
            self.sessions[session_id] = Session()
        else:
            session_id = cookies["TeaLeaf-Session"]
            if self.sessions.get(session_id) is None:
                self.sessions[session_id] = Session()

        return self.sessions[session_id], header_session_cookie

    def __process_response__(self, response):
        res_code = "200 OK"
        res_headers = []
        if type(response) is tuple:
            res_len = len(response) - 1
            res_body = response[res_len]
            response = response[:res_len]
            for res_item in response:
                if type(res_item) is str or type(res_item) is int:
                    res_code = str(res_item)
                elif type(res_item) is list and type(res_item[0] is tuple):
                    res_headers += res_item
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

        res_headers.append(("Content-Type", content_type))
        return res_code, res_headers, res_body

    def handle_request(self, request: HttpRequest):
        handler_and_match = match_path(self.routes, request.path)

        if handler_and_match:
            params, handler = handler_and_match
            params["req"] = request

            _cookies = request.headers.get("COOKIE") or ""
            cookies = {
                k.strip(): v.strip()
                for k, v in (c.split("=", 1) for c in _cookies.split(";") if "=" in c)
            }

            params["session"], session_header = self.__handle_session__(cookies)
            params["cookies"] = cookies
            sig = inspect.signature(handler)
            params = {k: v for k, v in params.items() if k in sig.parameters}
            response = handler(**params)
            res_code, headers, res_body = self.__process_response__(response)
            if session_header is not None:
                headers.append(session_header)
            return res_code, headers, [res_body]
        return "404 Not Found", [("Content-Type", "text/plain")], ["Not Found"]

    def serve(self, payload: str | Component):
        pass
