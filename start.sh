#!/bin/sh

if [ "$(id -u)" -ne "0" ];then
  echo "have to start by root"
  exit
fi

falcoctl driver install --type=modern_ebpf --compile
systemctl start falco-modern-bpf

uvicorn run:sandbox --host 127.0.0.1 --port 20000 --workers 2 &
