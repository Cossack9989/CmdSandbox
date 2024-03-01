import docker

from fastapi import FastAPI
from contextlib import asynccontextmanager

from sandbox.globals import docker_images

from sandbox.api.watch import watcher
from sandbox.api.execute import executor


@asynccontextmanager
async def lifespan(_app: FastAPI):
    client = docker.from_env()
    for image_name in docker_images.keys():
        for tag in docker_images[image_name]:
            if len(client.images.list(filters={"reference": f"{image_name}:{tag}"})) == 0:
                client.images.pull(repository=image_name, tag=tag)
                print(f"Prepared {image_name}:{tag}")
    if len(client.containers.list(filters={"name": "CmdSandboxDb", "status": "running"}) + client.containers.list(filters={"name": "CmdSandboxDb", "status": "restarting"})) < 1:
        for container in client.containers.list(filters={"name": "CmdSandboxDb", "status": "exited"}) + client.containers.list(filters={"name": "CmdSandboxDb", "status": "paused"}):
            container.stop()
            container.remove()
        client.containers.run("mongo", detach=True, name="CmdSandboxDb", ports={"27017/tcp": ("127.0.0.1", 27017)}, volumes=["/opt/mongo:/data/db"])
    yield
    client.close()


sandbox = FastAPI(lifespan=lifespan)
sandbox.include_router(watcher, prefix="/api/v1")
sandbox.include_router(executor, prefix="/api/v1")
