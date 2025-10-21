from TeaLeaf.Magic.Common import JSDO


class localState():
    def __init__(self, init_state):
        self.do = JSDO("LocalState",init_state)

    def js(self):
        return self.do.js()

    def get(self):
        return self.do.get()

    def set(self, data):
        return self.do.set(data)





def use_state(init_state):
    return localState(init_state)
