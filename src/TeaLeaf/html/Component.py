class Component:
    def __init__(self, name, *childs) -> None:
        self.name = name
        self.childs: list[Component] = list(childs)
        self.attributes: dict[str, str] = dict()

    def id(self, id: str):
        return self.attr(id=id)

    def classes(self, classes):
        self.attributes["class"] = classes
        return self

    def style(self, **attr):
        styles = ""
        for k in attr:
            styles += f"{k}:{attr[k]};"
        self.attributes["style"] = styles

    def attr(self, **attr):
        for k in attr:
            self.attributes[k] = attr[k]
        return self

    def append(self, child):
        self.childs.append(child)
        return self

    def __build_attr(self) -> str:
        result = ""
        for k in self.attributes:
            result += f'{k}="{self.attributes[k]}"'
        return result

    def build(self) -> str:
        if len(self.childs) == 0:
            result = f"<{self.name} {self.__build_attr()}/>\n"
        else:
            result = f"<{self.name} {self.__build_attr()}>\n"
            for child in self.childs:
                if type(child) is str:
                    result += f"\t{child}\n"
                else:
                    result += f"\t{child.build()}"

            result += f"</{self.name}>\n"
        return result


class ComponentMeta(type):
    def __new__(cls, name, bases, dct):
        # Creamos una clase personalizada para cada componente HTML
        if name not in ("Component", "ComponentMeta"):
            def init(self, *childs):
                super(self.__class__, self).__init__(name, *childs)

            dct['__init__'] = init
        return super().__new__(cls, name, bases, dct)
