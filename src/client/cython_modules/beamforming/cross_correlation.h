#ifndef CPP_CROSS_CORRELATION_H_
#define CPP_CROSS_CORRELATION_H_

#include <fftw3.h>
#include <stdint.h>

namespace matrix_hal {

/*
Cross-correlation between signals implemented in frequency domain.
*/
class CrossCorrelation {
 public:
  CrossCorrelation();
  ~CrossCorrelation();
  bool Init(int N);
  void Release();
  void Exec(int16_t *a, int16_t *b);
  float *Result();

 private:
  void Corr(float *out, float *x, float *y);

  int order_;
  float *in_;
  float *A_;
  float *B_;
  float *C_;
  float *c_;

  fftwf_plan forward_plan_a_;
  fftwf_plan forward_plan_b_;
  fftwf_plan inverse_plan_;
};

};      // namespace matrix_hal
#endif  // CPP_CROSS_CORRELATION_H_