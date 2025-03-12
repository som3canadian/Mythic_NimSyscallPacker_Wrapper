FROM ubuntu:jammy

ARG CA_CERTIFICATE
ARG NPM_REGISTRY
ARG PYPI_INDEX
ARG PYPI_INDEX_URL
ARG DOCKER_REGISTRY_MIRROR
ARG HTTP_PROXY
ARG HTTPS_PROXY

RUN apt update && apt install -y python3 python3-pip mingw-w64=8.0.0-1 xz-utils git osslsigncode tar zip openssl gcc make wget curl xml2 pkg-config automake build-essential perl libtool autotools-dev g++ ruby libssl-dev --no-install-recommends && rm -rf /var/lib/apt/lists/* && apt-get clean

COPY [".docker/requirements.txt", "requirements.txt"]
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# FROM python:3.11-slim-bullseye

RUN mkdir /Mythic
WORKDIR /Mythic/

COPY [".", "."]

RUN wget https://nim-lang.org/choosenim/init.sh && CHOOSENIM_CHOOSE_VERSION=1.6.8 bash init.sh -y
ENV PATH=/root/.nimble/bin:$PATH
RUN nimble install -y nimcrypto docopt ptr_math winim https://github.com/S3cur3Th1sSh1t/nim-strenc/

RUN cd /opt/ && git clone https://github.com/S4ntiagoP/donut --branch syscalls && cd donut && make && cd
ENV PATH=/opt/donut:$PATH

# copy folder from mythic_base to this image
WORKDIR /Mythic/agent_code/NimSyscallPacker
RUN nim c -d:noRES NimSyscallLoader.nim
RUN mkdir /shared

WORKDIR /Mythic/
# RUN ls -la

CMD ["python3", "main.py"]