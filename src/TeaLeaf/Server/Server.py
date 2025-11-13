from TeaLeaf.Html.Component import Component
import inspect
import io
import json
import os
import re
import typing
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4



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
            return self[attr]
        except KeyError:
            raise AttributeError(f"'Session' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        self[attr] = value


class Headers():
    def __init__(self, data: dict[str,str] = {}):
        self._data: dict[str, str] = {}
        for k in data:
            self._data[k.lower()] = data[k]

    def __getitem__(self, key: str):
        return self._data.get(key.lower())


    def __setitem__(self, name: str, value: str) -> None:
        self._data[name.lower()] = value


    def get(self, key: str):
        return self._data.get(key.lower())


    def __contains__(self, item):
        return item.lower() in self._data


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
        self.headers: Headers = Headers(headers)
        self.body: str | bytes | io.BufferedReader | Any | None = body

    def text(self) -> str | None:
        return self.__body_to_text__()

    def __body_to_text__(self) -> str | None:
        if "content_length" not in self.headers:
            return None

        body_size = int(self.headers.get("content_length") or 0)
        if body_size == 0 or self.body is None:
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
        elif hasattr(self.body, '__iter__'):
            result = b"".join([d for d in iter(self.body)])
            return result.decode("utf-8")
        else:
            raise ValueError(f"Invalid body type: {type(self.body)}")

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


class ServerEvent(Enum):
    on_response = "on_response"
    on_request = "on_request"
    path_registered = "path_registered"
    new_session = "new_session"



class Server:
    """
    HTTP server handling routing and session management.
    """

    def __init__(self):
        self.routes = {}
        self.sessions: dict[str, Session] = {}
        self._hooks: dict[ServerEvent,list[Callable[..., None]]] = {event: [] for event in ServerEvent}
        self.add_path("/_engine/helper.js", return_helper)

    def registry_hook(self, event: ServerEvent, callback: Callable[..., None]):
        event_hooks = self._hooks.get(event)
        if event_hooks is None:
            raise Exception("event dont exist")
        event_hooks.append(callback)

    def __call_hook__(self, event: ServerEvent, *payload):
        events = self._hooks.get(event)
        if events is None:
            return
        for callback in events:
            callback(*payload)

    def __create_session__(self):  # TODO: move to Session class
        """Generates a unique session ID."""
        session_id = str(uuid4())
        self.sessions[session_id] = Session()
        self.__call_hook__(ServerEvent.new_session, session_id, self.sessions[session_id])
        return session_id

    def route(self, path):
        """Registers a function as a handler for a given route pattern."""

        def decorator(func):
            self.add_path(path, func)
            return func

        return decorator

    def add_path(self, path, func):
        """Manually adds a route-handler mapping."""

        path_regex = path_to_regex(path)
        self.__call_hook__(ServerEvent.path_registered, path, path_regex, func)
        self.routes[path_regex] = func

    def __handle_session__(self, cookies: dict):
        header_session_cookie = None
        if cookies.get("TeaLeaf-Session") is None:
            session_id = self.__create_session__()
            header_session_cookie = ("Set-Cookie", f"TeaLeaf-Session={session_id}")
        else:
            session_id = cookies["TeaLeaf-Session"]
            if self.sessions.get(session_id) is None:
                self.sessions[session_id] = Session()
                self.__call_hook__(ServerEvent.new_session, session_id, self.sessions[session_id])


        return self.sessions[session_id], header_session_cookie

    def __process_response__(self, response):
        res_code = "200 OK"
        res_headers = []
        if isinstance(response, tuple):
            if len(response) == 3:
                res_code, res_headers, res_body = response
            elif len(response) == 2:
                res_code, res_body = response
                res_headers = []
            else:
                res_body = response[0]
                res_code, res_headers = "200 OK", []
        else:
            res_body = response

        self.__call_hook__(ServerEvent.on_response, res_code, res_body, res_headers)
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
        self.__call_hook__(ServerEvent.on_request, request)
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
