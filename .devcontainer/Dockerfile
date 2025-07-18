ARG BASE_IMAGE=mcr.microsoft.com/devcontainers/base:debian
FROM ${BASE_IMAGE}


# Install waypipe and basic tools
RUN apt-get update && \
    apt-get install -y waypipe xwayland thunar chromium

RUN mkdir -p /tmp/wayland-runtime && \
    chown vscode:vscode /tmp/wayland-runtime

USER vscode
WORKDIR /home/vscode
