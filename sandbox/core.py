import json
import uuid
import falco
import docker

from time import sleep
from typing import List
from docker.models import containers as con
from func_timeout import func_timeout, FunctionTimedOut


class Monitor:

    def __init__(self, container_id_list: List[str], unix_path="unix:///run/falco/falco.sock", debug=False):
        self.client = falco.Client(endpoint=unix_path, output_format="json")
        self.events = []
        self.raw_events = []
        self.container_id_list = container_id_list
        self.debug = debug

    def _mon(self):
        for event in self.client.get():
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
            if event["priority"].upper() not in ["EMERGENCY", "ALERT", "CRITICAL", "ERROR", "WARNING"]:
                continue
            if event["output_fields"]["container.id"] in self.container_id_list:
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
