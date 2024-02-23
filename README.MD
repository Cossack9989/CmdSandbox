# CmdSandbox

- `/deps/client-py` is from [Falco python SDK](https://github.com/falcosecurity/client-py), which has been archived.

## install

- `docker` is a must
- execute `install.sh`

## start

- execute `start.sh`

## usage

- `export CMD_SANDBOX_CONF_PATH=/path/to/your/config` 
- `curl -X POST http://localhost:10080/api/v1/command/image -d "cmd=/bin/bash&image=debian:stretch&init_cmd=/bin/sh"`