// lumie/math/overflow_arithmetic/forward.hpp - Forward declarations for
// overflow traits

#pragma once
#include <concepts>    // for std::same_as
#include <cstdint>     // for fixed-width integer types
#include <type_traits> // for std::is_integral_v, std::is_signed_v

namespace lumie::math::overflow_arithmetic {

template <typename T, typename... Tags> struct overflow_trait;

// A type models OverflowTrait if it provides a signed integral base_type and
// checked arithmetic member functions that report overflow via bool.
template <typename Trait, typename T>
concept OverflowTrait = std::is_integral_v<T> && std::is_signed_v<T> &&
                        requires(T a, T b, T *result) {
                          {
                            Trait::add_overflow(a, b, result)
                          } -> std::same_as<bool>;
                          {
                            Trait::sub_overflow(a, b, result)
                          } -> std::same_as<bool>;
                          {
                            Trait::mul_overflow(a, b, result)
                          } -> std::same_as<bool>;
                        };

namespace portable {
struct tag {};
} // namespace portable

namespace gnu {
struct tag {};
} // namespace gnu

namespace msvc {
struct experimental_tag {};
} // namespace msvc

#if defined(__GNUC__) || defined(__clang__)
template <typename T>
  requires std::is_integral_v<T> && std::is_signed_v<T>
struct overflow_trait<T, gnu::tag>;
#endif

#if defined(_MSC_VER)
template <> struct overflow_trait<std::int16_t, msvc::experimental_tag>;
template <> struct overflow_trait<std::int32_t, msvc::experimental_tag>;
#endif

template <> struct overflow_trait<std::int16_t, portable::tag>;
template <> struct overflow_trait<std::int32_t, portable::tag>;

} // namespace lumie::math::overflow_arithmetic
