#include <Arduino.h>

#include <array>
#include <vector>

namespace ADC {

std::vector<String> init();
std::tuple<std::vector<String>, std::array<float, 8>> readAll();

String progress_bar(float value, int length);

} // namespace ADC
