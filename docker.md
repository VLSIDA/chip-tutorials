---
title: Docker
nav_order: 13
---

# Installing Docker

## Linux (Ubuntu)

To install Docker on Ubuntu, follow these steps:

1. **Update your existing list of packages and install prerequisites**:

   ```bash
   sudo apt update
   sudo apt install ca-certificates curl
   ```

2. **Add Docker's official GPG key** to `/etc/apt/keyrings/`:

   ```bash
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   ```

   Note: the older `apt-key add` flow is deprecated and removed on Ubuntu 22.04+. Use the `/etc/apt/keyrings/` approach above.

3. **Add the Docker APT repository**:

   ```bash
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
     $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

4. **Update the package database with the Docker packages from the newly added repo**:

   ```bash
   sudo apt update
   ```

5. **Install Docker**:

   ```bash
   sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

6. **Check that Docker is running**:

   ```bash
   sudo systemctl status docker
   ```

7. **(Optional) Manage Docker as a non-root user**:

   ```bash
   sudo usermod -aG docker ${USER}
   ```

   Log out and back in for the group change to take effect.

## Windows

To install Docker Desktop on Windows, follow these steps:

1. **Download Docker Desktop for Windows** from the [official Docker website](https://desktop.docker.com).

2. **Run the Docker Desktop Installer**, which you just downloaded, and follow the installation instructions.

3. **Enable WSL 2** if it is not already enabled:
   - Open PowerShell as Administrator and run:

     ```powershell
     wsl --install
     ```

4. **Start Docker Desktop** from the Start menu.

5. **Follow the guided onboarding** to build your first container.

6. **Verify installation**:
   - Open PowerShell and run:

     ```powershell
     docker --version
     ```

## MacOS

To install Docker Desktop on MacOS, follow these steps:

1. **Download Docker Desktop for Mac** from the [official Docker website](https://desktop.docker.com).

2. **Open the downloaded Docker.dmg file** and drag Docker to Applications.

3. **Run Docker Desktop** from the Applications folder.

4. **Follow the installation process** and authorize the installer with your system password.

5. **Verify installation**:
   - Open Terminal and run:

     ```bash
     docker --version
     ```

6. **Start using Docker** from the Docker menu in the top status bar.

This will set up Docker Desktop on all three platforms: Ubuntu, Windows, and MacOS.

## Check Docker

You can check that Docker is working by running:

```bash
$ docker run -it hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
e6590344b1a5: Pull complete
Digest: sha256:0b6a027b5cf322f09f6706c754e086a232ec1ddba835c8a15c6cb74ef0d43c29
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/

```
