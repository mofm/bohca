import ctypes.util


MAGIC_NONE = 0
MAGIC_MIME = 1040
MAGIC_MIME_ENCODING = 1024

# Load the library
libmagic = ctypes.cdll.LoadLibrary(ctypes.util.find_library('magic'))

# Set the return type
libmagic.magic_file.restype = ctypes.c_char_p
libmagic.magic_buffer.restype = ctypes.c_char_p
libmagic.magic_open.restype = ctypes.c_void_p
libmagic.magic_load.restype = ctypes.c_int
libmagic.magic_close.restype = ctypes.c_int
libmagic.magic_error.restype = ctypes.c_char_p

# Set the argument types
libmagic.magic_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
libmagic.magic_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
libmagic.magic_open.argtypes = [ctypes.c_int]
libmagic.magic_load.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
libmagic.magic_close.argtypes = [ctypes.c_void_p]
libmagic.magic_error.argtypes = [ctypes.c_void_p]


class Magic:
    def __init__(self, mime=True, magic_file=None, mime_encoding=False):
        self.cookie = libmagic.magic_open(MAGIC_NONE)
        if mime:
            self.cookie = libmagic.magic_open(MAGIC_MIME)
        if mime_encoding:
            self.cookie = libmagic.magic_open(MAGIC_MIME_ENCODING)
        if libmagic.magic_load(self.cookie, magic_file) != 0:
            raise RuntimeError(libmagic.magic_error(self.cookie))

    def from_file(self, filename):
        return libmagic.magic_file(self.cookie, filename).decode('utf-8')

    def from_buffer(self, buf):
        return libmagic.magic_buffer(self.cookie, buf, len(buf)).decode('utf-8')

    def close(self):
        libmagic.magic_close(self.cookie)

    def __del__(self):
        if hasattr(self, 'cookie') and libmagic:
            self.close()


magic_none = Magic(mime=False)
magic_mime = Magic(mime=True)


def _parse_output(output):
    if output is None:
        return None
    return output.split(';')[0]


def check_magic_file(mime, magic_file=None):
    if mime:
        return _parse_output(magic_mime.from_file(magic_file))
    else:
        return magic_none.from_file(magic_file)


def check_magic_buffer(mime, buf=None):
    if mime:
        return _parse_output(magic_mime.from_buffer(buf))
    else:
        return magic_none.from_buffer(buf)
