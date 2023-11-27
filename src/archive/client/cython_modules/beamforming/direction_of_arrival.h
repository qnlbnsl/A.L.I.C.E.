#ifndef DIRECTION_OF_ARRIVAL_H
#define DIRECTION_OF_ARRIVAL_H

#include <array>
#include <valarray>
#include <cmath>
#include "cross_correlation.h"

namespace matrix_hal {

class DirectionOfArrival {
 public:
  DirectionOfArrival();
  void Calculate(const std::valarray<int16_t>& input_data);
  float GetAzimutalAngle() const;
  float GetPolarAngle() const;

 private:
  CrossCorrelation cross_corr_;  // Cross-correlation instance
  std::array<std::array<float, 2>, 8> mic_positions;
  float azimutal_angle_;
  float polar_angle_;
  void calculateCrossCorrelation(const std::valarray<int16_t>& input_data);
  void findDirection();
};

}  // namespace matrix_hal

#endif // DIRECTION_OF_ARRIVAL_H
