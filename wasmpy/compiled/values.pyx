#cython: language_level=3

from libc.stdint cimport uint8_t, uint32_t, int32_t, uint64_t, int64_t


cdef struct valid:
    int is_vld
    char * err_msg


def say_hello():
    print("Hello, World!")


cdef uint32_t get_vec_len(char *buf, uint32_t *buf_off, valid *v):
    """Return the length of a vector consumed from buf."""
    # https://www.w3.org/TR/wasm-core-1/#vectors%E2%91%A2
    return read_uint32(buf, buf_off, v)


cdef uint32_t read_uint32(char *buf, uint32_t *buf_off, valid *v):
    """Read an unsigned 32 bit integer stored in LEB128 format."""
    # https://www.w3.org/TR/wasm-core-1/#integers%E2%91%A4
    cdef short consumed_bytes = 0, shift = 0, in_off = 0
    cdef uint32_t result = 0
    cdef uint8_t byte
    while True:
        byte = buf[buf_off[0] + in_off]
        consumed_bytes += 1
        if consumed_bytes > 5 and v.is_vld:
            v.is_vld = 0
            v.err_msg = "Invalid integer."

        result |= (byte & 127) << shift
        if not byte >> 7:
            break

        shift += 7
        in_off += 1

    buf_off += in_off
    return result


cdef uint64_t read_uint64(char *buf, uint32_t *buf_off, valid *v):
    """Read an unsigned 64 bit integer stored in LEB128 format."""
    # https://www.w3.org/TR/wasm-core-1/#integers%E2%91%A4
    cdef short consumed_bytes = 0, shift = 0, in_off = 0
    cdef uint64_t result = 0
    cdef uint8_t byte
    while True:
        byte = buf[buf_off[0] + in_off]
        consumed_bytes += 1
        if consumed_bytes > 10 and v.is_vld:
            v.is_vld = 0
            v.err_msg = "Invalid integer."

        result |= (byte & 127) << shift
        if not byte >> 7:
            break

        shift += 7
        in_off += 1

    buf_off += in_off
    return result


cdef int32_t read_sint32(char *buf, uint32_t *buf_off, valid *v):
    """Read a signed 32 bit integer stored in LEB128 format."""
    # https://www.w3.org/TR/wasm-core-1/#integers%E2%91%A4
    cdef short consumed_bytes = 1, shift = 0, in_off = 0
    cdef uint8_t byte = buf[buf_off[0]]
    cdef int32_t result  = byte & 127
    buf_off += 1
    byte = buf[buf_off[0]]
    while byte >> 7:
        consumed_bytes += 1
        if consumed_bytes > 5:
            v.is_vld = 0
            v.err_msg = "Invalid integer."

        result |= (byte & 127) << shift
        shift += 7
        in_off += 1
        byte = buf[buf_off[0]+in_off]

    if shift < 32 and (byte >> 6) & 1:
        result |= ~0 << shift

    buf_off += in_off
    return result


cdef int64_t read_sint64(char *buf, uint32_t *buf_off, valid *v):
    """Read a signed 64 bit integer stored in LEB128 format."""
    # https://www.w3.org/TR/wasm-core-1/#integers%E2%91%A4
    cdef short consumed_bytes = 1, shift = 0, in_off = 0
    cdef uint8_t byte = buf[buf_off[0]]
    cdef int64_t result  = byte & 127
    buf_off += 1
    byte = buf[buf_off[0]]
    while byte >> 7:
        consumed_bytes += 1
        if consumed_bytes > 5:
            v.is_vld = 0
            v.err_msg = "Invalid integer."

        result |= (byte & 127) << shift
        shift += 7
        in_off += 1
        byte = buf[buf_off[0]+in_off]

    if shift < 32 and (byte >> 6) & 1:
        result |= ~0 << shift

    buf_off += in_off
    return result


cdef uint32_t read_f32(char *buf, uint32_t *buf_off, valid *v):
    """Read a single precision float from buf."""
    # returns a uint32_t so as to eliminate any possible rounding errors
    # https://www.w3.org/TR/wasm-core-1/#floating-point%E2%91%A4
    cdef uint32_t val = buf[buf_off[0]]
    # shift left as stored as little endian
    val |= buf[buf_off[0]+1] << 8
    val |= buf[buf_off[0]+2] << 16
    val |= buf[buf_off[0]+3] << 24
    buf_off += 4
    return val


cdef uint64_t read_f64(char *buf, uint32_t *buf_off, valid *v):
    """Read a single precision float from buf."""
    # returns a uint64_t so as to eliminate any possible rounding errors
    # https://www.w3.org/TR/wasm-core-1/#floating-point%E2%91%A4
    cdef uint64_t val = buf[buf_off[0]]
    # shift left as stored as little endian
    val |= <uint64_t>buf[buf_off[0]+1] << 8
    val |= <uint64_t>buf[buf_off[0]+2] << 16
    val |= <uint64_t>buf[buf_off[0]+3] << 24
    val |= <uint64_t>buf[buf_off[0]+4] << 32
    val |= <uint64_t>buf[buf_off[0]+5] << 40
    val |= <uint64_t>buf[buf_off[0]+6] << 48
    val |= <uint64_t>buf[buf_off[0]+7] << 56
    buf_off += 8
    return val


cdef bytes read_name(char *buf, uint32_t *buf_off, valid *v):
    """Read a name from buf."""
    # https://www.w3.org/TR/wasm-core-1/#names%E2%91%A2
    cdef uint32_t length = get_vec_len(buf, buf_off, v)
    cdef bytes result
    result = buf[buf_off[0]:buf_off[0]+length]
    return result
