#!/bin/sh

if [ "$(id -u)" -ne "0" ];then
  echo "have to start by root"
  exit
fi

falcoctl driver install --type=modern_ebpf --compile
systemctl start falco-modern-ebpf

uvicorn run:sandbox --host 0.0.0.0 --port 10080 --workers 4 &
