from .sections import *
import io

preamble = b"\0asm\x01\0\0\0"

# section ids
# 0 = custom section
# other ids (starting from 1) map to those in empty_module_lists
sects = [i for j in range(1, 12) for i in (0, j)] + [0]

empty_module_lists = [
    "types",
    "tables",
    "mems",
    "globals",
    "elem",
    "data",
    "imports",
    "exports",
]


def read_module(buffer):
    assert preamble == buffer.read(8), "Invalid magic number or version."

    module = {
        "custom": [], "types": [], "tables": [], "mems": [], "globals": []
    }
    typeidx = None
    code = []

    # index offsets
    func_off = tabl_off = mems_off = glob_off = 0

    # attempt to read sections
    upto = 0
    try:
        while upto < 23:
            id = buffer.read(1)[0]
            assert id < 12

            length = read_uint(buffer, 32)
            actual_len = length

            while sects[upto] != id:
                upto += 1
                if upto == 22:
                    break

            if sects[upto] != id:
                break

            if not id:
                 module["custom"].append(read_customsec(buffer, length))

            if id == 1:
                module["types"], actual_len = read_typesec(buffer)

            if id == 2:
                (
                    module["imports"],
                    func_off,
                    tabl_off,
                    mems_off,
                    glob_off,
                    actual_len
                ) = read_importsec(buffer, module["types"])

            if id == 3:
                typeidx, actual_len = read_funcsec(buffer)

            if id == 4:
                module["tables"], actual_len = read_tablesec(buffer)

            if id == 5:
                module["mems"], actual_len = read_memsec(buffer)

            if id == 6:
                module["globals"], actual_len = read_globalsec(buffer)

            if id == 7:
                module["exports"], actual_len = read_exportsec(
                    buffer, module["tables"], module["mems"],
                    module["globals"], tabl_off, mems_off, glob_off
                )

            if id == 8:
                module["start"], actual_len = read_startsec(buffer)

            if id == 9:
                module["elem"], actual_len = read_elemsec(buffer)

            if id == 10:
                code, actual_len = read_codesec(buffer)

            if id == 11:
                module["data"], actual_len = read_datasec(buffer)

            assert actual_len == length

    except IndexError:
        pass

    # map function signatures to the respective functions
    module["funcs"] = [
        [module["types"][typeidx[i]], t, e] for i, (t, e) in enumerate(code)
    ]

    # The meta section is a special custom section with the name: "name"
    # containg ids from the text format which is used in function signatures
    # https://www.w3.org/TR/wasm-core-1/#name-section%E2%91%A0
    meta_module_name = meta_function_names = meta_local_names = replace = None
    for secidx, section in enumerate(module["custom"]):
        if section[0] == "name":
            if section[1]:
                data = io.BytesIO(section[1])
                try:
                    assert not data.read(1)[0]
                    length = read_uint(data, 32)
                    start = data.tell()
                    meta_module_name = read_name(data)
                    assert data.tell() - start == length

                except AssertionError:
                    pass

                except (IndexError, TypeError):
                    continue

                try:
                    assert data.read(1)[0] == 1
                    length = read_uint(data, 32)
                    start = data.tell()
                    meta_function_names = []
                    for _ in range(get_vec_len(data)):
                        meta_function_names.append(
                            # function index and name
                            [read_uint(data, 32), read_name(data)]
                        )

                except AssertionError:
                    pass

                except (IndexError, TypeError):
                    continue

                try:
                    assert data.read(1)[0] == 2
                    length = read_uint(data, 32)
                    start = data.tell()
                    meta_local_names = []
                    for _ in range(get_vec_len(data)):
                        indirectnameassoc = [read_uint(data, 32), []]
                        for _ in range(get_vec_len(data)):
                            indirectnameassoc[1].append(
                                [read_uint(data, 32), read_name(data)]
                            )

                        meta_local_names.append(indirectnameassoc)

                except (AssertionError, IndexError, TypeError):
                    continue

                replace = secidx
                break  # ignore any repeated "name" sections

    if replace is not None:
        # remove parsed "name" section from custom modules
        module["custom"].pop(replace)

    module["meta"] = [meta_module_name, meta_function_names, meta_local_names]

    for section in empty_module_lists:
        if section not in module.keys():
            module[section] = ()

    if "start" not in module.keys():
        module["start"] = None

    return module
