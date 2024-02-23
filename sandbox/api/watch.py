import docker
from fastapi import APIRouter


watcher = APIRouter()


@watcher.get("/ping")
async def ping():
    return "pong"


@watcher.get("/containers")
async def get_containers():
    client = docker.from_env()
    containers = [f"{container.name}:{container.id}" for container in client.containers.list()]
    client.close()
    return containers
