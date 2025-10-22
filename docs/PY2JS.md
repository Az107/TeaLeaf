# JSCode — General Pupose Spec


## Specification

### ***1. Basic build***
 ```Python
 class JSCode:
     def __init__(self, raw: str):
 ```
- raw: valid JS code that is inserted as is.
- JSCode is immutable (each operation generates a new instance).



### ***2. Conversion and representation***
```Python
def __str__(self) -> str:
def __repr__(self) -> str:
```

### ***3. Properties and methods access***

```Python
def __getattr__(self, name: str) -> JSCode:
    return JSCode(f"{self.raw}.{name}")

def call(self, *args) -> JSCode:
    payload = ",".join(_js_arg(a) for a in args)
    return JSCode(f"{self.raw}({payload})")

def __call__(self, *args) -> JSCode:
    self.call(*args)
```
Example:
```Python
document = JSCode("document")
expr = document.getElementById("my_id").value
# => JSCode("document.getElementById('my_id').value")
```



### ***4. Common operators (arithmetic, logic, comparative)***

```Python
def _binary(self, op, other):
    return JSCode(f"({self.raw} {op} {_js_arg(other)})")

__add__ = lambda self, o: self._binary("+", o)
__sub__ = lambda self, o: self._binary("-", o)
__mul__ = lambda self, o: self._binary("*", o)
__truediv__ = lambda self, o: self._binary("/", o)
__eq__ = lambda self, o: self._binary("==", o)
__ne__ = lambda self, o: self._binary("!=", o)
__lt__ = lambda self, o: self._binary("<", o)
__le__ = lambda self, o: self._binary("<=", o)
__gt__ = lambda self, o: self._binary(">", o)
__ge__ = lambda self, o: self._binary(">=", o)
__and__ = lambda self, o: self._binary("&&", o)
__or__ = lambda self, o: self._binary("||", o)
```


Unitary operators:
```Python
def __neg__(self): return JSCode(f"(-{self.raw})")
def __invert__(self): return JSCode(f"!{self.raw}")
```

Example:
```Python
    Dom("#id").value == "hola"
    # => JSCode("(document.querySelector(`#id`).value == 'hola')")
```

### ***5. “await”, “new”, y expression templates***

```Python
def await_(self) -> "JSCode":
    return JSCode(f"await {self.raw}")

def new(self, *args) -> "JSCode":
    payload = ",".join(_js_arg(a) for a in args)
    return JSCode(f"new {self.raw}({payload})")

def template(self, **vars) -> "JSCode":
    # JSCode("`hola ${name}`").template(name=JSCode("user.name"))
    code = self.raw
    for k, v in vars.items():
        code = code.replace("${" + k + "}", str(_js_arg(v)))
    return JSCode(code)
```


### ***6. Argument serialization (aux function)***

```Python
def _js_arg(arg):
    if isinstance(arg, JSCode):
        return str(arg)
    return json.dumps(arg)
```
This parses string, numbers and estructures to JSON but JS code keeps clean.

---

## Examples

```Python
document = JSCode("document")

expr1 = document.getElementById("user").value
# => document.getElementById('user').value

expr2 = JSCode("Math").pow(2, 3) + 10
# => (Math.pow(2,3) + 10)

expr3 = JSCode("fetch")("/api/data").await_()
# => await fetch('/api/data')

expr4 = JSCode("new Date")().call("getTime")  # o mejor new(JSCode("Date"))().call(...)
# => new Date().getTime()
```


## JSDO

JSDO its a object factory with local state

```Python
store = JSDO("Store", {"todos": []})
store.call("set", "todos", ["item1"])
```

```Python
self.js_obj = JSCode(object_name).new(arg)
```
