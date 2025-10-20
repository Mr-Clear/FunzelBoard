#pragma once

#include "state.h"

class PanicState : public State {
public:
  void enter() override;
  void update() override;
  void exit() override;
};
