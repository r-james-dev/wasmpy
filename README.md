# WasmPy
Interacting with WebAssembly code from python.

## Installing

Install the latest version:

```
$ python -m pip install wasmpy
```

Or build and install from source:

```
$ git clone https://github.com/r-james-dev/wasmpy.git
$ cd wasmpy
$ python setup.py install
```

If you wish to build without compiling the extensions for other python implementations, pass the `--no-compile` option to the `install` command.

# Usage
WasmPy defines import hooks to make the loading of WebAssembly binary files much easier! Just import the `WasmPy` library then you are good to go!
### Example:
If you have the following project setup:

```
|- my_wasm_file.wasm
|- main.py
```
Then in `main.py` the following code will load the WebAssembly file:
```py
import wasmpy
import my_wasm_file
```
The hook also allows importing the files from submodules, eg:
```
|- main.py
|- my_module
|  |- my_wasm_file.wasm
```
Then 
```py
import wasmpy
from my_module import my_wasm_file
```
