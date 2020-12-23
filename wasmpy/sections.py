from .types import (
    read_functype,
    read_globaltype,
    read_memtype,
    read_tabletype,
    read_valtype,
)
from .values import get_vec_len, read_name, read_uint
from .instructions import read_expr


def read_customsec(buffer: object, length: int) -> tuple:
    """Read a custom section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#custom-section%E2%91%A0
    start = buffer.tell()
    name = read_name(buffer)
    bytes = buffer.read(length - (buffer.tell() - start))
    return name, bytes


def read_typesec(buffer: object) -> tuple:
    """Read a type section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#type-section%E2%91%A0
    start = buffer.tell()
    types = [read_functype(buffer) for _ in range(get_vec_len(buffer))]
    end = buffer.tell()
    return types, end - start


def read_importsec(buffer: object, types: list) -> tuple:
    """Read an import section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#import-section%E2%91%A0
    start = buffer.tell()
    im = []
    func_off = tabl_off = mems_off = glob_off = 0
    try:
        for _ in range(get_vec_len(buffer)):
            import_ = {"module": read_name(buffer), "name": read_name(buffer)}
            flag = buffer.read(1)[0]
            assert flag in range(4)
            if not flag:
                import_["desc"] = ("func", types[read_uint(buffer, 32)])
                func_off += 1

            elif flag == 1:
                import_["desc"] = ("table", read_tabletype(buffer))
                tabl_off += 1

            elif flag == 2:
                import_["desc"] = ("mem", read_memtype(buffer))
                mems_off += 1

            elif flag == 3:
                import_["desc"] = ("global", read_globaltype(buffer))
                glob_off += 1

            im.append(import_)

    except (IndexError, AssertionError):
        raise TypeError("Invalid import section.")

    end = buffer.tell()
    return im, func_off, tabl_off, mems_off, glob_off, end - start


def read_funcsec(buffer: object) -> tuple:
    """Read a function section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#function-section%E2%91%A0
    start = buffer.tell()
    funcindicies = [read_uint(buffer, 32) for _ in range(get_vec_len(buffer))]
    end = buffer.tell()
    return funcindicies, end - start


def read_tablesec(buffer: object) -> tuple:
    """Read a table section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#table-section%E2%91%A0
    start = buffer.tell()
    return [
        [read_tabletype(buffer)] for _ in range(get_vec_len(buffer))
    ], buffer.tell() - start


def read_memsec(buffer: object) -> tuple:
    """Read a memory section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#memory-section%E2%91%A0
    start = buffer.tell()
    return (
        [read_memtype(buffer)] for _ in range(get_vec_len(buffer))
    ), buffer.tell() - start


def read_globalsec(buffer: object) -> tuple:
    """Read a global section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#global-section%E2%91%A0
    start = buffer.tell()
    globals = [[read_globaltype(buffer), read_expr(buffer)]
               for _ in range(get_vec_len(buffer))]

    return globals, buffer.tell() - start


def read_exportsec(buffer: object, t, m, g, *offs) -> tuple:
    """Read an export section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#export-section%E2%91%A0
    start = buffer.tell()
    ex = []
    for _ in range(get_vec_len(buffer)):
        export = [read_name(buffer)]
        desc = buffer.read(1)[0]
        assert desc in range(4)
        idx = read_uint(buffer, 32)
        if not desc:
            export.append(["func", idx])

        if desc == 1:
            export.append(["table", idx])

        if desc == 2:
            export.append(["mem", idx])

        if desc == 3:
            export.append(["global", idx])

        ex.append(export)

    end = buffer.tell()
    return ex, end - start


def read_startsec(buffer: object) -> tuple:
    """Read a start section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#start-section%E2%91%A0
    start = buffer.tell()
    # section is just a function index
    funcidx = read_uint(buffer, 32)
    end = buffer.tell()
    return funcidx, end - start


def read_elemsec(buffer: object) -> tuple:
    """Read an element section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#element-section%E2%91%A0
    start = buffer.tell()
    seg = []
    for _ in range(get_vec_len(buffer)):
        seg.append([
            read_uint(buffer, 32),
            read_expr(buffer),
            [read_uint(buffer, 32) for _ in range(get_vec_len(buffer))]
        ])

    end = buffer.tell()
    return seg, end - start


def read_codesec(buffer: object) -> tuple:
    """Read a code section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#code-section%E2%91%A0
    section_start = buffer.tell()
    code = []
    try:
        for _ in range(get_vec_len(buffer)):
            size = read_uint(buffer, 32)
            start = buffer.tell()

            # read function locals
            t = []
            for _ in range(get_vec_len(buffer)):
                n = read_uint(buffer, 32)
                type = read_valtype(buffer)
                [t.append(type) for _ in range(n)]

            code.append([t, read_expr(buffer)])
            end = buffer.tell()
            assert size == end - start

    except AssertionError:
        raise TypeError("Invalid code section.")

    end = buffer.tell()
    return code, end - section_start


def read_datasec(buffer: object) -> tuple:
    """Read a data section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#data-section%E2%91%A0
    start = buffer.tell()
    seg = []
    for _ in range(get_vec_len(buffer)):
        seg.append([
            read_uint(buffer, 32),
            read_expr(buffer),
            [buffer.read(1)[0] for _ in range(get_vec_len(buffer))]
        ])

    end = buffer.tell()
    return seg, end - start
