# cython: language_level=3str
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "numpy/arrayobject.h"

import numpy as np
cimport numpy as np

from libc.stdint cimport int16_t, uint16_t, uint32_t
from libcpp cimport bool

cdef extern from "matrix_hal/matrixio_bus.h" namespace "matrix_hal":
    cdef cppclass MatrixIOBus:
        MatrixIOBus() except +
        bool Init()

cdef extern from "matrix_hal/microphone_array.h" namespace "matrix_hal":
    cdef cppclass MicrophoneArray:
        MicrophoneArray(bool enable_beamforming) except +
        void Setup(MatrixIOBus*)
        bool Read()
        uint32_t SamplingRate() 
        uint16_t Gain()
        void SetSamplingRate(int)
        void SetGain(int)
        bool GetSamplingRate()
        bool GetGain()
        void ReadConfValues()
        void ShowConfiguration()
        uint16_t Channels()
        uint32_t NumberOfSamples()
        int16_t& At(int16_t, int16_t) nogil
        int16_t& Beam(int16_t)
        void CalculateDelays(float azimutal_angle, float polar_angle,
                            float radial_distance_mm, float sound_speed_mmseg)        

cdef class PyMatrixIOBus:
    cdef MatrixIOBus* c_bus

    def __cinit__(self):
        self.c_bus = new MatrixIOBus()
        if not self.c_bus.Init():
            raise Exception("Failed to initialize MatrixIOBus")

cdef class PyMicrophoneArray:
    cdef MicrophoneArray* c_mic_array
    cdef PyMatrixIOBus py_bus

    def __cinit__(self, PyMatrixIOBus py_bus, int sampling_rate, int gain, bool enable_beamforming):
        self.py_bus = py_bus
        self.c_mic_array = new MicrophoneArray(enable_beamforming)
        self.c_mic_array.Setup(self.py_bus.c_bus)
        self.c_mic_array.SetSamplingRate(sampling_rate)
        print(self.c_mic_array.Channels())
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

    def show_configuration(self):
        self.c_mic_array.ShowConfiguration()
    
    def calculate_delays(self, float azimutal_angle, float polar_angle, float radial_distance_mm, float sound_speed_mmseg):
        self.c_mic_array.CalculateDelays(azimutal_angle, polar_angle, radial_distance_mm, sound_speed_mmseg)

    def beam(self, np.int16_t samples):
        return self.c_mic_array.Beam(samples)
    def __dealloc__(self):
        if self.c_mic_array is not NULL:
            del self.c_mic_array
