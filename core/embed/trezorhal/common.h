/*
 * This file is part of the Trezor project, https://trezor.io/
 *
 * Copyright (c) SatoshiLabs
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef __TREZORHAL_COMMON_H__
#define __TREZORHAL_COMMON_H__

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "secbool.h"

typedef enum {
  STAY_REASON_NONE = 0,
  STAY_REASON_REQUIRED_BY_FLAG,
  STAY_REASON_MANUAL_OVERRIDE,
  STAY_REASON_INVALID_DEPENDENCY,
  STAY_REASON_INVALID_NEXT_TARGET,
  STAY_REASON_UPDATE_NEXT_TARGET,
  STAY_REASON_UNKNOWN,
} STAY_REASON;

typedef enum {
  BOOT_TARGET_NORMAL = 0,
  BOOT_TARGET_BOARDLOADER = 0x64616F62,
  BOOT_TARGET_BOOTLOADER = 0x746F6F62,
} volatile BOOT_TARGET;

#define BOOT_TARGET_FLAG_ADDR ((BOOT_TARGET *)(0x30040000 - 4))

#ifndef MIN_8bits
#define MIN_8bits(a, b)                  \
  ({                                     \
    typeof(a) _a = (a);                  \
    typeof(b) _b = (b);                  \
    _a < _b ? (_a & 0xFF) : (_b & 0xFF); \
  })
#endif
#ifndef MIN
#define MIN(a, b)       \
  ({                    \
    typeof(a) _a = (a); \
    typeof(b) _b = (b); \
    _a < _b ? _a : _b;  \
  })
#endif
#ifndef MAX
#define MAX(a, b)       \
  ({                    \
    typeof(a) _a = (a); \
    typeof(b) _b = (b); \
    _a > _b ? _a : _b;  \
  })
#endif

extern const uint8_t toi_icon_warning[321];

void shutdown(void);

void restart(void);

void reboot_to_board(void);

void reboot_to_boot(void);

void __attribute__((noreturn))
__fatal_error(const char *expr, const char *msg, const char *file, int line,
              const char *func);
void __attribute__((noreturn))
error_shutdown(const char *line1, const char *line2, const char *line3,
               const char *line4);

void error_reset(const char *line1, const char *line2, const char *line3,
                 const char *line4);
void error_pin_max_prompt(void);

// cannot use like this due to code size issue
// waiting until we could outmize out some space
// #if PRODUCTION
#define ensure(expr, msg) \
  (((expr) == sectrue)    \
       ? (void)0          \
       : __fatal_error(#expr, msg, __FILE__, __LINE__, __func__))
// #else
// #define ensure(expr, msg) (((expr) == sectrue) ? (void)0 :
// dbgprintf_Wait("%s\n%s\n",#expr, msg)) #endif

#define ensure_ex(expr, ret, msg) \
  (((expr) == ret) ? (void)0      \
                   : __fatal_error(#expr, msg, __FILE__, __LINE__, __func__))

void hal_delay(uint32_t ms);
uint32_t hal_ticks_ms();

void clear_otg_hs_memory(void);

extern uint32_t __stack_chk_guard;

void collect_hw_entropy(void);
#define HW_ENTROPY_LEN (12 + 32)
extern uint8_t HW_ENTROPY_DATA[HW_ENTROPY_LEN];

// the following functions are defined in util.s

void memset_reg(volatile void *start, volatile void *stop, uint32_t val);
void jump_to(uint32_t address);
void jump_to_unprivileged(uint32_t address);
void jump_to_with_flag(uint32_t address, uint32_t register_flag);
void ensure_compatible_settings(void);

bool check_all_ones(const void *data, int len);

bool check_all_zeros(const void *data, int len);

int compare_str_version(const char *version1, const char *version2);

#endif
