import io, unittest

import wasmpy.values


class TestInts(unittest.TestCase):
    def test_unsigned_32bit_zeros(self):
        for z in (io.BytesIO(b"\x80" * i + b"\x00") for i in range(5)):
            self.assertEquals(wasmpy.values.read_uint(buffer=z, bits=32), 0)

        # too many bytes: 6 > ( ceil(32 / 7) = 5 )
        buf = io.BytesIO(b"\x80" * 5 + b"x00")
        with self.assertRaises(TypeError):
            wasmpy.values.read_uint(buffer=buf, bits=32)

    def test_unsigned_64bit_zeros(self):
        for z in (io.BytesIO(b"\x80" * i + b"\x00") for i in range(10)):
            self.assertEquals(wasmpy.values.read_uint(buffer=z, bits=64), 0)

        # too many bytes: 11 > ( ceil(64 / 7) = 10 )
        buf = io.BytesIO(b"\x80" * 10 + b"\x00")
        with self.assertRaises(TypeError):
            wasmpy.values.read_uint(buffer=buf, bits=64)

    def test_lack_of_continuation(self):
        buf = io.BytesIO(b"\x80")
        with self.assertRaises(TypeError):
            # attempts to consume another byte at end of file
            wasmpy.values.read_uint(buffer=buf, bits=32)

    def test_signed_32bit_zeros(self):
        for z in (io.BytesIO(b"\x80" * i + b"\x00") for i in range(5)):
            self.assertEquals(wasmpy.values.read_sint(buffer=z, bits=32), 0)

        # too many bytes: 6 > ( ceil(32 / 7) = 5 )
        buf = io.BytesIO(b"\x80" * 5 + b"x00")
        with self.assertRaises(TypeError):
            wasmpy.values.read_uint(buffer=buf, bits=32)

    def test_signed_64bit_zeros(self):
        for z in (io.BytesIO(b"\x80" * i + b"\x00") for i in range(10)):
            self.assertEquals(wasmpy.values.read_sint(buffer=z, bits=64), 0)

        # too many bytes: 11 > ( ceil(64 / 7) = 10 )
        buf = io.BytesIO(b"\x80" * 10 + b"x00")
        with self.assertRaises(TypeError):
            wasmpy.values.read_uint(buffer=buf, bits=64)
