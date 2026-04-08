// lumie/math/overflow_arithmetic/msvc.hpp - MSVC-specific overflow traits
#pragma once

#include <intrin.h>
#include <type_traits>

#include "forward.hpp"

namespace lumie::math::overflow_arithmetic {

// Experimental MSVC-specific specialization using undocumented overflow
// intrinsics. This wraps compiler-provided checked arithmetic operations
// and is based on observed behavior rather than documented guarantees.

template <> struct overflow_trait<std::int16_t, msvc::experimental_tag> {
  using base_type = std::int16_t;
  using native_type = signed short;
  static_assert(std::is_same_v<base_type, native_type>,
                "base_type and native_type must be the same type.");

  [[nodiscard("overflow result must be checked")]]
  static bool add_overflow(base_type a, base_type b, base_type *result) {
    return _add_overflow_i16(0, a, b, result) != 0;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool sub_overflow(base_type a, base_type b, base_type *result) {
    return _sub_overflow_i16(0, a, b, result) != 0;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool mul_overflow(base_type a, base_type b, base_type *result) {
    return _mul_overflow_i16(a, b, result) != 0;
  }
};

template <> struct overflow_trait<std::int32_t, msvc::experimental_tag> {
  using base_type = std::int32_t;
  using native_type = signed int;
  static_assert(std::is_same_v<base_type, native_type>,
                "base_type and native_type must be the same type.");

  [[nodiscard("overflow result must be checked")]]
  static bool add_overflow(base_type a, base_type b, base_type *result) {
    return _add_overflow_i32(0, a, b, result) != 0;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool sub_overflow(base_type a, base_type b, base_type *result) {
    return _sub_overflow_i32(0, a, b, result) != 0;
  }
  [[nodiscard("overflow result must be checked")]]
  static bool mul_overflow(base_type a, base_type b, base_type *result) {
    return _mul_overflow_i32(a, b, result) != 0;
  }
};

static_assert(
    OverflowTrait<overflow_trait<std::int16_t, msvc::experimental_tag>,
                  std::int16_t>);
static_assert(
    OverflowTrait<overflow_trait<std::int32_t, msvc::experimental_tag>,
                  std::int32_t>);

} // namespace lumie::math::overflow_arithmetic