from typing import List, Union, Any
import uuid
from types import FunctionType
import inspect




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

        self.styles: str | None = None
        self._id: str = "tl" + str(uuid.uuid4())
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

    def style(self, path: str | None = None, **attr):
        """
        Adds inline styles to the component.

        :param path: Optional path to an external CSS file.
        :param attr: CSS properties to apply (e.g., color="red", margin="10px").
        :return: The component instance (for method chaining).
        """

        self.styles = (self.styles or "") + f"#{self._id} {{\n"
        self.styles += "\n".join(
            f"  {k.replace('_', '-')}: {v};" for k, v in attr.items()
        )
        self.styles += "\n}"

        if path:
            with open(path, "r") as f:
                self.styles += f.read()
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
        return " " + " ".join(
            f"{k}='{v}'" if v is not None else f"{k}" for k, v in self.attributes.items()
        )

    def __build_child__(self, children: list):
        html_parts = []
        css_parts = []
        for child in children:
            if isinstance(child, str):
                html_parts.append(f"{child}")
            elif isinstance(child, list):
                html, css = self.__build_child__(child)
                html_parts.append(html)
                css_parts.append(css)
            elif isinstance(child, Component):
                html, css = child.build()
                html_parts.append(html)
                css_parts.append(css)
            else:
                try:
                    html_parts.append(str(child))
                except Exception:
                    continue
        return "".join(html_parts), "".join(filter(None, css_parts))

    def build(self) -> tuple[str, str]:
        """
        Builds the component's HTML and CSS separately.

        :return: A tuple (HTML string, CSS string)
        """

        if self.styles is not None and "id" not in self.attributes:
            self.attr(id=self._id)
        if len(self.children) == 0:
            result = f"<{self.name}{self.__build_attr__()}/>\n"
        else:
            endln = "\n" if len(self.children) > 1 else ""
            result = f"<{self.name}{self.__build_attr__()}>{endln}"
            html, styles = self.__build_child__(self.children)
            result += html
            if self.styles is None:
                self.styles = styles
            else:
                self.styles += styles
            result += f"\t</{self.name}>\n"
        css: str = "" if self.styles is None else self.styles
        return result, css

    def render(self) -> str:
        """
        Builds and returns the full HTML including inline CSS inside a <style> tag.

        :return: A complete HTML string with embedded CSS.
        """

        if len(self.children) == 0:
            result = f"<{self.name}{self.__build_attr__()}/>\n"
        else:
            inner_result, css = self.__build_child__(self.children)
            if self.styles is None:
                self.styles = css
            else:
                self.styles += css
            result = f"<{self.name}{self.__build_attr__()}>\n"
            if self.styles is not None:
                result += f"<style>{self.styles}</style>\n"
            result += inner_result
            result += f"</{self.name}>\n"

        return result


class ComponentMeta(type):
    def __new__(cls, name, bases, dct):
        # Creamos una clase personalizada para cada componente HTML
        if name not in ("Component", "ComponentMeta"):

            def init(self, *childs):
                super(self.__class__, self).__init__(name, *childs)

            dct["__init__"] = init
        return super().__new__(cls, name, bases, dct)
