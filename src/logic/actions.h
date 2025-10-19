#pragma once

#include <functional>
#include <time.h>

using Action = std::function<void()>;
using ScheduledAction = std::function<void(time_t scheduledTime)>;
