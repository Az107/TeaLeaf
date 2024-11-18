from TeaLeaf.CGI import CGI
from TeaLeaf.html.HTMLElements import *

server = CGI()


js = """
    function magic_button(name) {
        alert("Hello " + name)
    }
"""

web = html(
    head(
        Component("title","TeaLeaf"),
        script(js)
    ),
    body(
        h1(f"hello {server.server_vars.get("name")}"),
        button("click me").a(onclick=f"magic_button({server.server_vars["name"]})")
    )
)

server.serve(web)
