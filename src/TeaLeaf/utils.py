
def redirect(path: str):
    return "302 Found", [("Location", path)], ""
