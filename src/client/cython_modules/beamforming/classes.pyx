# cclasses.pyx
cdef extern from "YourCHeaderFile.h":
    cdef cppclass MicrophoneArray:
        MicrophoneArray() except +
        # Other necessary methods and attributes

    cdef cppclass CrossCorrelation:
        CrossCorrelation() except +
        # Methods and attributes

    cdef cppclass DirectionOfArrival:
        DirectionOfArrival(MicrophoneArray&) except +
        # Methods and attributes

# You may also need to cimport numpy if your C++ code interfaces with numpy arrays
