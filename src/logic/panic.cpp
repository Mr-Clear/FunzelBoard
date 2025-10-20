#include "panic.h"

#include "buzzer.h"
#include "motor.h"
#include "pixels.h"

void PanicState::enter() {
}
void PanicState::update() {
}
void PanicState::exit() {
  Motor::stop();
  Pixels::clear();
  Buzzer::off(0);
  Buzzer::off(1);
}