#pragma once

#include "data.h"

#include <memory>

class Action {
  public:
  Action() = default;
  virtual ~Action() = default;
  virtual void run() = 0;
};

class DelayedAction : public Action {
public:
  DelayedAction(time_t timestamp) : Action{}, _timestamp(timestamp) {}
  time_t timestamp() const;
  virtual bool operator<(const DelayedAction& other) const;

private:
  time_t _timestamp;
};

struct ActionOrder {
  bool operator()(const std::unique_ptr<DelayedAction>& a, const std::unique_ptr<DelayedAction>& b) const;
};