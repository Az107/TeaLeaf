from TeaLeaf.Html.JS import JS
from TeaLeaf.MagicFunction.Store import SuperStore, Store
from TeaLeaf.Server import HttpRequest
from TeaLeaf.WSGI import WSGI
from TeaLeaf.Html.Elements import (
    header,
    checkbox,
    head,
    form,
    html,
    div,
    textInput,
    button,
    h1,
    submit,
    body,
    script,
)
from TeaLeaf.Html.MagicComponent import FetchComponent, rButton
from TeaLeaf.utils import redirect, Dom


app = WSGI()
SuperStore(app)
cstore = Store()
cstore.create(id="todo", data=[])
cstore.create(id="counter", data=1)
print(cstore._id)

mincss = """<link rel="stylesheet" href="https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css">"""


@app.route("/health")
def health(req: HttpRequest):
    return {
        "status": "ok",
        "method": req.method,
        "path": req.path,
        "body": str(req.json()),
    }


@app.route("/api/contar")
def contar_api(session):
    print(session)
    if session.has("contador"):
        session.contador += 1
    else:
        session.contador = 0
    return str(session.contador)


@app.route("/api/restar")
def restar_api(session):
    if session.has("contador"):
        session.contador -= 1
    else:
        session.contador = 0
    return str(session.contador)


@app.route("/contar")
def contar():
    contador = FetchComponent("/api/contar")

    def test():
        a = 0
        a += 1
        return a

    return html(
        div(
            rButton("-").reactive("/api/restar", contador),
            contador,
            rButton("+").reactive("/api/contar", contador),
        ).row()
    )


@app.route("/hello/{name}")
def saluda(req, name):
    return (
        202,
        [("potato-header", "yay")],
        f"Hello {name} here is your req body {req.body}",
    )


def LoginPage():
    return html(
        mincss,
        form(textInput().id("userName").attr(name="userName"), submit("Login"))
        .action("/login")
        .method("POST"),
    )


@app.route("/login")
def user(session, req: HttpRequest):
    if session.has("name"):
        return "Hello " + session.name
    user = req.form()
    if user is None or not "userName" in user:
        return LoginPage()
    else:
        session.name = user["userName"]
        return redirect("/")


@app.route("/example")
def userNav(req: HttpRequest):
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
        button("logout")
        .attr(onclick="alert('login out')")
        .style(backgroud_color="blue"),
    ).row()
    return userCard


def elementoCompra(task):
    print(task)
    return div(
        checkbox(checked=task["done"]).attr(
            onchange=cstore.do.Update(
                "todo", {"done": not task["done"], "value": task["value"]}
            )
        ),
        task["value"],
    ).row()


@app.route("/")
def home(session, req: HttpRequest):
    print(session)
    if not session.has("name"):
        return redirect("/login")

    web = html(
        head(
            mincss,
            """<script src='_engine/worker.js'></script>""",

            script(cstore.do.js()),
        ),
        body(
            header(
                div(
                    h1("TeaLeaf!").style(color="green"),
                    h1(f"Welcome {session["name"]}"),
                ).row()
            ),
            div(
                contar(),
                div([elementoCompra(c) for c in cstore.read("todo")]).style(
                    padding="20px"
                ),
                div(
                    textInput().id("item_compra"),
                    button("Create").attr(
                        onclick=cstore.do.Update(
                            "todo", {"done": False, "value": Dom("#item_compra")}
                        )
                    ),
                ).row(),
            ).classes(["row"]),
        ),
    )
    return web


application = app.wsgi_app  # Punto de entrada WSGI


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    with make_server("", 8000, application) as server:
        print("Serving on http://127.0.0.1:8000")
        server.serve_forever()
