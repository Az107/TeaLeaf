import json

class JSCode():
    def __init__(self, raw: str):
        self.raw = raw

    def __str__(self):
        return self.raw

    def __repr__(self):
        return self.raw

    def __invert__(self):
        return JSCode(f"!{self.raw}")

    def __getattr__(self, name: str):
        return JSCode(f"{self.raw}.{name}")

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
        print(f"jscode -> {JSCode(f"{self.raw}({payload})")}")
        return JSCode(f"{self.raw}({payload})")

    def __call__(self, *args: Any):
        return self.call(*args)
