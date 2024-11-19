from TeaLeaf.Html.Component import Component, ComponentMeta


class html(Component, metaclass=ComponentMeta):
    pass

class head(Component, metaclass=ComponentMeta):
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

class button(Component, metaclass=ComponentMeta):
    pass


class label(Component, metaclass=ComponentMeta):
    pass


class textInput(Component):
    def __init__(self, *childs):
        super().__init__("input", *childs);


class form(Component):
    def __init__(self,action:str, *childs):
        super().__init__("form", *childs);
        self.attr(action=action)
