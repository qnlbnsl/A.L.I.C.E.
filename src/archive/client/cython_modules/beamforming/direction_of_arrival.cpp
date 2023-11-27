#include <cmath>
#include <map>
#include <string>
#include <vector>

#include "./cross_correlation.h"
#include "./direction_of_arrival.h"

namespace matrix_hal {

static float micarray_location_creator[8][2] = {
    {20.0908795, -48.5036755},  /* M1 */
    {-20.0908795, -48.5036755}, /* M2 */
    {-48.5036755, -20.0908795}, /* M3 */
    {-48.5036755, 20.0908795},  /* M4 */
    {-20.0908795, 48.5036755},  /* M5 */
    {20.0908795, 48.5036755},   /* M6 */
    {48.5036755, 20.0908795},   /* M7 */
    {48.5036755, -20.0908795}   /* M8 */
};

static float micarray_location_voice[8][2] = {
    {00.00, 00.00},  /* M1 */
    {-38.13, 3.58},  /* M2 */
    {-20.98, 32.04}, /* M3 */
    {11.97, 36.38},  /* M4 */
    {35.91, 13.32},  /* M5 */
    {32.81, -19.77}, /* M6 */
    {5.00, -37.97},  /* M7 */
    {-26.57, -27.58} /* M8 */
};

  DirectionOfArrival::DirectionOfArrival() : azimutal_angle_(0), polar_angle_(0) {
      // Initialize microphone positions
      for (size_t i = 0; i < 8; ++i) {
          mic_positions[i] = {micarray_location_creator[i][0], micarray_location_creator[i][1]};
      }

      // Initialize CrossCorrelation object
      cross_corr_.Init(640); // Assuming 640 is the size of the audio chunk
  }

  void DirectionOfArrival::Calculate(const std::valarray<int16_t>& input_data) {
      calculateCrossCorrelation(input_data);
      findDirection();
  }

  void DirectionOfArrival::calculateCrossCorrelation(const std::valarray<int16_t>& input_data) {
      // Assuming input_data is an 8x640 array (8 channels, 640 samples each)
      // You need to reshape or reorganize this data to pass to cross_corr_.Exec

      // Example: Cross-correlation between channel 1 and channel 2
      // Adjust indices and loop as needed for all channel pairs
      std::valarray<int16_t> channel1 = input_data[std::slice(0, 640, 8)];
      std::valarray<int16_t> channel2 = input_data[std::slice(1, 640, 8)];
      cross_corr_.Exec(&channel1[0], &channel2[0]);

      // Process results from cross_corr_.Result()
      // Repeat for other channel pairs as needed
  }

  void DirectionOfArrival::findDirection() {
      // Use cross-correlation results to calculate time delays between microphones
      // and use those delays to compute the DoA

      // Placeholder for direction calculation logic
      // You'll need to implement the actual algorithm to compute azimutal_angle_ and polar_angle_
      float *results = cross_corr_.Result();
      azimutal_angle_ = computeAzimuth(results); // Implement this method
      polar_angle_ = computeElevation(results); // Implement this method
  }

  float DirectionOfArrival::computeAzimuth(float *results) {
      // Implement azimuth calculation based on cross-correlation results
      return 0.0; // Placeholder
  }

  float DirectionOfArrival::computeElevation(float *results) {
      // Implement elevation calculation based on cross-correlation results
      return 0.0; // Placeholder
  }

  float DirectionOfArrival::GetAzimutalAngle() const {
      return azimutal_angle_;
  }

  float DirectionOfArrival::GetPolarAngle() const {
      return polar_angle_;
  }
  
} // namespace matrix_hal