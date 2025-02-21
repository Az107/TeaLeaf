from TeaLeaf.Server import HttpRequest
from TeaLeaf.WSGI import WSGI
from TeaLeaf.Html import Elements as e
from TeaLeaf.Html.MagicComponent import FetchComponent


app = WSGI()

mincss = """<link rel="stylesheet" href="https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css">"""

@app.route("/health")
def health(req: HttpRequest):
    return {"status": "ok","method": req.method, "path": req.path}

@app.route("/user")
def user():
    return "no logged"

@app.route("/example")
def example(req: HttpRequest):
    userCard = e.divRow(
        e.div("Username {{name}}"),
        e.button("logout").attr(onclick="alert('login out')")
    )
    return userCard


@app.route('/')
def home():
    js = """
        function magic_button(name) {
            alert("Hello " + name)
        }
    """
    name = "Alberto"
    userspace = FetchComponent("/example") if name == "Alberto" else e.h3("You are not alberto")
    ifconfig = FetchComponent("https://ifconfig.co/json")
    web = e.html(
        mincss,
        e.head(e.script(js)),
        e.body(
            e.h1("Hello World around music"),
            userspace,
            ifconfig,
            e.button("click me").attr(onclick="alert('Hi')")
        )
    )
    return web


application = app.wsgi_app  # Punto de entrada WSGI



if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server('', 8000, application) as server:
        print("Serving on http://127.0.0.1:8000")
        server.serve_forever()
