FROM fedora:29
LABEL maintainer "Sayan Chowdhury <gmail@yudocaa.in>"

WORKDIR /src
RUN dnf -y install \
    vim \
    python3-pip \
    git-core \
    mantle \
    fedora-messaging \
    python3-fedfind

ENV FEDORA_MESSAGING_CONF=/etc/fedora-messaging/joystick.toml

RUN pip3 install joystick-py && \
    mkdir -p /etc/fedora-messaging
