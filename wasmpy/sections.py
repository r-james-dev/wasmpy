from .types import (
    read_functype,
    read_globaltype,
    read_memtype,
    read_tabletype,
    read_valtype,
)
from .values import get_vec_len, read_name, read_uint
from .instructions import read_expr


def read_customsec(buffer: object, length: int) -> None:
    """Read a custom section from buffer."""
    # Does not return anything as custom sections are dropped.
    # https://www.w3.org/TR/wasm-core-1/#custom-section%E2%91%A0
    buffer.read(length)


def read_typesec(buffer: object) -> tuple:
    """Read a type section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#type-section%E2%91%A0
    return tuple(read_functype(buffer) for _ in range(get_vec_len(buffer)))


def read_importsec(buffer: object) -> tuple:
    """Read an import section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#import-section%E2%91%A0
    im = ()
    try:
        for _ in range(get_vec_len(buffer)):
            import_ = {"module": read_name(buffer), "name": read_name(buffer)}
            flag = buffer.read(1)[0]
            assert flag in range(4)
            if not flag:
                import_["desc"] = ("func", read_uint(buffer, 32))

            elif flag == 1:
                import_["desc"] = ("table", read_tabletype(buffer))

            elif flag == 2:
                import_["desc"] = ("mem", read_memtype(buffer))

            elif flag == 3:
                import_["desc"] = ("global", read_globaltype(buffer))

            im += (import_,)

    except (IndexError, AssertionError):
        raise TypeError("Invalid import section.")

    return im


def read_funcsec(buffer: object) -> tuple:
    """Read a function section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#function-section%E2%91%A0
    return tuple(read_uint(buffer, 32) for _ in range(get_vec_len(buffer)))


def read_tablesec(buffer: object) -> tuple:
    """Read a table section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#table-section%E2%91%A0
    return tuple({"type": read_tabletype(buffer)} for _ in range(get_vec_len(buffer)))


def read_memsec(buffer: object) -> tuple:
    """Read a memory section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#memory-section%E2%91%A0
    return tuple({"type": read_memtype(buffer)} for _ in range(get_vec_len(buffer)))


def read_globalsec(buffer: object) -> tuple:
    """Read a global section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#global-section%E2%91%A0
    return tuple(
        {"gt": read_globaltype(buffer), "e": read_expr(buffer)}
        for _ in range(get_vec_len(buffer))
    )


def read_exportsec(buffer: object) -> tuple:
    """Read an export section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#export-section%E2%91%A0
    ex = ()
    for _ in range(get_vec_len(buffer)):
        export = {"name": read_name(buffer)}
        desc = buffer.read(1)[0]
        assert desc in range(4)
        if not desc:
            export["desc"] = "func", read_uint(buffer, 32)

        if desc == 1:
            export["desc"] = "table", read_uint(buffer, 32)

        if desc == 2:
            export["desc"] = "mem", read_uint(buffer, 32)

        if desc == 3:
            export["desc"] = "global", read_uint(buffer, 32)

        ex += (export,)

    return ex


def read_startsec(buffer: object) -> dict:
    """Read a start section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#start-section%E2%91%A0
    return {"func": read_uint(buffer, 32)}


def read_elemsec(buffer: object) -> tuple:
    """Read an element section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#element-section%E2%91%A0
    seg = ()
    for _ in range(get_vec_len(buffer)):
        seg += (
            {
                "table": read_uint(buffer, 32),
                "offset": read_expr(buffer),
                "init": tuple(
                    read_uint(buffer, 32) for _ in range(get_vec_len(buffer))
                ),
            },
        )

    return seg


def read_codesec(buffer: object) -> tuple:
    """Read a code section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#code-section%E2%91%A0
    code = ()
    try:
        for _ in range(get_vec_len(buffer)):
            size = read_uint(buffer, 32)
            start = buffer.tell()

            t = ()
            for _ in range(get_vec_len(buffer)):
                n = read_uint(buffer, 32)
                t += ((read_valtype(buffer),),)

            concat_t = ()
            for locals in t:
                concat_t += locals

            code += ((concat_t, read_expr(buffer)),)
            end = buffer.tell()
            assert size == end - start

    except AssertionError:
        raise TypeError("Invalid code section.")

    return code


def read_datasec(buffer: object) -> tuple:
    """Read a data section from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#data-section%E2%91%A0
    return tuple(
        {
            "data": read_uint(buffer, 32),
            "offset": read_expr(buffer),
            "init": tuple(buffer.read(1)[0] for _ in range(get_vec_len(buffer))),
        }
        for _ in range(get_vec_len(buffer))
    )
