import json
import os

_self_dir = os.path.dirname(__file__)
_default_config_path = os.path.join(_self_dir, "../configs/default.json")
config_path = os.getenv("CMD_SANDBOX_CONF_PATH", _default_config_path)
config_file_descriptor = open(config_path, "rb")
docker_images: dict[str, list[str]] = json.load(config_file_descriptor)
config_file_descriptor.close()

image_list = []
[[image_list.append(f"{image_name}:{tag}") for tag in docker_images[image_name]] for image_name in docker_images.keys()]
