

def JS(code: str, **kargs) -> str:
    for k in kargs:
        code = code.replace(f"{{{k}}}", str(kargs[k]))
    return code
