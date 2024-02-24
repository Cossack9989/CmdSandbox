# CmdSandbox

- `/deps/client-py` is from [Falco python SDK](https://github.com/falcosecurity/client-py), which has been archived.

## install

- `docker.service` on Linux is a must
- `install.sh`

## start

- `export CMD_SANDBOX_CONF_PATH=/path/to/your/config`
- `start.sh`

## usage

- ```
  curl -X 'POST' \
  'http://127.0.0.1:8080/api/v1/command/image' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"cmd": "/bin/bash", "image": "debian:buster", "init_cmd": "/bin/sh", "timeout": 0}'
```