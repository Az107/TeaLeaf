import os
import sys
from urllib.parse import parse_qs

from CGIpy.html import Component


class CGI():
    def __init__(self) -> None:
        # Obtener los datos de entrada del formulario (si se pasan por POST)
        input_data = sys.stdin.read()

        # Obtener las variables de entorno CGI
        query_string = os.environ.get("QUERY_STRING", "")
        method = os.environ.get("REQUEST_METHOD", "")
        cgi_vars = {}

        # Obtener las variables de la query string
        if query_string:
            cgi_vars.update(parse_qs(query_string))

        # Si el método es POST, leer los datos del cuerpo de la solicitud
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

    def serve(self, output: str | Component):
        if isinstance(output, Component):
            print(output.build())
        else:
            print(output)
