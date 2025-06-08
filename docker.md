# Installing Docker

## Linux (Ubuntu)

To install Docker on Ubuntu, follow these steps:

1. **Update your existing list of packages**:

   ```bash
   sudo apt update
   ```

2. **Install packages to allow apt to use a repository over HTTPS**:

   ```bash
   sudo apt install apt-transport-https ca-certificates curl software-properties-common
   ```

3. **Add Docker’s official GPG key**:

   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   ```

4. **Add the Docker APT repository**:

   ```bash
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   ```

5. **Update the package database with the Docker packages from the newly added repo**:

   ```bash
   sudo apt update
   ```

6. **Make sure you are about to install from the Docker repo instead of the default Ubuntu repo**:

   ```bash
   apt-cache policy docker-ce
   ```

7. **Install Docker**:

   ```bash
   sudo apt install docker-ce
   ```

8. **Check that Docker is running**:

   ```bash
   sudo systemctl status docker
   ```

9. **(Optional) Manage Docker as a non-root user**:

   ```bash
   sudo usermod -aG docker ${USER}
   ```

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
