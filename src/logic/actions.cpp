#include "actions.h"

time_t DelayedAction::timestamp() const
{
  return _timestamp;
}

bool DelayedAction::operator<(const DelayedAction &other) const
{
  return _timestamp < other._timestamp;
}

bool ActionOrder::operator()(const std::unique_ptr<DelayedAction>& a, const std::unique_ptr<DelayedAction>& b) const {
  if (a->timestamp() != b->timestamp())
    return a->timestamp() < b->timestamp();
  return a.get() < b.get();
}