from CGIpy.CGI import CGI
from CGIpy.html.HTMLElements import *

server = CGI()


js = """
    function magic_button(name) {
        alert("Hello " + name)
    }
"""

web = html(
    header(script(js)),
    body(
        h1(f"hello {server.server_vars.get("name")}"),
        button("click me").a(onclick=f"magic_button({server.server_vars["name"]})")
    )
)

server.serve(web)
