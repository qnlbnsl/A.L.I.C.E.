import ctypes

matrix_hal = ctypes.CDLL("libmatrix_creator_hal.so")
matrix_hal.matrix_hal_get_version.restype = ctypes.c_char_p
