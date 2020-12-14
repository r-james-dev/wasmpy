import math, struct

f32 = struct.Struct("<f")
f64 = struct.Struct("<d")


def get_vec_len(buffer):
    """Return the length of a vector consumed from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#vectors%E2%91%A2
    return read_uint(buffer, 32)


def read_uint(buffer, bits):
    """Read an unsigned integer stored in LEB128 format."""
    # https://www.w3.org/TR/wasm-core-1/#integers%E2%91%A4
    consumed_bytes = 0
    result = 0
    shift = 0

    try:
        while True:
            byte = buffer.read(1)[0]
            consumed_bytes += 1
            assert consumed_bytes <= math.ceil(bits / 7)
            result |= (byte & 127) << shift
            if not byte >> 7:
                break

            shift += 7

    except (AssertionError, IndexError):
        raise TypeError("Invalid integer.")

    return result


def read_sint(buffer, bits):
    """Read a signed integer stored in LEB128 format."""
    # https://www.w3.org/TR/wasm-core-1/#integers%E2%91%A4
    try:
        byte = buffer.read(1)[0]
        consumed_bytes = 1
        result = byte & 127
        shift = 7
        while byte >> 7:
            byte = buffer.read(1)[0]
            consumed_bytes += 1
            assert consumed_bytes <= math.ceil(bits / 7)
            result |= (byte & 127) << shift
            shift += 7

    except (AssertionError, IndexError):
        raise TypeError("Invalid integer.")

    if result >> consumed_bytes * 7 - 1:
        result |= ~0 << shift

    return result


def read_f32(buffer):
    """Read a single precision float from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#floating-point%E2%91%A4
    return f32.unpack(buffer.read(4))


def read_f64(buffer):
    """Read a double precision float from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#floating-point%E2%91%A4
    return f64.unpack(buffer.read(8))


def read_name(buffer):
    """Read a name from buffer."""
    # https://www.w3.org/TR/wasm-core-1/#names%E2%91%A2
    return buffer.read(get_vec_len(buffer)).decode("utf-8")
