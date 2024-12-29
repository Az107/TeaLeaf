from TeaLeaf.Html.Component import Component
from TeaLeaf.Html.JS import JS
from TeaLeaf.Html.Elements import div, script
import uuid


class FetchComponent(Component):
    def __init__(self, url) -> None:
        self._id = str(uuid.uuid4())
        super().__init__("div", div("Loading...").id(self._id))
        js = JS("""
                fetch('{url}').then(
                    r => r.text().then(
                       text => document.getElementById('{id}').innerHTML = text
                    )
                )
                """,
                url=url, id=self._id)
        self.append(script(js))


def new_id():
    return uuid.uuid4()
