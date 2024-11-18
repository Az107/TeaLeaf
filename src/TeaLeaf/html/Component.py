from typing import Any, Self

class Component:
    def __init__(self,name,*childs) -> None:
        self.name = name
        self.childs: list[Component] = list(childs)
        self.attr = dict()


    def a(self, **attr):
        return self.attributes(**attr)

    def attributes(self, **attr):
        for k in attr:
            self.attr[k] = attr[k]
        return self

    def append(self, child):
        self.childs.append(child)
        return self

    def __build_attr(self) -> str:
        result = ""
        for k in self.attr:
            result+=f'{k}="{self.attr[k]}"'
        return result;


    def build(self) -> str:
        result = f"<{self.name} {self.__build_attr()}>"
        for child in self.childs:
            if type(child) == str:
                result+=child
            else:
                result+=child.build()
        result += f"</{self.name}>"
        return result

class ComponentMeta(type):
    def __new__(cls, name, bases, dct):
        # Creamos una clase personalizada para cada componente HTML
        if name not in ("Component", "ComponentMeta"):
            def init(self, *childs):
                super(self.__class__, self).__init__(name, *childs)

            dct['__init__'] = init
        return super().__new__(cls, name, bases, dct)
