from TeaLeaf.WSGI import WSGI
from TeaLeaf.Html.Elements import *


app = WSGI()

@app.route('/')
def home():
    js = """
        function magic_button(name) {
            alert("Hello " + name)
        }
    """

    web = html(
        head(script(js)),
        body(
            h1(f"hello World"),
            button("click me").attr(onclick=f"alert('Hi')")
        )
    )
    return [web.build()]


application = app.wsgi_app  # Punto de entrada WSGI



if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server('', 8000, application) as server:
        print("Serving on http://127.0.0.1:8000")
        server.serve_forever()
