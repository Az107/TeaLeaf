from typing import Iterable
import json
from uuid import uuid4
from TeaLeaf.Html.Component import Component
from TeaLeaf.Html.Elements import div
from TeaLeaf.Server.Server import HttpRequest, Server, Session
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
                # self.server.add_path("/api/_store/{api_id}/{id}/*", self.process)
                self.server.add_path("/api/_store/{api_id}/*", self.process)
            self._initialized = True

    def len(self):
        return len(self.api_list)

    def add(self, id, store: "Store"):
        self.api_list[id] = store

    def process(self,session: Session, req: HttpRequest, api_id):
        print(f"coll id: {id}")
        path = req.path.removeprefix(f"/api/_store/{api_id}/")

        store = self.api_list.get(api_id)
        if store is None:
            return "Not found :C"

        if req.method == "GET":
            return json.dumps(store.read(path))
        elif req.method == "POST":
            return json.dumps(store.create(req.json() or req.body, path))
        elif req.method == "DELETE":
            return json.dumps(store.delete(path))
        elif req.method == "PATCH":
            return json.dumps(store.update(path, req.json() or req.body))
        else:
            return "404 Not Found", "Not found"


class Store:
    def __init__(self) -> None:
        self._id = str(uuid4())
        self.data = {}
        self.do = JSDO("Store", self._id)
        SuperStore().add(self._id, self)


    def __get_pointer__(self, path):
        pointer = self.data
        for item in path:
            print(item)
            if not isinstance(pointer, Iterable):
                return None
            if type(pointer) is list:
                item = int(item)
                pointer = pointer[item]
            else:
                if item in pointer:
                    pointer = pointer[item]
                else:
                    return None
        return pointer

    def delete(self, path):
        path = path.split("/") if path != "" else []
        parent = self.__get_pointer__(path[:-1])
        item = path[-1]
        if type(parent) is list:
            del parent[int(item)]
            return True
        else:
            if item in parent:
                del parent[item]
                return True
            else:
                return False


    def update(self, path, data):
        path = path.split("/") if path != "" else []

        parent = self.__get_pointer__(path[:-1])
        item = path[-1]
        # match type(parent[item]):
        #     case int:
        #         parent[item] = parent[item] + data
        #     case dict:
        #         parent[item] = parent[item] | data
        #     case _:
        parent[item] = data

        return data


    def read(self, path: str) -> Any:
        path = path.split("/") if path != "" else []
        pointer = self.__get_pointer__(path)
        return pointer


    def react(self,path) -> Component:
        return div(self.read(path)).classes(f"{self._id}{id}_react")

    def create(self, data, path):
        path = path.split("/") if path != "" else []
        parent = self.__get_pointer__(path[:-1])
        item = path[-1]

        if item in parent:
            pointer = parent[item]
            if type(pointer) is dict:
                pointer = pointer | data
            elif type(pointer) is list:
                pointer.append(data)
            else:
                return None

        else:
            parent[item] = data

        return parent
