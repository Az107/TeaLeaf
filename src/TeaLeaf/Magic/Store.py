import json
from uuid import uuid4
from TeaLeaf.Html.Elements import div
from TeaLeaf.Server.Server import HttpRequest, Server
from TeaLeaf.Magic.Common import JSDO
# import os


class SuperStore:
    _instance = None
    _initialized = False

    def __new__(cls, server=None):
        if cls._instance is None:
            cls._instance = super(SuperStore, cls).__new__(cls)
        return cls._instance

    def __init__(self, server: Server | None = None):
        if not self._initialized:
            self.api_list: dict[str, "Store"] = {}
            self._initialized = True
            self.server = server
            if self.server:
                self.server.add_path("/api/_store/{api_id}/{id}", self.process)
                self.server.add_path("/api/_store/{api_id}", self.process)
            self._initialized = True

    def len(self):
        return len(self.api_list)

    def add(self, id, store: "Store"):
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
            return store.create(req.json() or req.body, id)
        elif req.method == "DELETE":
            return store.delete(id)
        elif req.method == "PATCH":
            return store.update(id, req.json() or req.body)
        else:
            return "404 Not Found", "Not found"


class Store:
    def __init__(self) -> None:
        self._id = str(uuid4())
        self.data = {}
        self.do = JSDO("Store", self._id)
        SuperStore().add(self._id, self)

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

    def update(self, id, data):
        if id not in self.data:
            return None
        col = self.data[id]
        if type(col) is list:
                if type(data) is dict and "id" in data:
                    for idx,item in enumerate(col):
                        if item["id"] == data["id"]:
                            col[idx] = data
                else:
                    return None

        else:
            print(f"COL type: {type(col)}")
            self.data[id] += data
        return str(data)

    def read(self, id):
        return self.data.get(id, "Key not found")


    def react(self,id):
        return div(self.read(id)).classes(f"{self._id}{id}_react")

    def create(self, data, id=None):
        if id is None:
            id = str(uuid4())

        if id in self.data and type(self.data[id]) is list:
            print(type(data))
            if type(data) is dict:
                data["id"] = data.get("id") or str(uuid4())

            self.data[id].append(data)
        else:
            self.data[id] = data
        return self.data[id]
