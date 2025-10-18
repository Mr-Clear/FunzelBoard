#pragma once

#include <cstdint>

namespace Buzzer {
    void init();
    void tone(uint8_t buzzer, float hz);
    void off(uint8_t buzzer);
}  // namespace Buzzer