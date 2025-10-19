
def redirect(path: str):
    return "302 Found", [("Location", path)], ""


def Dom(query):
    return f"""'document.querySelector(`{query}`).value'"""
