
def redirect(path: str):
    return 302, [("Location","/login")], ""


def Dom(query):
    return f"""document.querySelector(`{query}`).value"""
