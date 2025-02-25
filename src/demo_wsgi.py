
from TeaLeaf.MagicFunction.Store import SuperStore, Store
from TeaLeaf.Server import HttpRequest
from TeaLeaf.WSGI import WSGI
from TeaLeaf.Html.Elements import checkbox, html, div,textInput, button, h1,h3, head, body,script
from TeaLeaf.Html.MagicComponent import FetchComponent


app = WSGI()
SuperStore(app)
cstore = Store()
cstore.create(id="counter",data=1)
print(cstore._id)

mincss = """<link rel="stylesheet" href="https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css">"""

@app.route("/health")
def health(req: HttpRequest):
    return {"status": "ok","method": req.method, "path": req.path, "body": str(req.json())}

contador = 0
@app.route("/api/contar")
def contar_api():
    global contador
    contador+=1
    return str(contador)

@app.route("/api/restar")
def restar_api():
    global contador
    contador-=1
    return str(contador)


@app.route("/contar")
def contar():
    contador = FetchComponent("/api/contar")
    return html(
        div(
            button("-").reactive("/api/restar",contador.reid()),
            contador,
            button("+").reactive("/api/contar",contador.reid())
        ).row()
    )


@app.route("/hello/{name}")
def saluda(req, name):
    return f"Hello {name} here is your req body {req.body}"

@app.route("/user")
def user():
    return "no logged"

@app.route("/example")
def example(req: HttpRequest):
    print(req.body)
    user = req.json()
    if user is None:
        name = ""
    else:
        name = user["name"]
    userCard = div(
        script("""
            console.log("loaded");
            """),
        div(f"Username {name}"),
        button("logout").attr(onclick="alert('login out')").style(backgroud_color="blue")
    ).row()
    return userCard


def elementoCompra(name):
    return div(
        checkbox(),
        name
    ).row()

@app.route('/')
def home():
    js = """
        function magic_button(name) {
            alert("Hello " + name)
        }
    """
    name = "Alberto"
    userspace = FetchComponent("/example",{'name': 'Alb'}) if name == "Alberto" else h3("You are not alberto")
    health = FetchComponent("/health")
    lista_compra = ["huevos","patatas","pimientos"]

    web = html(
        mincss,
        script(js),
        body(
            div(
                h1("Hello World!").style(color="red"),
                userspace.style(border="solid 1px grey"),
            ).row(),
            contar(),
            div(
            [elementoCompra(c) for c in lista_compra]
            ).style(padding="20px"),
            div(
                textInput(),
                button("Add")
            ).row()
        )
    )
    return web


application = app.wsgi_app  # Punto de entrada WSGI



if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server('', 8000, application) as server:
        print("Serving on http://127.0.0.1:8000")
        server.serve_forever()
