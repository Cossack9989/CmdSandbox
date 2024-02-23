# CmdSandbox

- `/deps/client-py` is from [Falco python SDK](https://github.com/falcosecurity/client-py), which has been archived.

## install

- `docker` is a must
- execute `install.sh`

## start

- execute `start.sh`

## usage

- `curl -X POST http://localhost:10080/api/v1/command -d "cmd=/bin/bash&image=debian:stretch"`