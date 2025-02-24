from TeaLeaf.Html.Component import Component
from TeaLeaf.Html.JS import JS
from TeaLeaf.Html.Elements import div, script
import uuid
import json
import os


class FetchComponent(Component):
    def __init__(self, url, body: str | dict | None = None) -> None:
        self._id = str(uuid.uuid4())
        super().__init__("div", div("Loading...").id(self._id))
        # Configuración de la petición
        config = {"method": "POST" if body is not None else "GET", "body": body }
        # Serializar la configuración en JSON para JS
        config_js = json.dumps(config)
        js_file = os.path.dirname(__file__) + "/MagicComponent.js"
        js = JS(f"fetchAndUpdate('{url}','{config_js}','{self._id}')",
            file=js_file)
        self.append(script(js))




def new_id():
    return uuid.uuid4()
