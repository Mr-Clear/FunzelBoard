#pragma once

#include "color.h"

namespace Pixels {
    bool init();
    void setBrightness(float brightness);
    void setColor(uint16_t n, Color color);
    void clear();
    void show();
}  // namespace Pixels