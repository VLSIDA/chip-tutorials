# Virtual Environment
Python virtual environment is a Python package management system for your projects. It lets you
retain different versions of Python packages for your projects. This is done by creating project
directories where the packages will be installed locally instead of in your system.

Some Linux distributions now disallow the use of `pip` for installing packages to your system.
Meaning you need to either install them using your system's package manager, or create a Virtual
Environment.

To craete a virtual environment, create a directory for your project:
```bash
mkdir my_project
```
Next go into the directory and create the virtual environment:
```bash
cd my_project
python -m venv .venv
```
This will create the `.venv` directory where the virtual environment will reside. Note that
directories that start with the `.` character are hidden by default. For example you will need to add
the `-a` flag to `ls` to be able to see it.

Once the virtual environment has been created, you can activate it with:
```bash
source .venv/bin/activate
```
Once active, packages and binaries in this environment will be preferred over the ones in your
system. You will need to run this command everytime you open a new terminal and want to use the
packages in there.

Now with the virtual environment active, you can install your packages with:
```bash
python -m pip install <package name>
```

