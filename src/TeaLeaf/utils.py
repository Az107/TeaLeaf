from TeaLeaf.Html.Elements import script
def redirect(path: str):
    return "302 Found", [("Location", path)], ""


def enable_reactivity():
    return script("", src="_engine/worker.js")
