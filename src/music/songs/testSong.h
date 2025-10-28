#pragma once

#include "music/song.h"

namespace Songs {
  namespace TestSong {
    inline constexpr Note track1[4] = {
      {0, 500000, 60},
      {600000, 1100000, 62},
      {1200000, 1700000, 64},
      {1800000, 2300000, 65},
    };

    inline constexpr Note track2[4] = {
      {0, 400000, 72},
      {500000, 900000, 74},
      {1000000, 1400000, 76},
      {1500000, 1900000, 77},
    };
  }

  inline constexpr Song testSong = {{{
      {TestSong::track1, 4},
      {TestSong::track2, 4},
      {nullptr, 0}
    }},
    false
  };
}
