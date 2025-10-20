#include "music.h"

#include "buzzer.h"
#include "pixels.h"

void MusicState::enter() {
}

void MusicState::update() {
}

void MusicState::exit() {
  Buzzer::off(0);
  Buzzer::off(1);
  Pixels::clear();
}
