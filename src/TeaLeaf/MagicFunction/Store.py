import json
from uuid import uuid4
from TeaLeaf.Server import HttpRequest, Server
from TeaLeaf.Html.JS import JS
import os


class SuperStore():
    _instance = None
    _initialized = False

    def __new__(cls, server=None):
        if cls._instance is None:
            cls._instance = super(SuperStore, cls).__new__(cls)
        return cls._instance

    def __init__(self, server: Server|None =None):
        if not self._initialized:
            self.api_list: dict[str, 'Store'] = {}
            self._initialized = True
            self.server = server
            if self.server:
                self.server.add_path("/api/_store/{api_id}/{id}",self.process)
                self.server.add_path("/api/_store/{api_id}",self.process)
            self._initialized = True

    def len(self):
        return len(self.api_list)

    def add(self, id, store: 'Store'):
        self.api_list[id] = store

    def process(self, req: HttpRequest, api_id, id=None):
        store = self.api_list.get(api_id)
        if store is None:
            return "Not found :C"

        if req.method == "GET":
            if id:
                return json.dumps(store.read(id))
            else:
                return store.list()
        elif req.method == "POST":
            return store.create(req.json() or req.body)
        elif req.method == "DELETE":
            return store.delete(id)
        elif req.method == "PATCH":
            return store.update(id,req.json() or req.body)
        else:
            return "404 Not Found", "Not found"


class Store():
    def __init__(self) -> None:
        self._id = str(uuid4())
        self.data = {}
        self.do = JSDO(self._id)
        SuperStore().add(self._id,self)


    def delete(self, id):
        if id in self.data:
            del self.data[id]
            return True
        return False

    def list(self):
        result = []
        for k in self.data:
            result.append(self.data[k])
        return json.dumps(result)

    def update(self,id,data):
        if id in self.data:
            if type(self.data[id]) is list:
                    self.data[id].append(data)
            else:
                self.data[id] = data

        return data

    def read(self,id):
        return self.data.get(id, "Key not found")

    def create(self,data,id=None):
        if id is None:
            id = str(uuid4())
        self.data[id] = data
        return id



class JSDO():
    def __init__(self, store_id):
        js_file = os.path.dirname(__file__) + "/Store.js"
        self.storeName = "store_" + str(uuid4())[:5]
        self.storeJS = JS(file=js_file, code=f"const {self.storeName} = new Store('{store_id}')")

    def js(self):
        return self.storeJS

    def Get(self, id):
        return f"{self.storeName}.get(`{id}`)"

    def Set(self, id, data):
        return f"{self.storeName}.set(`{id}`,`{data}`)"

    def Update(self, id, data):
        if type(data) is dict:
            data = json.dumps(data)
            data = '"{data}"'
        return f"""{self.storeName}.update(`{id}`,{data})"""
