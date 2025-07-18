# Devcontainer God

This Project is to make a template which can easily generate any and all kind of devcontainers easily.

## Features

| SL no. | Features | Description | Supported OS |
| --- | --- | --- | --- |
| 1. | Waypipe | Forward container windows to host wayland | Linux(Wayland)|
| 2. | Devcontainer Features | Directly add devcontainer features from CLI  | All |
| 3. | Apt Packages | Search and Directly add Apt packages from CLI  | All |


## Usage
### 0. Requirements
1. Docker
2. VSCode (or devcontainer-cli)
3. Python3
4. Make
### 1. Setup:
1. run 
    ```sh
    make conf-container
    ```
    and follow the steps
### 2. Connect
 - For VSCode: `crtl + shift + p` and select `Rebuild and Reopen in Container`
 - For devcontainer-cli : Check Docs
 - for Connecting to Running container easily -