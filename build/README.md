
# Build Documentation

## cx_freeze instructions

### Get cx_freeze

To build cross platform images we use the [cx_freeze](http://cx-freeze.sourceforge.net/) tool.

To install cx_freeze you can [download](http://cx-freeze.sourceforge.net/index.html) it or [build it](http://cx-freeze.sourceforge.net/index.html) from source using the README provided upon downloading it.

#### Fixing Build Errors

  * I can't build cx_freeze.

If you encounter an error like the one below it could be that the version of python you are using was compiled without a shared library. 

```
/usr/bin/ld: cannot find -lpython3.3
collect2: error: ld returned 1 exit status
error: command 'gcc' failed with exit status 1
```

You will want to reconfigure & install your version of python using the following option.

```
./configure --enable-shared
```

  * python3.3 does not work when I re-compile it with enable-shared
  
If you are using python3.3, which is the version of python being used for this project you may have some problems with runing python3.3 after compiling it with enable-shared. The solution to this is to edit /etc/ld.so.conf or create something in /etc/ld.so.conf.d/ to add /usr/local/lib and /usr/local/lib64. Then run ldconfig.

### Preparing the project for building

#### Adding Extensions to Builds

Extensions are built-in to the Commotion client by adding them to the extension folder and then adding that folder name to the core_extensions list in the setup.py.

```
core_extensions = ["config_editor", "main_window", "your_extension_name"]
```

### Creating an executable

Linux:
  * go to the root directory of the project.
  * type ```make linux```
  * The executables folder will be created in the build directory.
  * run the ```Commotion``` executable in the executables folder.
  