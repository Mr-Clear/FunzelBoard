#include "tools.h"

std::vector<std::string_view> splitString(std::string_view s, char delimiter) {
  std::vector<std::string_view> result;
  size_t start = 0;
  size_t end = s.find(delimiter);
  while (end != std::string_view::npos) {
    result.emplace_back(s.substr(start, end - start));
    start = end + 1;
    end = s.find(delimiter, start);
  }
  result.emplace_back(s.substr(start));
  return result;
}
