#include <Arduino.h>

#include <array>
#include <optional>
#include <vector>

namespace ADC {

std::optional<String> init();
std::array<float, 8> readAll();

String progress_bar(float value, int length);

} // namespace ADC
