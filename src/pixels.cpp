#include "pixels.h"

#include "config.h"

#include <Adafruit_NeoPixel.h>

namespace {
    Adafruit_NeoPixel pixels(NUM_PIXELS, PIXELS_PIN, NEO_GRB + NEO_KHZ800);
    float brightness = 1.0f;
}

bool Pixels::init() {
  return pixels.begin();
}

void Pixels::setBrightness(float brightness) {
    ::brightness = brightness;
}

void Pixels::setColor(uint16_t n, Color color) {
    pixels.setPixelColor(n, color * brightness);
}

void Pixels::clear() {
    pixels.clear();
}

void Pixels::show() {
    pixels.show();
}
