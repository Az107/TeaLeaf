import hashlib
import json
from typing import List, Union, Any
import uuid
from types import FunctionType
import inspect
import html as html_tools
from dataclasses import dataclass

globals()["component_cache"] = {}
globals()["render_calls"] = 0

class Component:
    """
    Represents an HTML component with attributes, children, and optional inline styles.
    This class allows constructing HTML elements programmatically and managing CSS styles.
    """

    def __init__(self, name, *childs: Union[str, List[Any], "Component"]) -> None:
        """
        Initializes a new Component instance.

        :param name: The tag name of the HTML element.
        :param childs: Optional children elements, which can be strings, lists, or other Component instances.
        """
        self.unsafe = False
        self._id: str = "tl" + name[:2]
        self.name = name
        self.children: list[Component | str | list] = list(childs)
        self.attributes: dict[str, str | None] = dict()

    def id(self, id: str):
        """
        Sets the ID of the component and adds it as an attribute.

        :param id: The ID to assign.
        :return: The component instance (for method chaining).
        """
        self._id = id
        return self.attr(id=id)

    def classes(self, classes):
        """
        Adds a CSS class attribute to the component.

        :param classes: CSS class names (space-separated).
        :return: The component instance (for method chaining).
        """

        self.attributes["class"] = classes
        return self

    def style(self, **attr):
        """
        Adds inline styles to the component.

        :param path: Optional path to an external CSS file.
        :param attr: CSS properties to apply (e.g., color="red", margin="10px").
        :return: The component instance (for method chaining).
        """
        style = ""
        for k in attr:
            v = attr[k]
            style += f"{k}: {v};"

        self.attributes["style"] = style

        return self


    def attr(self,*args, **attr):
        """
        Adds custom attributes to the component.

        :param attr: Dictionary of attribute names and values.
        :return: The component instance (for method chaining).
        """

        for arg in args:
            self.attributes[arg] = None

        for k in attr:

            # if type(attr[k]) is str:
            self.attributes[k] = str(attr[k])
            # elif type(attr[k]) is FunctionType:
            #     py_f = inspect.getsource(attr[k])
            #     self.attributes[k] = f"""() => pyodide.runPython(`{py_f}`)"""

        return self

    def append(self, child: Union[str, "Component", list]):
        """
        Appends a child element to the component.

        :param child: A Component, string, or list of elements.
        :return: The component instance (for method chaining).
        """

        self.children.append(child)
        return self

    def __build_attr__(self) -> str:
        if len(self.attributes) == 0:
            return ""
        return " " + " ".join(
            f"{k}='{v}'" if v is not None else f"{k}" for k, v in self.attributes.items()
        )


    def __build_html__(self, enable_styles = False) -> str:
        def render_child(child: str|list|Component) -> str:
            if isinstance(child, str):
                if self.unsafe:
                    return child
                else:
                    return html_tools.escape(str(child), quote=True)
            elif isinstance(child, list):
                result = ""
                for c in child:
                    result += render_child(c)
                return result
            elif isinstance(child, Component):
                result = child.__build_html__()
                return result
            else:
                try:
                    return str(child)
                except Exception:
                    pass


        hash = self.__hash_state__()
        if hash in globals()["component_cache"]:
            return globals()["component_cache"][hash]
        globals()["render_calls"] += 1
        if "id" in self.attributes:
            self.attr(id=self._id)

        if len(self.children) == 0:
            result = f"<{self.name}{self.__build_attr__()}/>"
        else:
            result = f"<{self.name}{self.__build_attr__()}>"
            for child in self.children:
                result += render_child(child)
            result += f"</{self.name}>"
        globals()["component_cache"][hash] = result
        return result



    # @lru_cache
    def render(self) -> str:
        """
        Builds and returns the full HTML including inline CSS inside a <style> tag.

        :return: A complete HTML string with embedded CSS.
        """
        globals()["render_calls"] = 0
        result = self.__build_html__()
        return result



    def __hash_state__(self) -> str:
        """
        Devuelve un hash único que representa el estado actual del componente.
        """

        def serialize_child(child):
            if isinstance(child, Component):
                return child.__hash_state__()
            elif isinstance(child, list):
                return [serialize_child(c) for c in child]
            return str(child)

        state = {
            "name": self.name,
            "attributes": self.attributes,
            "children": [serialize_child(c) for c in self.children],
        }

        raw = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha1(raw.encode()).hexdigest()





class ComponentMeta(type):
    def __new__(cls, name, bases, dct):
        # Creamos una clase personalizada para cada componente HTML
        if name not in ("Component", "ComponentMeta"):

            def init(self, *childs):
                super(self.__class__, self).__init__(name, *childs)

            dct["__init__"] = init
        return super().__new__(cls, name, bases, dct)
