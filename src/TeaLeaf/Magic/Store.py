from TeaLeaf.Html.Elements import html
import copy
from typing import Any, Iterable
import json
from uuid import uuid4
from TeaLeaf.Html.Component import Component
from TeaLeaf.Html.Elements import div
from TeaLeaf.Server.Server import HttpRequest, Server, ServerEvents, Session
from TeaLeaf.Magic.Common import JSDO
# import os


class SuperStore:
    _instance = None
    _initialized = False

    def __new__(cls, server=None):
        if cls._instance is None:
            cls._instance = super(SuperStore, cls).__new__(cls)
        return cls._instance


    def inject_stores(self, res_code, res_body, res_headers):
        if isinstance(res_body, html):
            for store_id in self.stores:
                store = self.stores[store_id]
                res_body.append(store.do.new())

    def __init__(self, server: Server | None = None):
        if not self._initialized:
            self.stores: dict[str, Store | AuthStore] = {}
            self._initialized = True
            if server:
                # self.server.add_path("/api/_store/{api_id}/{id}/*", self.process)
                server.add_path("/api/_store/{api_id}/*", self.process)
                server.registry_hook(ServerEvents.response, self.inject_stores)

            self._initialized = True

    def len(self):
        return len(self.stores)

    def add(self, id, store: Store | AuthStore):
        self.stores[id] = store

    def process(self,session: Session, req: HttpRequest, api_id):
        print(f"coll id: {id}")
        path = req.path.removeprefix(f"/api/_store/{api_id}/")

        store = self.stores.get(api_id)
        if store is None:
            return "Not found"

        if isinstance(store, AuthStore):
            store = store.auth(session)


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
    def __init__(self, default={}, subscribe=True):
        self._id = str(uuid4())
        self.data = copy.copy(default)
        self.do = JSDO("Store", self._id)
        if subscribe:
            SuperStore().add(self._id, self)


    def __get_pointer__(self, path):
        pointer = self.data
        for item in path:
            # if not isinstance(pointer, Iterable):
            #     return None
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
        if parent is None:
            return None
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
        if parent is None:
            return None
        # match type(parent[item]):
        #     case int:
        #         parent[item] = parent[item] + data
        #     case dict:
        #         parent[item] = parent[item] | data
        #     case _:
        parent[item] = data

        return data


    def read(self, path: str) -> Any:
        path_list = path.split("/") if path != "" else []
        pointer = self.__get_pointer__(path_list)
        return pointer


    def react(self,path) -> Component:
        return div(self.read(path)).classes(f"{self._id}{id}_react")

    def create(self, data, path):
        path = path.split("/") if path != "" else []
        parent = self.__get_pointer__(path[:-1])
        if parent is None:
            return None
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


class AuthStore():
    def __init__(self, auth, default={}) -> None:
        self._id = str(uuid4())
        self.default = copy.deepcopy(default)
        self.data: dict[str, Store] = {}
        self.auth_func = auth
        self.do = JSDO("Store", self._id)
        SuperStore().add(self._id, self)

    def auth(self, session: Session) -> Store:
        key = self.auth_func(session)
        if key not in self.data:
            self.data[key] = Store(default=copy.deepcopy(self.default),subscribe=False)
        return self.data[key]
