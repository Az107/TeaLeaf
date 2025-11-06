# 🍃 TeaLeaf

**TeaLeaf** is a *declarative web framework for Python* —
it lets you build dynamic, reactive web apps using **pure Python**,
without writing templates or frontend JavaScript manually.

---

## ✨ Overview

TeaLeaf merges ideas from modern frontend frameworks like React, Svelte, and SolidJS
with the simplicity of traditional Python web servers.

You declare HTML directly in Python, manage reactive state via `Store` objects,
and TeaLeaf takes care of keeping everything in sync — automatically.

---

## 🚀 Quick Example

```python
from TeaLeaf.Server.WSGI import WSGI
from TeaLeaf.Magic.Store import Store, SuperStore
from TeaLeaf.Html.Elements import div, h3, button

# Create the server
app = WSGI()
SuperStore(app)

# Reactive server-side store
counter = Store({"count": 0})

@app.route("/")
def home():
    return div(
        button("-").attr(onclick=counter.do.update("count", -1)),
        h3(counter.react("count")),
        button("+").attr(onclick=counter.do.update("count", 1)),
    )

application = app.wsgi_app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server("", 8000, application) as server:
        print("Serving at http://127.0.0.1:8000")
        server.serve_forever()
```

Open your browser and visit http://127.0.0.1:8000 —
you’ll see a fully reactive counter built with only Python


## Key Features
-  Declarative HTML components — build DOM structures with Python functions
-	 Path-based routing — simple, expressive route definitions
-	 Reactive server state (Store, AuthStore) — auto-sync between backend and UI
-	 JS transpilation (JSCode, JSDO) — write JavaScript logic directly in Python
-	Session support — cookies and per-user AuthStore state

##  Roadmap

- [x] Declarative HTML components
- [x] Path mapping
- [x] Server Side State (Stores)
- [x] JS transcription from python
- [ ] Client Side state
- [ ] State hooks
- [ ] Template system
- [ ] Persistent Store (redis,SQL...)
- [ ] CLI
- [ ] Render optimisation

Documentation

Full documentation is available in the [Wiki](https://github.com/Az107/TeaLeaf/wiki/Welcome-to-the-TeaLeaf!)

## Status

TeaLeaf is currently in alpha.
It’s stable enough for experimentation and small demos,
but the public API might still change before beta.

## License

MIT License © 2025 — TeaLeaf Framework Made with 🍃 and Python.
