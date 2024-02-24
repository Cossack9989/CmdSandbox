from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..core import Monitor, Containers, Container
from ..globals import image_list

executor = APIRouter()


class ImageCommandRequest(BaseModel):
    cmd: str = Field(examples=["/bin/bash"])
    image: str = Field(examples=["debian:buster"])
    init_cmd: str = Field(default="/bin/sh", examples=["/bin/sh"])
    timeout: int = Field(default=0, examples=[0])


class ImagesCommandRequest(BaseModel):
    cmd: str = Field(examples=["/bin/bash"])
    images: List[str] = Field(examples=[["debian:buster", "debian:stretch"]])
    init_cmd: str = Field(default="/bin/sh", examples=["/bin/sh"])
    timeout: int = Field(default=0, examples=[0])


@executor.post("/command/image")
def execute_command_in_image(data: ImageCommandRequest):
    container_id_list = []
    if data.image in image_list:
        with Container(image_name=data.image, init_command=data.init_cmd) as container:
            container.exec_run(data.cmd)
            container_id_list.append(container.id[:12])
        monitor = Monitor(container_id_list)
        monitor.mon()
        return monitor.events
    else:
        with Containers(image_name_list=image_list, init_command=data.init_cmd, timeout=data.timeout) as container_list:
            for container in container_list:
                container_id_list.append(container.id[:12])
                container.exec_run(data.cmd)
        monitor = Monitor(container_id_list)
        monitor.mon()
        return monitor.events


@executor.post("/command/images")
def execute_command_in_images(data: ImagesCommandRequest):
    container_id_list = []
    if len(data.images) > 0:
        image_name_list = list(set(data.images) & set(image_list))
        if len(image_name_list) == 0:
            image_name_list = image_list
    else:
        image_name_list = image_list
    with Containers(image_name_list=image_name_list, init_command=data.init_cmd, timeout=data.timeout) as container_list:
        for container in container_list:
            container_id_list.append(container.id[:12])
            container.exec_run(data.cmd)
    monitor = Monitor(container_id_list)
    monitor.mon()
    return monitor.events
