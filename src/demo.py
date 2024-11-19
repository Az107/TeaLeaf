from TeaLeaf.CGI import CGI
from TeaLeaf.Html.Elements import *
from TeaLeaf.Html.JS import JS
from TeaLeaf.Html.MagicComponent import FetchComponent

server = CGI()

def card(text):
    return div(
        h1(text),
        div(
            button("remove").attr(onclick=f"magic_button()"),
            button("accept").attr(onclick=f"magic_button()")
        ).classes("row")
    ).classes("card")



name = server.server_vars.get("name")
js = JS("""
    function magic_button(name) {
        alert("Hello " + name)
    }
""")

css = """
    body {

    }
"""

mincss = """<link rel="stylesheet" href="https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css">"""
userspace = FetchComponent("/example.py") if name == ["Alberto"] else h3("You are not alberto")

if server.method == "POST":
    content = div(
        card(f"Hello {name}") if name != None else "Empty name",
        div(userspace if name != None else "").classes("card")
    )
else:
    content = form("/demo.py", # add a value in server to call itself
        label(""),
        textInput().attr(name="name"),
        textInput().attr(type="submit")
    )

web = html(
    head(
        mincss,
        Component("title","TeaLeaf"),
        script(js),
        style(css)
    ),
    body(
        content
    )
)

server.serve(web)
