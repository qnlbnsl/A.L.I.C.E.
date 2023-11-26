# distutils: language = c++

from libc.stdint cimport int16_t
from libcpp cimport bool
    
cdef extern from "matrix_hal/matrixio_bus.h" namespace "matrix_hal":
    cdef cppclass MatrixIOBus:
        MatrixIOBus() except +
        bool Init()

cdef extern from "matrix_hal/microphone_array.h" namespace "matrix_hal":
    cdef cppclass MicrophoneArray:
        MicrophoneArray() except +
        void Setup(MatrixIOBus*)
        void SetSamplingRate(int)
        void SetGain(int)
        bool Read()
        int16_t& At(int, int) nogil
        # ... other methods as needed ...

cdef extern from "matrix_hal/microphone_core.h" namespace "matrix_hal":
    cdef cppclass MicrophoneCore:
        MicrophoneCore(MicrophoneArray&) except +
        void Setup(MatrixIOBus*)
        # ... other methods as needed ...
