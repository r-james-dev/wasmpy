from .module import read_module
import os, sys, warnings


class WasmModule(object):
    """Object representing the module returned on import."""
    def __init__(self, file=None, loader=None, name=None):
        """Initialize common attributes of imported modules."""
        self.__file__ = file
        self._imports = {}
        self.__loader__ = loader
        self.__name__ = name
        with open(file, "rb") as fp:
            self._module = read_module(fp)

        # define exported functions as module methods
        for export in self._module["exports"]:
            if export["desc"][0] == "func":
                if export["name"].startswith("_"):
                    # do not create methods starting with an underscore "_"
                    warnings.warn(
                        f"exported function starts with \"_\", this function \
must be called with _func(\"{export['name']}\")", Warning
                    )
                    continue

                self.__setattr__(export["name"], export["desc"][1])

    def __call__(self, imports={}, run=True):
        """Can be called by user to provide imports and run a start method.
        imports is a dict object that provides namespaced functions
        """
        self._imports.update(imports)


class WebAssemblyBinaryLoader(object):
    """WebAssembly binary import hook.
    This hook is registered automatically with `import wasmpy`.
    After the initial import a WebAssembly binary format file (.wasm) can
    be loaded with the import statement eg:
    |- mymodule
    |  |- mymodule_2.wasm
    |
    |- mymodule_1.wasm
    |- example.py
    in example.py:
    ```
    import wasmpy
    import mymodule_1
    from mymodule import mymodule_2
    ``` Will load both binary files.
    """
    def find_module(self, fullname, path=None):
        fname = fullname.split(".")[-1] + ".wasm"
        if path is not None and len(path):
            for p in path:
                if os.path.isfile(os.path.join(p, fname)):
                    self.fname = os.path.join(p, fname)
                    return self

        elif len(fullname.split(".")) < 2 and os.path.isfile(fname):
            self.fname = os.path.abspath(fname)
            return self

    def load_module(self, fullname):
        if fullname in sys.modules:
            return

        mod = WasmModule(self.fname, self, fullname)
        sys.modules[fullname] = mod
        return mod
