# Windows Subsystem for Linux

The tools we will be using are not supported for Windows. Windows users can install Windows Subsystem for Linux (WSL) to get the tools working. The instructions for installing WSL can be found here: [https://learn.microsoft.com/en-us/windows/wsl/install](https://learn.microsoft.com/en-us/windows/wsl/install)

## Enable WSL and Install Ubuntu 24.04

1. **Enable the Windows Subsystem for Linux**:
   - Open PowerShell as Administrator and run the following command:

     ```shell
     wsl --install
     ```

2. **Set WSL Version to 2** (if not already set):
   - In PowerShell, execute:

     ```shell
     wsl --set-default-version 2
     ```

   - This sets WSL 2 as the default version for any newly installed distributions.

3. **Install Ubuntu 24.04**:
   - Open Microsoft Store and search for "Ubuntu 24.04".
   - Click on "Get" or "Install" to download and install it.

4. **Initialize Ubuntu 24.04**:
   - Once installed, launch Ubuntu 24.04 from the Start menu.
   - Follow the on-screen instructions to complete the setup, which includes creating a user account.

Once WSL and Ubuntu 24.04 are installed, you can follow the rest of the instructions from the WSL terminal.
