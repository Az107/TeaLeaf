import json
from uuid import uuid4
from TeaLeaf.Server import HttpRequest, Server

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


    def add(self, id, store: 'Store'):
        self.api_list[id] = store

    def process(self, req: HttpRequest, api_id, id=None):
        print(self.api_list)
        store = self.api_list.get(api_id)
        if store is None:
            return "Not found :C"

        if req.method == "GET":
            if id:
                return store.read(id)
            else:
                return store.list()
        elif req.method == "POST":
            return store.create(req.body)
        elif req.method == "DELETE":
            return store.delete(id)
        elif req.method == "PUT":
            return store.update(id,req.body)
        else:
            return "404 Not Found", "Not found"


class Store():
    def __init__(self) -> None:
        self._id = str(uuid4())
        self.data = {}
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
            self.data[id] = data
        return data

    def read(self,id):
        return str(self.data.get(id, "Key not found"))

    def create(self,data,id=None):
        if id == None:
            id = str(uuid4())
        self.data[id] = data
        return id
