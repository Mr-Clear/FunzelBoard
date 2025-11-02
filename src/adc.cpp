#include "adc.h"

#include "config.h"

#include <i2c_adc_ads7828.h>

namespace {

  ADS7828 *device;

} // namespace

std::optional<String> ADC::init() {
  device = new ADS7828(0x48, SINGLE_ENDED | REFERENCE_ON | ADC_ON, 0xFF);
  switch (device->start()) {
    case 0:
      return {};
    case 1:
      return {"ADC error: Length too long for buffer"};
    case 2:
      return {"ADC error: Address send, NACK on data"};
    case 3:
      return {"ADC error: Data send, NACK on data"};
    case 4:
      return {"ADC error: Other TWI error"};
    default:
      return {"ADC error: Unknown error"};
  }
}

std::array<float, 8> ADC::readAll() {
  device->updateAll();
  std::array<uint16_t, 8> raw;
  for (size_t i = 0; i < 8; i++) {
    raw[i] = device->channel(i)->value();
  }

  const auto min = raw[7];
  const auto max = raw[6];

  std::array<float, 8> results;
  for (size_t i = 0; i < 8; i++) {
    results[i] = static_cast<float>(raw[i] - min) / static_cast<float>(max - min);
    results[i] = std::clamp(results[i], 0.0f, 1.0f);
  }

  return results;
}

String ADC::progress_bar(float value, int length) {
  const char* bars[] = {" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"};
  const int full_blocks = static_cast<int>(value * length);
  const int partial_block_index = static_cast<int>((value * length - full_blocks) * 8);
  const int empty_blocks = length - full_blocks - (partial_block_index > 0 ? 1 : 0);
  String bar;
  bar.reserve(length * 3); // Reserve enough space for UTF-8 characters
  for (int i = 0; i < full_blocks; i++) {
    bar += bars[7];
  }
  if (partial_block_index > 0) {
    bar += bars[partial_block_index];
  }
  for (int i = 0; i < empty_blocks; i++) {
    bar += bars[0];
  }
  return bar;
}
