# distutils: language = c++
# cython: language_level=3str


from matrix_hal cimport MatrixIOBus, MicrophoneArray, MicrophoneCore
import numpy as np
cimport numpy as np

cdef class PyMatrixIOBus:
    cdef MatrixIOBus c_bus

    def __cinit__(self):
        self.c_bus = MatrixIOBus()
        if not self.c_bus.Init():
            raise Exception("Failed to initialize MatrixIOBus")

cdef class PyMicrophoneArray:
    cdef MicrophoneArray c_mic_array
    cdef PyMatrixIOBus py_bus

    def __cinit__(self, PyMatrixIOBus py_bus, int sampling_rate, int gain):
        self.py_bus = py_bus
        self.c_mic_array.Setup(&py_bus.c_bus)
        self.c_mic_array.SetSamplingRate(sampling_rate)
        if gain > 0:
            self.c_mic_array.SetGain(gain)

    def read(self):
        if not self.c_mic_array.Read():
            raise Exception("Failed to read from MicrophoneArray")

    def get_audio_data(self, int channel, int num_samples):
        cdef np.ndarray data = np.zeros(num_samples, dtype=np.int16)
        for i in range(num_samples):
            data[i] = self.c_mic_array.At(i, channel)
        return data

# Similar wrapper for MicrophoneCore if needed
