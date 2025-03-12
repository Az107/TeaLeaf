from TeaLeaf.Html.Component import Component, ComponentMeta


class html(Component, metaclass=ComponentMeta):
    pass


class head(Component, metaclass=ComponentMeta):
    pass

class header(Component, metaclass=ComponentMeta):
    pass

class script(Component, metaclass=ComponentMeta):
    pass


class style(Component, metaclass=ComponentMeta):
    pass


class body(Component, metaclass=ComponentMeta):
    pass


class h1(Component, metaclass=ComponentMeta):
    pass


class h2(Component, metaclass=ComponentMeta):
    pass


class h3(Component, metaclass=ComponentMeta):
    pass


class div(Component, metaclass=ComponentMeta):
    pass

    def row(self):
        self.attr(style="display: flex; flex-directoion: row")
        return self

    def column(self):
        self.attr(style="display: flex; flex-directoion: column")
        return self


class button(Component, metaclass=ComponentMeta):
    pass


class label(Component, metaclass=ComponentMeta):
    pass

class checkbox(Component):
    def __init__(self, *childs):
        super().__init__("input", *childs)
        self.attr(type="checkbox")

class textInput(Component):
    def __init__(self, *childs):
        super().__init__("input", *childs)

class submit(Component):
    def __init__(self, *childs):
        super().__init__("input", *childs)
        self.attr(type="submit")

class form(Component):
    def __init__(self, *childs):
        super().__init__("form", *childs)

    def action(self, action):
        self.attr(action=action)
        return self

    def method(self, method):
        self.attr(method=method)
        return self
