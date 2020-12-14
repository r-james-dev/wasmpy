from .values import get_vec_len, read_sint, read_uint, read_f32, read_f64
from .types import read_valtype


def read_expr(buffer: object) -> tuple:
    """Read an expression from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#expressions%E2%91%A6
    in_ = ()
    instruction = read_instruction(buffer)
    while instruction != "end":
        in_ += (instruction,)
        instruction = read_instruction(buffer)

    return (in_, "end")


def read_memarg(buffer: object) -> dict:
    """Read a memory arg from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#binary-memarg
    a = read_uint(buffer, 32)
    o = read_uint(buffer, 32)
    return {"align": a, "offset": o}


def read_instruction(buffer: object) -> "str or tuple":
    """Read an instruction from buffer."""
    data = buffer.read(1)
    # 0x0B (end) and 0x05 (else) explicit instructions
    if data == b"\x0b":
        return "end"

    if data == b"\x05":
        return "else"

    # Control instructions
    # https://www.w3.org/TR/wasm-core-1/#control-instructions%E2%91%A6
    if data == b"\0":
        return "unreachable"

    if data == b"\x01":
        return "nop"

    if data == b"\x02":
        try:
            rt = read_valtype(buffer)

        except TypeError:
            buffer.seek(-1, 1)
            if buffer.read(1)[0] != 64:
                raise TypeError("Invalid blocktype.")

            rt = None

        in_ = []
        instruction = read_instruction(buffer)
        while instruction != "end":
            in_.append(instruction)
            instruction = read_instruction(buffer)

        return "block", rt, tuple(in_), "end"

    if data == b"\x03":
        try:
            rt = read_valtype(buffer)

        except TypeError:
            buffer.seek(-1, 1)
            if buffer.read(1)[0] != 64:
                raise TypeError("Invalid blocktype.")

            rt = None

        in_ = []
        instruction = read_instruction(buffer)
        while instruction != "end":
            in_.append(instruction)
            instruction = read_instruction(buffer)

        return "loop", rt, tuple(in_), "end"

    if data == b"\x04":
        try:
            rt = read_valtype(buffer)

        except TypeError:
            buffer.seek(-1, 1)
            if buffer.read(1)[0] != 64:
                raise TypeError("Invalid blocktype.")

            rt = None

        in1 = []
        instruction = read_instruction(buffer)
        while instruction not in ["end", "else"]:
            in1.append(instruction)
            instruction = read_instruction(buffer)

        in1 = tuple(in1)
        if instruction == "end":
            return "if", rt, in1, "else", (), "end"

        # "else"
        in2 = []
        instruction = read_instruction(buffer)
        while instruction != "end":
            in2.append(instruction)
            instruction = read_instruction(buffer)

        return "if", rt, in1, "else", tuple(in2), "end"

    if data == b"\x0c":
        return "br", read_uint(buffer, 32)

    if data == b"\x0d":
        return "br_if", read_uint(buffer, 32)

    if data == b"\x0e":
        l = [read_uint(buffer, 32) for _ in range(get_vec_len(buffer))]
        return "br_table", l, read_uint(buffer, 32)

    if data == b"\x0f":
        return "return"

    if data == b"\x10":
        return "call", read_uint(buffer, 32)

    if data == b"\x11":
        x = read_uint(buffer, 32)
        assert buffer.read(1) == b"\0", "Invalid instruction."
        return "call_indirect", x

    # Parametric instructions
    # https://www.w3.org/TR/wasm-core-1/#parametric-instructions%E2%91%A6
    if data == b"\x1a":
        return "drop"

    if data == b"\x1b":
        return "select"

    # Variable instructions
    # https://www.w3.org/TR/wasm-core-1/#variable-instructions%E2%91%A6
    if data == b"\x20":
        return "local.get", read_uint(buffer, 32)

    if data == b"\x21":
        return "local.set", read_uint(buffer, 32)

    if data == b"\x22":
        return "local.tee", read_uint(buffer, 32)

    if data == b"\x23":
        return "global.get", read_uint(buffer, 32)

    if data == b"\x24":
        return "global.set", read_uint(buffer, 32)

    # Memory instructions
    # https://www.w3.org/TR/wasm-core-1/#memory-instructions%E2%91%A6
    if data == b"\x28":
        return "i32.load", read_memarg(buffer)

    if data == b"\x29":
        return "i64.load", read_memarg(buffer)

    if data == b"\x2a":
        return "f32.load", read_memarg(buffer)

    if data == b"\x2b":
        return "f64.load", read_memarg(buffer)

    if data == b"\x2c":
        return "i32.load8_s", read_memarg(buffer)

    if data == b"\x2d":
        return "i32.load8_u", read_memarg(buffer)

    if data == b"\x2e":
        return "i32.load16_s", read_memarg(buffer)

    if data == b"\x2f":
        return "i32.load16_u", read_memarg(buffer)

    if data == b"\x30":
        return "i64.load8_s", read_memarg(buffer)

    if data == b"\x31":
        return "i64.load8_u", read_memarg(buffer)

    if data == b"\x32":
        return "i64.load16_s", read_memarg(buffer)

    if data == b"\x33":
        return "i64.load16_u", read_memarg(buffer)

    if data == b"\x34":
        return "i64.load32_s", read_memarg(buffer)

    if data == b"\x35":
        return "i64.load32_u", read_memarg(buffer)

    if data == b"\x36":
        return "i32.store", read_memarg(buffer)

    if data == b"\x37":
        return "i64.store", read_memarg(buffer)

    if data == b"\x38":
        return "f32.store", read_memarg(buffer)

    if data == b"\x39":
        return "f64.store", read_memarg(buffer)

    if data == b"\x3a":
        return "i32.store8", read_memarg(buffer)

    if data == b"\x3b":
        return "i32.store16", read_memarg(buffer)

    if data == b"\x3c":
        return "i64.store8", read_memarg(buffer)

    if data == b"\x3d":
        return "i64.store16", read_memarg(buffer)

    if data == b"\x3e":
        return "i64.store32", read_memarg(buffer)

    if data == b"\x3f":
        assert buffer.read(1) == b"\0"
        return "memory.size"

    if data == b"\x40":
        assert buffer.read(1) == b"\0"
        return "memory.grow"

    # Numeric instructions
    # https://www.w3.org/TR/wasm-core-1/#numeric-instructions%E2%91%A6
    if data == b"\x41":
        return "i32.const", read_sint(buffer, 32)

    if data == b"\x42":
        return "i64.const", read_sint(buffer, 64)

    if data == b"\x43":
        return "f32.const", read_f32(buffer)

    if data == b"\x44":
        return "f64.const", read_f64(buffer)

    if data == b"\x45":
        return "i32.eqz"

    if data == b"\x46":
        return "i32.eq"

    if data == b"\x47":
        return "i32.ne"

    if data == b"\x48":
        return "i32.lt_s"

    if data == b"\x49":
        return "i32.lt_u"

    if data == b"\x4a":
        return "i32.gt_s"

    if data == b"\x4b":
        return "i32.gt_u"

    if data == b"\x4c":
        return "i32.le_s"

    if data == b"\x4d":
        return "i32.le_u"

    if data == b"\x4e":
        return "i32.ge_s"

    if data == b"\x4f":
        return "i32.ge_u"

    if data == b"\x50":
        return "i64.eqz"

    if data == b"\x51":
        return "i64.eq"

    if data == b"\x52":
        return "i64.ne"

    if data == b"\x53":
        return "i64.lt_s"

    if data == b"\x54":
        return "i64.lt_u"

    if data == b"\x55":
        return "i64.gt_s"

    if data == b"\x56":
        return "i64.gt_u"

    if data == b"\x57":
        return "i64.le_s"

    if data == b"\x58":
        return "i64.le_u"

    if data == b"\x59":
        return "i64.ge_s"

    if data == b"\x5a":
        return "i64.ge_u"

    if data == b"\x5b":
        return "f32.eq"

    if data == b"\x5c":
        return "f32.ne"

    if data == b"\x5d":
        return "f32.lt"

    if data == b"\x5e":
        return "f32.gt"

    if data == b"\x5f":
        return "f32.le"

    if data == b"\x60":
        return "f32.ge"

    if data == b"\x61":
        return "f64.eq"

    if data == b"\x62":
        return "f64.ne"

    if data == b"\x63":
        return "f64.lt"

    if data == b"\x64":
        return "f64.gt"

    if data == b"\x65":
        return "f64.le"

    if data == b"\x66":
        return "f64.ge"

    if data == b"\x67":
        return "i32.clz"

    if data == b"\x68":
        return "i32.ctz"

    if data == b"\x69":
        return "i32.popcnt"

    if data == b"\x6a":
        return "i32.add"

    if data == b"\x6b":
        return "i32.sub"

    if data == b"\x6c":
        return "i32.mul"

    if data == b"\x6d":
        return "i32.div_s"

    if data == b"\x6e":
        return "i32.div_u"

    if data == b"\x6f":
        return "i32.rem_s"

    if data == b"\x70":
        return "i32.rem_u"

    if data == b"\x71":
        return "i32.and"

    if data == b"\x72":
        return "i32.or"

    if data == b"\x73":
        return "i32.xor"

    if data == b"\x74":
        return "i32.shl"

    if data == b"\x75":
        return "i32.shr_s"

    if data == b"\x76":
        return "i32.shr_u"

    if data == b"\x77":
        return "i32.rotl"

    if data == b"\x78":
        return "i32.rotr"

    if data == b"\x79":
        return "i64.clz"

    if data == b"\x7a":
        return "i64.ctz"

    if data == b"\x7b":
        return "i64.popcnt"

    if data == b"\x7c":
        return "i64.add"

    if data == b"\x7d":
        return "i64.sub"

    if data == b"\x7e":
        return "i64.mul"

    if data == b"\x7f":
        return "i64.div_s"

    if data == b"\x80":
        return "i64.div_u"

    if data == b"\x81":
        return "i64.rem_s"

    if data == b"\x82":
        return "i64.rem_u"

    if data == b"\x83":
        return "i64.and"

    if data == b"\x84":
        return "i64.or"

    if data == b"\x85":
        return "i64.xor"

    if data == b"\x86":
        return "i64.shl"

    if data == b"\x87":
        return "i64.shr_s"

    if data == b"\x88":
        return "i64.shr_u"

    if data == b"\x89":
        return "i64.rotl"

    if data == b"\x8a":
        return "i64.rotr"

    if data == b"\x8b":
        return "f32.abs"

    if data == b"\x8c":
        return "f32.neg"

    if data == b"\x8d":
        return "f32.ceil"

    if data == b"\x8e":
        return "f32.floor"

    if data == b"\x8f":
        return "f32.trunc"

    if data == b"\x90":
        return "f32.nearset"

    if data == b"\x91":
        return "f32.sqrt"

    if data == b"\x92":
        return "f32.add"

    if data == b"\x93":
        return "f32.sub"

    if data == b"\x94":
        return "f32.mul"

    if data == b"\x95":
        return "f32.div"

    if data == b"\x96":
        return "f32.min"

    if data == b"\x97":
        return "f32.max"

    if data == b"\x98":
        return "f32.copysign"

    if data == b"\x99":
        return "f64.abs"

    if data == b"\x9a":
        return "f64.neg"

    if data == b"\x9b":
        return "f64.ceil"

    if data == b"\x9c":
        return "f64.floor"

    if data == b"\x9d":
        return "f64.trunc"

    if data == b"\x9e":
        return "f64.nearset"

    if data == b"\x9f":
        return "f64.sqrt"

    if data == b"\xa0":
        return "f64.add"

    if data == b"\xa1":
        return "f64.sub"

    if data == b"\xa2":
        return "f64.mul"

    if data == b"\xa3":
        return "f64.div"

    if data == b"\xa4":
        return "f64.min"

    if data == b"\xa5":
        return "f64.max"

    if data == b"\xa6":
        return "f64.copysign"

    if data == b"\xa7":
        return "i32.wrap_i64"

    if data == b"\xa8":
        return "i32.trunc_f32_s"

    if data == b"\xa9":
        return "i32.trunc_f32_u"

    if data == b"\xaa":
        return "i32.trunc_f64_s"

    if data == b"\xab":
        return "i32.trunc_f64_u"

    if data == b"\xac":
        return "i64.extend_i32_s"

    if data == b"\xad":
        return "i64.extend_i32_u"

    if data == b"\xae":
        return "i64.trunc_f32_s"

    if data == b"\xaf":
        return "i64.trunc_f32_u"

    if data == b"\xb0":
        return "i64.trunc_f64_s"

    if data == b"\xb1":
        return "i64.trunc_f64_u"

    if data == b"\xb2":
        return "f32.convert_i32_s"

    if data == b"\xb3":
        return "f32.convert_i32_u"

    if data == b"\xb4":
        return "f32.convert_i64_s"

    if data == b"\xb5":
        return "f32.convert_i64_u"

    if data == b"\xb6":
        return "f32.demote_f64"

    if data == b"\xb7":
        return "f64.convert_i32_s"

    if data == b"\xb8":
        return "f64.convert_i32_u"

    if data == b"\xb9":
        return "f64.convert_i64_s"

    if data == b"\xba":
        return "f64.convert_i64_u"

    if data == b"\xbb":
        return "f64.promote_f32"

    if data == b"\xbc":
        return "i32.reinterpret_f32"

    if data == b"\xbd":
        return "i64.reinterpret_f64"

    if data == b"\xbe":
        return "f32.reinterpret_i32"

    if data == b"\xbf":
        return "f64.reinterpret_i64"

    raise TypeError("Invalid instruction type.")
