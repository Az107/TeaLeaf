

def JS(code: str, file: str|None=None, **kargs) -> str:
    _code = ""
    if file is not None:
        f = open(file, "r")
        _code = f.read()
    for k in kargs:
        code = code.replace(f"{{{k}}}", str(kargs[k]))
    _code += code
    return _code
