# TeaLeaf 🍃☕✨
## SSE framework for python
TeaLeaf is a Python web framework designed to work seamlessly with HTeaPot.
It provides a declarative and reactive approach to building web applications,
inspired by SwiftUI.
TeaLeaf allows you to create server-side rendered (SSR) applications

## Features 🔧
### There are the actual and planed features
- [x] *Server-Side* Rendering (SSR): Generate HTML on the server for improved performance.
- [x] *Declarative UI*: Define your UI using a simple function-based syntax.
- [x] *Session managment*: TeaLeaf keep and handle data for sessions autmatically.
- [x] *WSGI and API Handling*: Serve dynamic content and interact with APIs.
- [x] *SuperStore*: A built-in store system that generates CRUD endpoints for data management.
- [x] *Scoped Styling*: Components can define their styles, which are automatically scoped and injected.
- [ ] *Reactivity*: Automatically update components using SSE.
- [ ] *Component-Based Architecture*: Reusable components for structuring your application.
- [ ] *Hydration Support*: Enable dynamic updates without full-page reloads.

## Installation 📦
TeaLeaf is still in development and not yet available as a package. You can clone the repository and integrate it into your project manually.
```bash
# Clone the repository
git clone https://github.com/your-repo/tealeaf.git

# Navigate to the project folder
cd tealeaf
```

## Usage 🚀

### Defining a Page
```Python
from TeaLeaf.WSGI import WSGI
from tealeaf.Html.Elements import body, h1, p, Button
app = WSGI()

app.route("/")
def index():
    return body(
        h1("Welcome to TeaLeaf!"),
        p("A simple and reactive Python web framework."),
        Button("Click me")
    )
```

### Using SuperStore 🗄️
```Python
app = WSGI()
SuperStore(app)
todo_store = Store()
todo_store.create(id="todo",data=[])


app.route("/todos")
def todos():
    return body(
        script(todo_store.do.js()),
        h1("TO-DO tasks"),
        [h3(c) for c in todo_store.read("todo")],
        div(
            textInput().id("new-todo"),
            button("Create").attr(
                onclick=todo_store.do.Update(
                    "todo",
                    Dom("#new-todo")
                )),
        ).row()
    )
```

## Roadmap 🛤️


## Contributing 🤝
Contributions are welcome! Feel free to submit issues or pull requests to improve TeaLeaf.

## License 📜
eaLeaf is released under the MIT License.
