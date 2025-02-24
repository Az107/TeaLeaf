from TeaLeaf.Server import HttpRequest
from TeaLeaf.WSGI import WSGI
from TeaLeaf.Html.Elements import html, div, divRow, button, h1,h3, head, body,script
from TeaLeaf.Html.MagicComponent import FetchComponent


app = WSGI()

mincss = """<link rel="stylesheet" href="https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css">"""

@app.route("/health")
def health(req: HttpRequest):
    return {"status": "ok","method": req.method, "path": req.path, "body": str(req.json())}

@app.route("/user")
def user():
    return "no logged"

@app.route("/example")
def example(req: HttpRequest):
    print(req.body)
    name = req.json()["name"]
    userCard = divRow(
        script("""
            console.log("loaded");
            """),
        div(f"Username {name}"),
        button("logout").attr(onclick="alert('login out')").style(color="blue")
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
    userspace = FetchComponent("/example",{'name': 'Alb'}) if name == "Alberto" else h3("You are not alberto")
    ifconfig = FetchComponent("/health")
    web = html(
        mincss,
        head(script(js)),
        body(
            h1("Hello World"),
            userspace,
            ifconfig,
            button("click me").attr(onclick="alert('Hi')")
        )
    )
    return web


application = app.wsgi_app  # Punto de entrada WSGI



if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server('', 8000, application) as server:
        print("Serving on http://127.0.0.1:8000")
        server.serve_forever()
