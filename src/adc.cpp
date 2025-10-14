#include <adc.h>

#include <ADS1115.h>

namespace {

std::array<std::tuple<ADS1115::ADS1115_ADC, int>, 2> adcs =
  {{{ADS1115::ADS1115_ADC(ADS1115::I2CAddress::Scl), 0},
    {ADS1115::ADS1115_ADC(ADS1115::I2CAddress::Sda), 1}}};

constexpr int MAX = 26300;
constexpr auto pga = ADS1115::Pga::FSR_4_096V;
constexpr auto dataRate = ADS1115::DataRate::SPS_475;

} // namespace

std::vector<String> ADC::init() {
  std::vector<String> errors;
  ADS1115::Status status;
  for (auto& [adc, index] : adcs) {
    if (!adc.isConnected()) {
      errors.push_back(String("ADC 0x") + static_cast<int>(adc.getAddress()) + " not connected");
      continue;
    }
    status = adc.init();
    if (status != ADS1115::Status::Ok) {
      errors.push_back(String("Failed to init ADC 0x") + static_cast<int>(adc.getAddress()) + ": " + static_cast<int>(status));
      continue;
    }
    adc.setPga(pga);
    adc.setDataRate(dataRate);
    status = adc.uploadConfig();
    if (status != ADS1115::Status::Ok) {
        errors.push_back(String("Failed to configure ADC 0x") + static_cast<int>(adc.getAddress()) + ": " + static_cast<int>(status));
        continue;
    }
  }
  return errors;
}

std::tuple<std::vector<String>, std::array<float, 8>> ADC::readAll() {
  std::vector<String> errors;
  std::array<float, 8> results = {0};
  const auto channels = {
    std::tuple{ADS1115::Mux::P0_GND, 0}, {ADS1115::Mux::P1_GND, 1}, {ADS1115::Mux::P2_GND, 2}, {ADS1115::Mux::P3_GND, 3},
  };

  ADS1115::Status status;
  for (int c = 0; c < 4; c++) {
    for (auto& [adc, adc_index] : adcs) {
      delay(1);
      if (!adc.isConnected()) {
        errors.push_back(String("ADC 0x") + static_cast<int>(adc.getAddress()) + " not connected");
        continue;
      }
      status = adc.startSingleShotConversion(c);
      if (status != ADS1115::Status::Ok) {
        errors.push_back(String("Failed to start conversion on ADC 0x") + static_cast<int>(adc.getAddress()) + " A" + static_cast<int>(c) + ": " + static_cast<int>(status));
        continue;
      }
      bool ready;
      int attempts = 0;
      do {
        delay(1);
        status = adc.isConversionReady(ready);
        if (status != ADS1115::Status::Ok) {
          errors.push_back(String("Failed to check conversion status on ADC 0x") + static_cast<int>(adc.getAddress()) + " A" + static_cast<int>(c) + ": " + static_cast<int>(status));
          break;
        }
        attempts++;
        if (attempts >= 100) {
          errors.push_back(String("Timeout waiting for conversion on ADC 0x") + static_cast<int>(adc.getAddress()) + " A" + static_cast<int>(c));
          break;
        }
      } while (!ready);
      int16_t result;
      status = adc.readConversion(result);
      if (status != ADS1115::Status::Ok) {
        errors.push_back(String("Failed to read conversion on ADC 0x") + static_cast<int>(adc.getAddress()) + " A" + static_cast<int>(c) + ": " + static_cast<int>(status));
        continue;
      }
      results[adc_index * 4 + c] = std::clamp(static_cast<float>(result) / static_cast<float>(MAX), 0.0f, 1.0f);
    }
  }
  return {errors, results};
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
