FROM nvidia/cuda:12.0.0-base-ubuntu22.04


ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#lsFROM python:3.11
# add user
ARG USERNAME=user
ARG GROUPNAME=user
ARG UID=1000
ARG GID=1000
ARG PASSWORD=user
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID -G sudo $USERNAME && \
    echo $USERNAME:$PASSWORD | chpasswd && \
    echo "$USERNAME   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
WORKDIR /home/work


RUN apt update && apt install vim wget -y

# Step1: python3.9 install
RUN apt update -y && apt-get  update -y && \
apt install software-properties-common -y && \
add-apt-repository ppa:deadsnakes/ppa && \ 
apt install python3.9 -y && \
alias python=python3.9

# Step2: poetry config
#env PATH $PATH:$WORKING_DIR/.local/bin
ENV POETRY_HOME=/opt/poetry
ENV PATH $PATH:$WORKING_DIR/.local/bin
RUN apt install curl -y && \
mkdir /opt/poetry/bin -p && \
apt install python3.9-distutils -y && \
curl -sSL https://install.python-poetry.org | python3.9 -  && \
cd /usr/local/bin && ln -s /opt/poetry/bin/poetry &&\
poetry config --local virtualenvs.in-project true

#RUN apt install build-essential
#USER $USERNAME
