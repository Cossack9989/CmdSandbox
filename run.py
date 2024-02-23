import docker

from fastapi import FastAPI
from contextlib import asynccontextmanager

from sandbox.globals import debian_releases

from sandbox.api.watch import watcher
from sandbox.api.execute import executor


@asynccontextmanager
async def lifespan(_app: FastAPI):
    client = docker.from_env()
    for release in debian_releases:
        if len(client.images.list(filters={"reference": f"debian:{release}"})) == 0:
            client.images.pull(repository="debian", tag=release)
    yield
    client.close()


sandbox = FastAPI(lifespan=lifespan)
sandbox.include_router(watcher, prefix="/api/v1")
sandbox.include_router(executor, prefix="/api/v1")
