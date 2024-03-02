import json
import uuid
import falco
import docker
import pymongo

from time import sleep
from typing import List
from docker.models import containers as con
from func_timeout import func_timeout, FunctionTimedOut


class Monitor:

    def __init__(self, container_id_list: List[str], unix_path="unix:///run/falco/falco.sock", debug=False):
        self.falco_client = falco.Client(endpoint=unix_path, output_format="json")
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
        self.events_database = self.mongo_client["falco_events_database"]
        self.events_collection = self.events_database["falco_events_collection"]
        self.events = []
        self.raw_events = []
        self.container_id_list = container_id_list
        self.debug = debug

    def _mon(self):
        for event in self.falco_client.get():
            if isinstance(event, str):
                self.raw_events.append(json.loads(event))

    def mon(self):
        try:
            func_timeout(10, self._mon)
        except FunctionTimedOut:
            pass
        for event in self.raw_events:
            if "output_fields" not in event.keys():
                continue
            if not isinstance(event["output_fields"], dict):
                continue
            if "container.id" not in event["output_fields"].keys():
                continue
            if "priority" not in event.keys():
                continue
            doc_id = self.events_collection.insert_one(event).inserted_id
            event["_id"] = f"{doc_id}"
            indexes = self.events_collection.index_information()
            index_key_name_list = set()
            [[index_key_name_list.add(index_key_name) for index_key_name, _ in indexes[index_name]["key"]] for index_name in indexes.keys()]
            if "time" not in index_key_name_list:
                self.events_collection.create_index("time", expireAfterSeconds=60*60*12)
            # FIXME: can not query by output_fields."container.id", dot in sub key name
            for hit_event in self.events_collection.find():
                hit_event["_id"] = str(hit_event["_id"])
                if hit_event["priority"].upper() not in ["EMERGENCY", "ALERT", "CRITICAL", "ERROR", "WARNING"]:
                    continue
                if hit_event["output_fields"]["container.id"] in self.container_id_list:
                    self.events.append(event)
        if self.debug:
            [print(json.dumps(event, indent=4)) for event in self.events]


class Container:

    def __init__(self, image_name: str, init_command="/bin/sh", debug=False, timeout=0):
        self.image_name = image_name
        self.init_command = init_command
        self.client = docker.from_env()
        self.debug = debug
        self.timeout = timeout
        self.container: con.Container = con.Container()
        self.container_name: str = ""

    def __enter__(self) -> con.Container:
        for container in self.client.containers.list(all=True):
            if container.name == self.container_name:
                container.stop()
                container.remove()
        self.container_name = self.image_name.replace(":", "-").replace("/", "-") + "-" + uuid.uuid1().hex
        self.container = self.client.containers.run(self.image_name, detach=True, tty=True,
                                                    name=self.container_name, command=self.init_command)
        if self.debug:
            print(self.container.status)
        return self.container

    def __exit__(self, exc_type, exc_val, exc_tb):
        sleep(self.timeout)
        self.container.stop()
        self.container.remove()
        self.client.close()


class Containers:

    def __init__(self, image_name_list: List[str], init_command="/bin/sh", debug=False, timeout=0):
        self.image_name_list = image_name_list
        self.init_command = init_command
        self.client = docker.from_env()
        self.debug = debug
        self.timeout = timeout
        self.container_list: List[con.Container] = []
        self.container_name_list: List[str] = []

    def __enter__(self) -> List[con.Container]:
        for image_name in self.image_name_list:
            container_name = image_name.replace(":", "-").replace("/", "-") + "-" + uuid.uuid1().hex
            self.container_name_list.append(container_name)
            container = self.client.containers.run(image_name, detach=True, tty=True, name=container_name)
            self.container_list.append(container)
        return self.container_list

    def __exit__(self, exc_type, exc_val, exc_tb):
        sleep(self.timeout)
        for container in self.container_list:
            container.stop()
            container.remove()
        self.client.close()
