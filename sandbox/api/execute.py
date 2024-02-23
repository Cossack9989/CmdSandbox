from typing import Union, List
from fastapi import APIRouter, Form

from ..core import Monitor, Containers, Container
from ..globals import linux_images

executor = APIRouter()


@executor.post("/command")
def execute_command(cmd: str = Form(), image: Union[str, List[str], None] = Form()):
    container_id_list = []
    if isinstance(image, list) or image is None:
        if isinstance(image, list):
            image_name_list = list(set(image) & set(linux_images))
            if len(image_name_list) == 0:
                image_name_list = linux_images
        else:
            image_name_list = linux_images

        with Containers(image_name_list=image_name_list) as container_list:
            for container in container_list:
                container_id_list.append(container.id[:12])
                container.exec_run(cmd)
        monitor = Monitor(container_id_list)
        monitor.mon()
        return monitor.events
    else:
        if image in linux_images:
            with Container(image_name=image) as container:
                container.exec_run(cmd)
                container_id_list.append(container.id[:12])
            monitor = Monitor(container_id_list)
            monitor.mon()
            return monitor.events
        else:
            with Containers(image_name_list=linux_images) as container_list:
                for container in container_list:
                    container_id_list.append(container.id[:12])
                    container.exec_run(cmd)
            monitor = Monitor(container_id_list)
            monitor.mon()
            return monitor.events
