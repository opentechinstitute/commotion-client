# Build Documentation

## Build Folder Structure

build/
  ├── exe.<platform>-<python version>/
  ├── README.md <- The file you are reading.
  ├── resources/
  └── scripts/
         └──compile_ui.py



### exe.<platform>-<python version>/

A set of folders containing all final bundled executables created by cx_freeze in the build process.

Built for a  64 bit linux machine with python3.3 this will look like:

```exe.linux-x86_64-3.3```

These folders are not tracked by version control

### scripts/

All scripts used by the build process

### resources/

All resources created during the build process.

This includes:
  * All bundled extensions
  * Compiled assets file ( commotion_assets_rc.py )

This folder is not tracked by version control

	 
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

### The setup script

The setup.py script in the root directory is not a traditional distutils setup.py script. It is actually a customized cx_freeze setup script. You can find documentation for it on the [cx_freeze docs site](http://cx-freeze.readthedocs.org/en/latest/distutils.html) and a searchable mailing list on [sourceforge](http://sourceforge.net/p/cx-freeze/mailman/cx-freeze-users/).