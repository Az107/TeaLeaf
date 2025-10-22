from TeaLeaf.Html.JS import JS
import json
from TeaLeaf.Html.Elements import script
from typing import Dict, Any
from uuid import uuid4
import re

class JSCode():
    def __init__(self, raw: str):
        self.raw = raw

    def __str__(self):
        return self.raw

    def __repr__(self):
        return self.raw

     def __add__(self, other):
            return JSCode(f"({self.raw} + {other})")

    def __sub__(self, other):
        return JSCode(f"({self.raw} - {other})")

    def __mul__(self, other):
        return JSCode(f"({self.raw} * {other})")

    def __truediv__(self, other):
        return JSCode(f"({self.raw} / {other})")

    def call(self, *args):
        payload = ",".join(json.dumps(a) if not isinstance(a, JSCode) else str(a) for a in args)
        return JSCode(f"{self.raw}({payload})")

    def __call__(self, *args: Any):
        return self.call(*args)


class JSDO:
    def __init__(self, object_name: str, arg: Any):
        # js_file = os.path.dirname(__file__) + "/Store.js"
        self.obj_name = f"{object_name.lower()}_{str(uuid4())[:5]}"
        self.store_js = JS(code=f"const {self.obj_name} = new {object_name}({json.dumps(arg)})")

    def __format_js__(self, func_name: str, *args) -> JSCode:
        def fmt_arg(arg):
            if isinstance(arg, JSCode):
                return str(arg)
            return json.dumps(arg)
        def mark_js(obj):
            if isinstance(obj, JSCode):
                return f"__JS__:{obj.raw}"
            elif isinstance(obj, (list, tuple)):
                return [mark_js(o) for o in obj]
            elif isinstance(obj, dict):
                return {k: mark_js(v) for k, v in obj.items()}
            else:
                return obj

        marked = [mark_js(arg) for arg in args]
        payload = json.dumps(marked)
        payload = re.sub(r'"__JS__:(.*?)"', r'\1', payload)

        base_js = f"""{self.obj_name}.{func_name}({payload[1:-1]})"""
        return JSCode(
            base_js
        )

    def js(self):
        return script(self.store_js)

    def get(self, *args):
        return self.__format_js__("get", *args)

    def set(self, *args):
        return self.__format_js__("set", *args)

    def update(self, *args):
        return self.__format_js__("update", *args)



def Dom(query):
    return JSCode(f"""document.querySelector(`{query}`).value""")


def Not(code: JSCode):
    return JSCode(f"!{code}")
