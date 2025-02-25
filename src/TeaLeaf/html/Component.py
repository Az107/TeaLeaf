from typing import Union
import uuid
from warnings import catch_warnings

def flatten(lst: list):
    return [item for sublist in lst for item in (sublist if isinstance(sublist, list) else [sublist])]

class Component:
    def __init__(self, name, *childs: Union[str,list,'Component']) -> None:
        self.styles: str | None = None
        self._id: str = "tl" + str(uuid.uuid4())
        self.name = name
        self.childs: list[Component|str|list] = list(childs)

        self.attributes: dict[str, str] = dict()


    def id(self, id: str):
        self._id = id
        return self.attr(id=id)

    def classes(self, classes):
        self.attributes["class"] = classes
        return self

    def style(self,path: str|None = None, **attr):
        if self.styles is None:
            self.styles = f"#{self._id} {{\n"
        else:
            self.styles = self.styles[:-1]
        for k in attr:
            self.styles += f"{k.replace("_","-")}: {attr[k]};"
        self.styles += "}"
        if path is not None:
            f = open(path, "r")
            self.styles += f.read()
        return self


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
            result += f' {k}="{self.attributes[k]}"'
        return result


    def __build_child__(self,childs: list):
        result = ""
        styles = ""
        for child in childs:
            if type(child) is str:
                result += f"{child}"
            elif type(child) is list:
                html,css = self.__build_child__(child)
                result+= html
                styles +=css
            elif isinstance(child, Component):
                html,css = child.build()
                if styles is not None:
                    if styles != "":
                        styles += "\n"
                    styles += css
                result += html
            else:
                try:
                    result += str(child)
                except:
                    continue
        return result,styles


    def build(self) -> tuple[str,str]:
        if self.styles is not None and "id" not in self.attributes:
            self.attr(id=self._id)
        if len(self.childs) == 0:
            result = f"<{self.name}{self.__build_attr()}/>\n"
        else:
            endln = "\n" if len(self.childs) > 1 else ""
            result = f"<{self.name}{self.__build_attr()}>{endln}"
            html,styles = self.__build_child__(self.childs)
            result += html
            if self.styles is None:
                self.styles = styles
            else:
                self.styles+=styles
            result += f"\t</{self.name}>\n"
        css: str = "" if self.styles is None else self.styles
        return result,css

    def render(self) -> str:
        if len(self.childs) == 0:
            result = f"<{self.name}{self.__build_attr()}/>\n"
        else:
            inner_result,css = self.__build_child__(self.childs)
            if self.styles is None:
                self.styles = css
            else:
                self.styles += css
            result = f"<{self.name}{self.__build_attr()}>\n"
            if self.styles is not None:
                result += f"<style>{self.styles}</style>\n"
            result+=inner_result
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
