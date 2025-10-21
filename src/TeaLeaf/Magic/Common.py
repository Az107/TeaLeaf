from TeaLeaf.Html.JS import JS
import json
from TeaLeaf.Html.Elements import script
from typing import Dict, Any
from uuid import uuid4

class JSDO:
    def __init__(self, object_name: str, arg: Any):
        # js_file = os.path.dirname(__file__) + "/Store.js"
        self.obj_name = f"{object_name.lower()}_{str(uuid4())[:5]}"
        self.store_js = JS(code=f"const {self.obj_name} = new {object_name}({json.dumps(arg)})")

    def __format_js__(self, func_name: str, *args):
        payload = ",".join(json.dumps(arg) for arg in args)
        base_js = f"""{self.obj_name}.{func_name}({payload})"""
        return (
            base_js.replace("\"'", "")
            .replace("'\"", "")
        )

    def js(self):
        return script(self.store_js).attr("defer")

    def get(self, *args):
        return self.__format_js__("get", *args)

    def set(self, *args):
        return self.__format_js__("set", *args)

    def update(self, *args):
        return self.__format_js__("update", *args)
