#!/bin/sh

if [ "$(id -u)" -ne "0" ];then
  echo "have to install by root"
  exit
fi
falc
apt install libbpf-dev
curl -o install_falco -s https://falco.org/script/install
chmod +x install_falco
bash install_falco

cd ./deps/client-py/ || exit
if [ -f setup.py ];then
  python3 setup.py install
fi
cd ../../ || exit

if [ ! -d /run/falco/ ]; then
  mkdir -p /run/falco/
fi

cp -b falco.yaml /etc/falco/falco.yaml

pip install python-multipart fastapi uvicorn docker