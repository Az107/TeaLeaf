
import json
import inspect
from TeaLeaf.Html.Component import Component

class HttpRequest:
    def __init__(self,
        method="GET",
        path="/",
        args={},
        headers={},
        body=""
    ):
        self.method=method
        self.path=path
        self.args=args
        self.headers=headers
        self.body=body

    def json(self):
        return json.loads(self.body)



class Server:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator


    def handle_request(self, request):
        handler = self.routes.get(request.path)

        if handler:
            sig = inspect.signature(handler)
            body = handler(request) if "req" in sig.parameters else handler()
            if isinstance(body, Component):
                body = body.build()
            if type(body) == dict:
                body = json.dumps(body)
            return '200 OK', [('Content-Type', 'text/html')], [body]
        return '404 Not Found', [('Content-Type', 'text/plain')], ["Not Found"]


    def serve(self, payload: str | Component):
        pass
