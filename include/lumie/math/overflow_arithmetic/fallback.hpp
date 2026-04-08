// lumie/math/overflow_arithmetic/fallback.hpp - Portable fallback overflow
// traits
#pragma once

#include <limits> // for std::numeric_limits

#include "forward.hpp"

namespace lumie::math::overflow_arithmetic {

template <> struct overflow_trait<std::int16_t, fallback::tag> {
  using base_type = std::int16_t;
  using wider_type = std::int32_t;

  [[nodiscard("overflow result must be checked")]]
  static bool add_overflow(base_type a, base_type b, base_type *result) {
    wider_type temp = static_cast<wider_type>(a) + static_cast<wider_type>(b);
    if (temp > static_cast<wider_type>(std::numeric_limits<base_type>::max()) ||
        temp < static_cast<wider_type>(std::numeric_limits<base_type>::min())) {
      return true;
    }
    *result = static_cast<base_type>(temp);
    return false;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool sub_overflow(base_type a, base_type b, base_type *result) {
    wider_type temp = static_cast<wider_type>(a) - static_cast<wider_type>(b);
    if (temp > static_cast<wider_type>(std::numeric_limits<base_type>::max()) ||
        temp < static_cast<wider_type>(std::numeric_limits<base_type>::min())) {
      return true;
    }
    *result = static_cast<base_type>(temp);
    return false;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool mul_overflow(base_type a, base_type b, base_type *result) {
    wider_type temp = static_cast<wider_type>(a) * static_cast<wider_type>(b);
    if (temp > static_cast<wider_type>(std::numeric_limits<base_type>::max()) ||
        temp < static_cast<wider_type>(std::numeric_limits<base_type>::min())) {
      return true;
    }
    *result = static_cast<base_type>(temp);
    return false;
  }
};

template <> struct overflow_trait<std::int32_t, fallback::tag> {
  using base_type = std::int32_t;
  using wider_type = std::int64_t;

  [[nodiscard("overflow result must be checked")]]
  static bool add_overflow(base_type a, base_type b, base_type *result) {
    wider_type temp = static_cast<wider_type>(a) + static_cast<wider_type>(b);
    if (temp > static_cast<wider_type>(std::numeric_limits<base_type>::max()) ||
        temp < static_cast<wider_type>(std::numeric_limits<base_type>::min())) {
      return true;
    }
    *result = static_cast<base_type>(temp);
    return false;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool sub_overflow(base_type a, base_type b, base_type *result) {
    wider_type temp = static_cast<wider_type>(a) - static_cast<wider_type>(b);
    if (temp > static_cast<wider_type>(std::numeric_limits<base_type>::max()) ||
        temp < static_cast<wider_type>(std::numeric_limits<base_type>::min())) {
      return true;
    }
    *result = static_cast<base_type>(temp);
    return false;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool mul_overflow(base_type a, base_type b, base_type *result) {
    wider_type temp = static_cast<wider_type>(a) * static_cast<wider_type>(b);
    if (temp > static_cast<wider_type>(std::numeric_limits<base_type>::max()) ||
        temp < static_cast<wider_type>(std::numeric_limits<base_type>::min())) {
      return true;
    }
    *result = static_cast<base_type>(temp);
    return false;
  }
};

static_assert(
    OverflowTrait<overflow_trait<std::int16_t, fallback::tag>, std::int16_t>);
static_assert(
    OverflowTrait<overflow_trait<std::int32_t, fallback::tag>, std::int32_t>);

} // namespace lumie::math::overflow_arithmetic