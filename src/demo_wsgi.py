from TeaLeaf.Html.JS import JS
from TeaLeaf.Magic.Store import SuperStore, Store
from TeaLeaf.Magic.LocalState import use_state
from TeaLeaf.Server.Server import HttpRequest
from TeaLeaf.Server.WSGI import WSGI
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
    h2,
    h3,
    submit,
    body,
    script,
)
from TeaLeaf.Magic.MagicComponent import FetchComponent, rButton
from TeaLeaf.utils import redirect
from TeaLeaf.Magic.Common import Not, Dom


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



@app.route("/contar")
def contar():

    return div(
            rButton("-").attr(onclick=cstore.do.update("counter",-1)),
            h3( cstore.react("counter")),
            rButton("+").attr(onclick=cstore.do.update("counter", 1)),
        ).row()



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
    if session.has("userName"):
        return "Hello " + session.userName
    print(req.body)
    user = req.form()
    print(user)
    if user is None or not "userName" in user:
        return "401 unauthorized", LoginPage()
    else:
        session.userName = user["userName"]
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
            onchange=cstore.do.update(
                "todo", {"done": not task["done"], "value": task["value"], "id": task["id"]}
            )
        ),
        h2(task["value"]),
        button("x").classes("secondary")
    ).row().classes("card")


@app.route("/")
def home(session, req: HttpRequest):
    if not session.has("userName"):
        return redirect("/login")

    modal_state = use_state(True)

    web = html(
        head(
            mincss,
            script("", src="_engine/worker.js"),
        ),
        body(
            header(
                div(
                    h1("TeaLeaf!").style(color="green"),
                    button(f"Welcome {session["userName"]}").attr(onclick=modal_state.set(Not(modal_state.get()))),
                ).row()
            ),
            div("Esto es modal").classes("card").row().attr(hidden=modal_state.get()),
            div(
                contar(),
                div([elementoCompra(c) for c in cstore.read("todo")]).style(
                    padding="20px",
                    height="200px",
                    overflow_y="scroll"
                ),
                div(
                    textInput().id("item_compra"),
                    button("Create").attr(
                        onclick=cstore.do.set(
                            "todo", {"done": False, "value": Dom("#item_compra")}
                        )
                    ),
                ).row(),
            )
        ),
        modal_state.js(),
        cstore.do.js(),
    )
    return web


application = app.wsgi_app  # Punto de entrada WSGI


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    with make_server("", 8000, application) as server:
        print("Serving on http://127.0.0.1:8000")
        server.serve_forever()
