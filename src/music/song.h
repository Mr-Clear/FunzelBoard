#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

struct Note {
  uint32_t startUs;
  uint32_t endUs;
  uint8_t pitch;
} __attribute__((packed));

struct Track {
  const Note* notes;
  size_t length;
};

struct Song {
  std::array<Track, 3> tracks;
  bool loop;
};
