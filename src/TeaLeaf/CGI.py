import os
import sys
from urllib.parse import parse_qs

from TeaLeaf.Server import Interface
from TeaLeaf.Html import Component


class CGI(Interface):
    def __init__(self) -> None:
        input_data = sys.stdin.read()

        query_string = os.environ.get("QUERY_STRING", "")
        method = os.environ.get("REQUEST_METHOD", "")
        cgi_vars = {}

        if query_string:
            cgi_vars.update(parse_qs(query_string))

        if method == "POST" and input_data:
            cgi_vars.update(parse_qs(input_data))

        # Obtener algunas variables de entorno comunes
        cgi_vars["REQUEST_METHOD"] = method
        cgi_vars["CONTENT_TYPE"] = os.environ.get("CONTENT_TYPE", "")
        cgi_vars["QUERY_STRING"] = query_string
        cgi_vars["PATH_INFO"] = os.environ.get("PATH_INFO", "")
        cgi_vars["SCRIPT_NAME"] = os.environ.get("SCRIPT_NAME", "")

        self.method = method
        self.server_vars = cgi_vars;

    def serve(self, payload: str | Component):
        if isinstance(payload, Component):
            print(payload.build())
        else:
            print(payload)
