from libc.stdint cimport uint32_t, uint64_t, int32_t, int64_t

# error construct
cdef struct valid

# vectors
cdef uint32_t get_vec_len(char *buf, uint32_t *buf_off, valid *v)

# unsigned integers
cdef uint32_t read_uint32(char *buf, uint32_t *buf_off, valid *v)
cdef uint64_t read_uint64(char *buf, uint32_t *buf_off, valid *v)

# signed integers
cdef int32_t read_sint32(char *buf, uint32_t *buf_off, valid *v)
cdef int64_t read_sint64(char *buf, uint32_t *buf_off, valid *v)

# floating point values
cdef uint32_t read_f32(char *buf, uint32_t *buf_off, valid *v)
cdef uint64_t read_f64(char *buf, uint32_t *buf_off, valid *v)

# name values
cdef bytes read_name(char *buf, uint32_t *buf_off, valid *v)
