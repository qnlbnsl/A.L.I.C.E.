# distutils: language = c++

cdef extern from "direction_of_arrival.h":
    cdef cppclass CDirectionOfArrival:
        CDirectionOfArrival() except +
        void Calculate(const int16_t[::1]&) nogil
        float GetAzimutalAngle() nogil
        float GetPolarAngle() nogil

cdef class PyDirectionOfArrival:
    cdef CDirectionOfArrival* thisptr      # Hold a C++ instance

    def __cinit__(self):
        self.thisptr = new CDirectionOfArrival()

    def __dealloc__(self):
        if self.thisptr is not NULL:
            del self.thisptr

    def calculate(self, data):
        # Assuming 'data' is a Python list or array. Convert it to a compatible format.
        cdef int16_t[:] c_data = data
        self.thisptr.Calculate(c_data)

    def get_azimutal_angle(self):
        return self.thisptr.GetAzimutalAngle()

    def get_polar_angle(self):
        return self.thisptr.GetPolarAngle()
