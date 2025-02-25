from TeaLeaf.Server import Server
from TeaLeaf.Html.Component import Component
from TeaLeaf.Html.JS import JS
from TeaLeaf.Html.Elements import div, script
import uuid
import json
import os


class MagicComponent(Component):
    pass


class ReactiveComponent(Component):
    def reactive(self,path,id):
        js = f"""fetchAndUpdate({path},{{}},{id})"""
        self.attr(onclick=js)
        return self


class FetchComponent(Component):
    def __init__(self, url, body: str | dict | None = None) -> None:
        self._reid = new_id()
        placeholder = div("Loading...").id(self._reid)
        super().__init__("div", placeholder)
        # Configuración de la petición
        config = {"method": "POST" if body is not None else "GET", "body": body }
        # Serializar la configuración en JSON para JS
        config_js = json.dumps(config)
        js_file = os.path.dirname(__file__) + "/MagicComponent.js"
        js = JS(f"fetchAndUpdate('{url}','{config_js}','{placeholder._id}')",
            file=js_file)
        self.append(script(js))

    def reid(self):
       return self._reid


class PoolComponent(Component):
    def __init__(self, child: Component, url):
        pass


def new_id():
    return "tlmg" + str(uuid.uuid4()).split("-")[0]
