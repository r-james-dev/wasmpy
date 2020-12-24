from .module import read_module
import os, sys, types, warnings


class WasmModule(types.ModuleType):
    """Module subclass which is callable to allow start function execution."""
    def __init__(self, file=None, loader=None, name=None):
        """Initialize common attributes of imported modules."""
        self.__file__ = file
        self._imports = {}
        self.__loader__ = loader
        self.__name__ = name
        with open(file, "rb") as fp:
            self._module = read_module(fp)

        # define exported functions as module methods
        warned = False
        for export in self._module["exports"]:
            if export[1][0] == "func":
                if export[0].startswith("_"):
                    if "WASMPY_NO_WARN" not in os.environ:
                        # do not create methods starting with an underscore "_"
                        warned = True
                        warnings.warn(
                            "exported function starts with \"_\", this "
                            "function must be called with _func(\""
                            f"{export[0]}\")", Warning
                        )
                        continue

                self.__setattr__(export[0], export[1][1])

        if warned:
            warnings.warn(
                "wasmpy import warnings can be turned of by setting the "
                "WASMPY_NO_WARN environment variable", Warning
            )

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
