from typing import List
from fastapi import APIRouter, Form

from ..core import Monitor, Containers, Container
from ..globals import image_list

executor = APIRouter()


@executor.post("/command/image")
def execute_command_in_image(cmd: str = Form(), image: str = Form(), init_cmd: str = Form()):
    container_id_list = []
    if image in image_list:
        with Container(image_name=image, init_command=init_cmd) as container:
            container.exec_run(cmd)
            container_id_list.append(container.id[:12])
        monitor = Monitor(container_id_list)
        monitor.mon()
        return monitor.events
    else:
        with Containers(image_name_list=image_list, init_command=init_cmd) as container_list:
            for container in container_list:
                container_id_list.append(container.id[:12])
                container.exec_run(cmd)
        monitor = Monitor(container_id_list)
        monitor.mon()
        return monitor.events


@executor.post("/command/images")
def execute_command_in_images(cmd: str = Form(), images: List[str] = Form(), init_cmd: str = Form()):
    container_id_list = []
    if len(images) > 0:
        image_name_list = list(set(images) & set(image_list))
        if len(image_name_list) == 0:
            image_name_list = image_list
    else:
        image_name_list = image_list
    with Containers(image_name_list=image_name_list, init_command=init_cmd) as container_list:
        for container in container_list:
            container_id_list.append(container.id[:12])
            container.exec_run(cmd)
    monitor = Monitor(container_id_list)
    monitor.mon()
    return monitor.events
