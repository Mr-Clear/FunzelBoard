#include "carousel.h"

#include "color.h"
#include "pixels.h"
#include "scheduler.h"

namespace {
  uint16_t carouselPosition = 0;
  uint16_t carouselPixel(uint16_t pos) {
    const uint16_t p = pos < 8 ? pos : 23 - pos;
    return (p + 24);
  }
}

void carousel(time_t scheduledTime) {
  Pixels::setColor(carouselPixel(carouselPosition), BLACK);
  carouselPosition = (carouselPosition + 1) % 16;
  Pixels::setColor(carouselPixel(carouselPosition), WHITE);
  Scheduler::schedule(scheduledTime + 100, &carousel);
}