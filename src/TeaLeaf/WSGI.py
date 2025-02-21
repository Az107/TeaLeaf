
from TeaLeaf.Server import HttpRequest, Server

from TeaLeaf.Html.Component import Component

class WSGI(Server):
    def __init__(self):
        super().__init__()


    def wsgi_app(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        request = HttpRequest(method,path)
        status, headers, body = self.handle_request(request)
        start_response(status, headers)
        return iter([b.encode('utf-8') for b in body])

    def serve(self, payload: str | Component):
        return super().serve(payload)
