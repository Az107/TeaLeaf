
from TeaLeaf.Html.Component import Component


class Interface:

    def __init__(self) -> None:
        pass

    def serve(self, payload: str | Component):
        pass
