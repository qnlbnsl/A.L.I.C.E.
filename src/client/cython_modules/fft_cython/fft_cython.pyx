# fft_cython.pyx
import numpy as np
cimport numpy as np
cimport cython

# Set the language level
# cython: language_level=3

# Import FFTW headers
cdef extern from "fftw3.h":
    ctypedef struct fftwf_plan_s "fftwf_plan"
    fftwf_plan fftwf_plan_dft_r2c_1d(int n, float *in_rs, float complex *out_rs, unsigned flags)
    fftwf_plan fftwf_plan_dft_c2r_1d(int n, float complex *in_rs, float *out_rs, unsigned flags)
    void fftwf_execute(const fftwf_plan plan)
    void fftwf_destroy_plan(fftwf_plan plan)

@cython.boundscheck(False)
@cython.wraparound(False)
def fft_cross_correlate(float[:] signal_a, float[:] signal_b):
    cdef int n = 2 ** np.ceil(np.log2(signal_a.size + signal_b.size - 1)).astype(int)
    cdef np.ndarray[cython.float, ndim=1] fft_input_a = np.zeros(n, dtype=np.float32)
    cdef np.ndarray[cython.float, ndim=1] fft_input_b = np.zeros(n, dtype=np.float32)
    cdef np.ndarray[cython.complex, ndim=1] fft_output_a = np.zeros(n // 2 + 1, dtype=np.complex64)
    cdef np.ndarray[cython.complex, ndim=1] fft_output_b = np.zeros(n // 2 + 1, dtype=np.complex64)

    # Create FFT plans
    cdef fftwf_plan plan_a = fftwf_plan_dft_r2c_1d(n, &fft_input_a[0], &fft_output_a[0], 0)
    cdef fftwf_plan plan_b = fftwf_plan_dft_r2c_1d(n, &fft_input_b[0], &fft_output_b[0], 0)

    # Perform FFT
    fftwf_execute(plan_a)
    fftwf_execute(plan_b)

    # Element-wise multiplication and IFFT...
    # (You'll need to write the code for this part, similar to your existing Python logic)

    # Clean up
    fftwf_destroy_plan(plan_a)
    fftwf_destroy_plan(plan_b)

    # Return the final result
    # (Remember to return the real part of the IFFT result)
