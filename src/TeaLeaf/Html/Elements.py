from TeaLeaf.Html.Component import Component, ComponentMeta
from typing import Union, List, Any

class html(Component, metaclass=ComponentMeta):
    pass


class head(Component, metaclass=ComponentMeta):
    pass

class header(Component, metaclass=ComponentMeta):
    pass

class script(Component):
    def __init__(self, *childs: Union[str, List[Any], "Component"] ,src=None) -> None:
        super().__init__("script", *childs)
        if src != None:
            self.attr(src=src)
            self.children = [""]


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
        self.attr(style="display: flex; flex-direction: row")
        return self

    def column(self):
        self.attr(style="display: flex; flex-direction: column")
        return self


class button(Component, metaclass=ComponentMeta):

    def reactive(self,path,component_id):
        """
        Makes the button reactive by linking it to a FetchComponent.

        :param path: The URL to fetch new data from when clicked.
        :param component: The FetchComponent to be updated.
        """

        #config = {"method": "GET"}

        # Serializar la configuración en JSON para JS
        #config_js = json.dumps(config)
        js = f"""fetchAndUpdate('{path}','{{}}','{component_id}')"""
        self.attr(onclick=js)
        return self



class label(Component, metaclass=ComponentMeta):
    pass

class checkbox(Component):
    def __init__(self,checked = False, *childs):
        super().__init__("input", *childs)
        self.attr(type="checkbox")
        if checked:
            self.attr(checked="True")

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
