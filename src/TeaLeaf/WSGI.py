
from TeaLeaf.Server import Interface
from TeaLeaf.Html import Component

class WSGI(Interface):
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator

    def handle_request(self, environ):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        handler = self.routes.get(path)
        if handler:
            return '200 OK', [('Content-Type', 'text/html')], handler()
        return '404 Not Found', [('Content-Type', 'text/plain')], ["Not Found"]

    def wsgi_app(self, environ, start_response):
        status, headers, body = self.handle_request(environ)
        start_response(status, headers)
        return [b.encode('utf-8') for b in body]

    def serve(self, payload: str | Component):
        return super().serve(payload)
