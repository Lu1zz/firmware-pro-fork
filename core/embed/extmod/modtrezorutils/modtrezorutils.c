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

#include "py/objstr.h"
#include "py/runtime.h"
#ifndef TREZOR_EMULATOR
#include "supervise.h"
#endif
#include "bc_bytewords.h"
#include "se_thd89.h"
#include "secure_heap.h"
#include "sha2.h"
#include "version.h"

#if MICROPY_PY_TREZORUTILS

#include "embed/extmod/modtrezorutils/modtrezorutils-meminfo.h"
#include "embed/extmod/trezorobj.h"

#include <string.h>
#include "blake2s.h"
#include "common.h"
#include "flash.h"
#include "usb.h"

#ifndef TREZOR_EMULATOR
#include "br_check.h"
#include "image.h"
#include "low_power.h"
#include "mini_printf.h"
#endif

// static void ui_progress(mp_obj_t ui_wait_callback, uint32_t current,
//                         uint32_t total) {
//   if (mp_obj_is_callable(ui_wait_callback)) {
//     mp_call_function_2_protected(ui_wait_callback, mp_obj_new_int(current),
//                                  mp_obj_new_int(total));
//   }
// }

/// def consteq(sec: bytes, pub: bytes) -> bool:
///     """
///     Compares the private information in `sec` with public, user-provided
///     information in `pub`.  Runs in constant time, corresponding to a length
///     of `pub`.  Can access memory behind valid length of `sec`, caller is
///     expected to avoid any invalid memory access.
///     """
STATIC mp_obj_t mod_trezorutils_consteq(mp_obj_t sec, mp_obj_t pub) {
  mp_buffer_info_t secbuf = {0};
  mp_get_buffer_raise(sec, &secbuf, MP_BUFFER_READ);
  mp_buffer_info_t pubbuf = {0};
  mp_get_buffer_raise(pub, &pubbuf, MP_BUFFER_READ);

  size_t diff = secbuf.len - pubbuf.len;
  for (size_t i = 0; i < pubbuf.len; i++) {
    const uint8_t *s = (uint8_t *)secbuf.buf;
    const uint8_t *p = (uint8_t *)pubbuf.buf;
    diff |= s[i] - p[i];
  }

  if (diff == 0) {
    return mp_const_true;
  } else {
    return mp_const_false;
  }
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mod_trezorutils_consteq_obj,
                                 mod_trezorutils_consteq);

/// def memcpy(
///     dst: bytearray | memoryview,
///     dst_ofs: int,
///     src: bytes,
///     src_ofs: int,
///     n: int | None = None,
/// ) -> int:
///     """
///     Copies at most `n` bytes from `src` at offset `src_ofs` to
///     `dst` at offset `dst_ofs`. Returns the number of actually
///     copied bytes. If `n` is not specified, tries to copy
///     as much as possible.
///     """
STATIC mp_obj_t mod_trezorutils_memcpy(size_t n_args, const mp_obj_t *args) {
  mp_arg_check_num(n_args, 0, 4, 5, false);

  mp_buffer_info_t dst = {0};
  mp_get_buffer_raise(args[0], &dst, MP_BUFFER_WRITE);
  uint32_t dst_ofs = trezor_obj_get_uint(args[1]);

  mp_buffer_info_t src = {0};
  mp_get_buffer_raise(args[2], &src, MP_BUFFER_READ);
  uint32_t src_ofs = trezor_obj_get_uint(args[3]);

  uint32_t n = 0;
  if (n_args > 4) {
    n = trezor_obj_get_uint(args[4]);
  } else {
    n = src.len;
  }

  size_t dst_rem = (dst_ofs < dst.len) ? dst.len - dst_ofs : 0;
  size_t src_rem = (src_ofs < src.len) ? src.len - src_ofs : 0;
  size_t ncpy = MIN(n, MIN(src_rem, dst_rem));

  memmove(((char *)dst.buf) + dst_ofs, ((const char *)src.buf) + src_ofs, ncpy);

  return mp_obj_new_int(ncpy);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mod_trezorutils_memcpy_obj, 4, 5,
                                           mod_trezorutils_memcpy);

/// def halt(msg: str | None = None) -> None:
///     """
///     Halts execution.
///     """
STATIC mp_obj_t mod_trezorutils_halt(size_t n_args, const mp_obj_t *args) {
  mp_buffer_info_t msg = {0};
  if (n_args > 0 && mp_get_buffer(args[0], &msg, MP_BUFFER_READ)) {
    ensure(secfalse, msg.buf);
  } else {
    ensure(secfalse, "halt");
  }
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mod_trezorutils_halt_obj, 0, 1,
                                           mod_trezorutils_halt);

/// def reset() -> None:
///     """
///     Reset system.
///     """
STATIC mp_obj_t mod_trezorutils_reset(void) {
  restart();
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_reset_obj,
                                 mod_trezorutils_reset);

/// def firmware_hash(
///     challenge: bytes | None = None,
///     callback: Callable[[int, int], None] | None = None,
/// ) -> bytes:
///     """
///     Computes the Blake2s hash of the firmware with an optional challenge as
///     the key.
///     """
STATIC mp_obj_t mod_trezorutils_firmware_hash(size_t n_args,
                                              const mp_obj_t *args) {
  // we use onekey firmware hash
  vstr_t vstr = {0};
  vstr_init_len(&vstr, BLAKE2S_DIGEST_LENGTH);
  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mod_trezorutils_firmware_hash_obj, 0,
                                           2, mod_trezorutils_firmware_hash);

/// def onekey_firmware_hash() -> bytes:
///     """
///     Computes the sha256 hash of the firmware
///     """
STATIC mp_obj_t mod_trezorutils_onekey_firmware_hash(void) {
  vstr_t hash = {0};

  vstr_init_len(&hash, 32);

  memcpy((uint8_t *)hash.buf, get_firmware_hash(), 32);

  return mp_obj_new_str_from_vstr(&mp_type_bytes, &hash);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_onekey_firmware_hash_obj,
                                 mod_trezorutils_onekey_firmware_hash);

/// def firmware_vendor() -> str:
///     """
///     Returns the firmware vendor string from the vendor header.
///     """
STATIC mp_obj_t mod_trezorutils_firmware_vendor(void) {
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  vendor_header vhdr = {0};
  uint32_t size = flash_sector_size(FLASH_SECTOR_FIRMWARE_START);
  const void *data = flash_get_address(FLASH_SECTOR_FIRMWARE_START, 0, size);
  if (data == NULL || sectrue != read_vendor_header(data, &vhdr)) {
    mp_raise_msg(&mp_type_RuntimeError, "Failed to read vendor header.");
  }
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)vhdr.vstr,
                             vhdr.vstr_len);
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_firmware_vendor_obj,
                                 mod_trezorutils_firmware_vendor);

/// def reboot_to_bootloader() -> None:
///     """
///     Reboots to bootloader.
///     """
STATIC mp_obj_t mod_trezorutils_reboot_to_bootloader() {
// actual reboot via trezorhal goes here:
#if !TREZOR_EMULATOR
  reboot_to_boot();
#endif
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_reboot_to_bootloader_obj,
                                 mod_trezorutils_reboot_to_bootloader);

/// def reboot2boardloader() -> None:
///     """
///     Reboots to boardloader.
///     """
STATIC mp_obj_t mod_trezorutils_reboot2boardloader() {
#if !TREZOR_EMULATOR
  reboot_to_board();
#endif
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_reboot2boardloader_obj,
                                 mod_trezorutils_reboot2boardloader);

/// def boot_version() -> str:
///     """
///     Returns the bootloader version string.
///     """
STATIC mp_obj_t mod_trezorutils_boot_version(void) {
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  uint8_t *boot_header = (uint8_t *)BOOTLOADER_START;
  uint32_t version;
  char ver_str[64] = {0};

  memcpy(&version, boot_header + 16, 4);

  mini_snprintf(ver_str, sizeof(ver_str), "%d.%d.%d", (int)(version & 0xFF),
                (int)((version >> 8) & 0xFF), (int)((version >> 16) & 0xFF));
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)ver_str,
                             strlen(ver_str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_boot_version_obj,
                                 mod_trezorutils_boot_version);

/// def boot_hash() -> bytes:
///     """
///     Returns the bootloader hash string.
///     """
STATIC mp_obj_t mod_trezorutils_boot_hash(void) {
  vstr_t vstr = {0};
  vstr_init_len(&vstr, 32);
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#else
  uint8_t *p_code_len = (uint8_t *)(BOOTLOADER_START + 12);
  int len = p_code_len[0] + p_code_len[1] * 256 + p_code_len[2] * 256 * 256;
  sha256_Raw((uint8_t *)(BOOTLOADER_START + 1024), len, (uint8_t *)vstr.buf);
  sha256_Raw((uint8_t *)vstr.buf, 32, (uint8_t *)vstr.buf);

  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_boot_hash_obj,
                                 mod_trezorutils_boot_hash);

/// def board_version() -> str:
///     """
///     Returns the bootloader version string.
///     """
STATIC mp_obj_t mod_trezorutils_board_version(void) {
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else

  char *ver_str = get_boardloader_version();

  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)ver_str,
                             strlen(ver_str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_board_version_obj,
                                 mod_trezorutils_board_version);
/// def board_hash() -> bytes:
///     """
///     Returns the boardloader hash.
///     """
STATIC mp_obj_t mod_trezorutils_board_hash(void) {
  vstr_t vstr = {0};
  vstr_init_len(&vstr, 32);
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#else
  SHA256_CTX context = {0};
  sha256_Init(&context);
  sha256_Update(&context, (uint8_t *)BOARDLOADER_START, BOARDLOADER_SIZE - 32);
  sha256_Update(
        &context,
        (uint8_t*)"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        32);
  sha256_Final(&context, (uint8_t *)vstr.buf);
  sha256_Raw((uint8_t *)vstr.buf, 32, (uint8_t *)vstr.buf);

  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_board_hash_obj,
                                 mod_trezorutils_board_hash);

/// def board_build_id() -> str:
///     """
///     Returns the boardloader build_id.
///     """
STATIC mp_obj_t mod_trezorutils_board_build_id(void) {
#ifdef TREZOR_EMULATOR
  mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  char *str = get_boardloader_build_id();

  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)str, strlen(str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_board_build_id_obj,
                                 mod_trezorutils_board_build_id);

/// def boot_build_id() -> str:
///     """
///     Returns the bootloader build_id.
///     """
STATIC mp_obj_t mod_trezorutils_boot_build_id(void) {
#ifdef TREZOR_EMULATOR
  mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  char *str = get_bootloader_build_id();

  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)str, strlen(str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_boot_build_id_obj,
                                 mod_trezorutils_boot_build_id);

/// def se_version(se_addr: int) -> str:
///     """
///     Returns the se version string.
///     """
STATIC mp_obj_t mod_trezorutils_se_version(mp_obj_t se_addr) {
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  int addr = mp_obj_get_int(se_addr);
  char ver_str[16] = {0};
  se_get_version(addr, ver_str, sizeof(ver_str));

  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)ver_str,
                             strlen(ver_str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_trezorutils_se_version_obj,
                                 mod_trezorutils_se_version);

/// def se_hash(se_addr: int) -> bytes:
///     """
///     Returns the se hash.
///     """
STATIC mp_obj_t mod_trezorutils_se_hash(mp_obj_t se_addr) {
  vstr_t vstr = {0};
  vstr_init_len(&vstr, 32);
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#else
  int addr = mp_obj_get_int(se_addr);
  uint8_t hash_str[32] = {0};
  se_get_hash(addr, hash_str, sizeof(hash_str));
  memcpy(vstr.buf, hash_str, 32);

  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_trezorutils_se_hash_obj,
                                 mod_trezorutils_se_hash);

/// def se_build_id(se_addr: int) -> str:
///     """
///     Returns the se build id string.
///     """
STATIC mp_obj_t mod_trezorutils_se_build_id(mp_obj_t se_addr) {
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  int addr = mp_obj_get_int(se_addr);
  char str[8] = {0};
  se_get_build_id(addr, str, sizeof(str));

  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)str, strlen(str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_trezorutils_se_build_id_obj,
                                 mod_trezorutils_se_build_id);

/// def se_boot_version(se_addr: int) -> str:
///     """
///     Returns the se version string.
///     """
STATIC mp_obj_t mod_trezorutils_se_boot_version(mp_obj_t se_addr) {
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  int addr = mp_obj_get_int(se_addr);
  char ver_str[16] = {0};
  se_get_boot_version(addr, ver_str, sizeof(ver_str));

  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)ver_str,
                             strlen(ver_str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_trezorutils_se_boot_version_obj,
                                 mod_trezorutils_se_boot_version);

/// def se_boot_hash(se_addr: int) -> bytes:
///     """
///     Returns the se hash.
///     """
STATIC mp_obj_t mod_trezorutils_se_boot_hash(mp_obj_t se_addr) {
  vstr_t vstr = {0};
  vstr_init_len(&vstr, 32);
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#else
  int addr = mp_obj_get_int(se_addr);
  uint8_t hash_str[32] = {0};
  se_get_boot_hash(addr, hash_str, sizeof(hash_str));
  memcpy(vstr.buf, hash_str, 32);

  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_trezorutils_se_boot_hash_obj,
                                 mod_trezorutils_se_boot_hash);

/// def se_boot_build_id(se_addr: int) -> str:
///     """
///     Returns the se build id string.
///     """
STATIC mp_obj_t mod_trezorutils_se_boot_build_id(mp_obj_t se_addr) {
#ifdef TREZOR_EMULATOR
  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)"EMULATOR", 8);
#else
  int addr = mp_obj_get_int(se_addr);
  char str[8] = {0};
  se_get_boot_build_id(addr, str, sizeof(str));

  return mp_obj_new_str_copy(&mp_type_str, (const uint8_t *)str, strlen(str));
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mod_trezorutils_se_boot_build_id_obj,
                                 mod_trezorutils_se_boot_build_id);

/// def usb_data_connected() -> bool:
///     """
///     Returns whether USB has been enumerated/configured
///     (and is not just connected by cable without data pins)
///     """
STATIC mp_obj_t mod_trezorutils_usb_data_connected() {
  return usb_configured() == sectrue ? mp_const_true : mp_const_false;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_usb_data_connected_obj,
                                 mod_trezorutils_usb_data_connected);

/// def get_tick() -> int:
///     """
///     Returns sysytick
///     """
STATIC mp_obj_t mod_trezorutils_get_tick(void) {
  uint32_t tick_cnts = 0;

  tick_cnts = HAL_GetTick();

  return mp_obj_new_int_from_uint(tick_cnts);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mod_trezorutils_get_tick_obj,
                                 mod_trezorutils_get_tick);

/// def bytewords_decode(
///    style: int,
///    in_string: str,
/// ) -> bytes:
///     """
///     bytewords decode
///     """
STATIC mp_obj_t mod_trezorutils_bytewords_decode(mp_obj_t type,
                                                 mp_obj_t in_str) {
  int style = mp_obj_get_int(type);
  mp_buffer_info_t inbuf = {0};
  mp_get_buffer_raise(in_str, &inbuf, MP_BUFFER_READ);

  uint8_t *outbuf = NULL;
  size_t outlen = 0;

  if (!bytewords_decode(style, (const char *)inbuf.buf, &outbuf, &outlen)) {
    mp_raise_msg(&mp_type_ValueError, "bytewords decode failed.");
  }

  vstr_t vstr = {0};
  vstr_init_len(&vstr, outlen);
  memcpy(vstr.buf, outbuf, outlen);
  vPortFree(outbuf);

  return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(mod_trezorutils_bytewords_decode_obj,
                                 mod_trezorutils_bytewords_decode);

/// def enter_lowpower(
/// restart: bool,
/// seconds: int,
/// wake_up: bool = False
/// ) ->None:
///     """
///     Enter lowpower mode.
///     """
STATIC mp_obj_t mod_trezorutils_enter_lowpower(size_t n_args,
                                               const mp_obj_t *args) {
  bool val_restart = mp_obj_is_true(args[0]);
  int val_ms = mp_obj_get_int(args[1]);

  bool wake_up = n_args > 2 && args[2] == mp_const_true;

  enter_stop_mode(val_restart, val_ms / 1000, wake_up);
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mod_trezorutils_enter_lowpower_obj,
                                           2, 3,
                                           mod_trezorutils_enter_lowpower);

STATIC mp_obj_str_t mod_trezorutils_revision_obj = {
    {&mp_type_bytes}, 0, sizeof(SCM_REVISION) - 1, (const byte *)SCM_REVISION};

STATIC mp_obj_str_t mod_trezorutils_build_id_obj = {
    {&mp_type_bytes}, 0, sizeof(BUILD_ID) - 1, (const byte *)BUILD_ID};

#define PASTER(s) MP_QSTR_##s
#define MP_QSTR(s) PASTER(s)

MP_DEFINE_STR_OBJ(mp_ONEKEY_VERSION, ONEKEY_VERSION);

/// SCM_REVISION: bytes
/// BUILD_ID: bytes
/// VERSION_MAJOR: int
/// VERSION_MINOR: int
/// VERSION_PATCH: int
/// MODEL: str
/// EMULATOR: bool
/// BITCOIN_ONLY: bool
/// FIRMWARE_SECTORS_COUNT: int
/// BW_STANDARD: int
/// BW_URL: int
/// BW_MINIMAL: int

STATIC const mp_rom_map_elem_t mp_module_trezorutils_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_trezorutils)},
    {MP_ROM_QSTR(MP_QSTR_consteq), MP_ROM_PTR(&mod_trezorutils_consteq_obj)},
    {MP_ROM_QSTR(MP_QSTR_memcpy), MP_ROM_PTR(&mod_trezorutils_memcpy_obj)},
    {MP_ROM_QSTR(MP_QSTR_halt), MP_ROM_PTR(&mod_trezorutils_halt_obj)},
    {MP_ROM_QSTR(MP_QSTR_reboot_to_bootloader),
     MP_ROM_PTR(&mod_trezorutils_reboot_to_bootloader_obj)},
    {MP_ROM_QSTR(MP_QSTR_reboot2boardloader),
     MP_ROM_PTR(&mod_trezorutils_reboot2boardloader_obj)},
    {MP_ROM_QSTR(MP_QSTR_reset), MP_ROM_PTR(&mod_trezorutils_reset_obj)},
    {MP_ROM_QSTR(MP_QSTR_firmware_hash),
     MP_ROM_PTR(&mod_trezorutils_firmware_hash_obj)},
    {MP_ROM_QSTR(MP_QSTR_onekey_firmware_hash),
     MP_ROM_PTR(&mod_trezorutils_onekey_firmware_hash_obj)},
    {MP_ROM_QSTR(MP_QSTR_firmware_vendor),
     MP_ROM_PTR(&mod_trezorutils_firmware_vendor_obj)},
    {MP_ROM_QSTR(MP_QSTR_boot_version),
     MP_ROM_PTR(&mod_trezorutils_boot_version_obj)},
    {MP_ROM_QSTR(MP_QSTR_boot_hash),
     MP_ROM_PTR(&mod_trezorutils_boot_hash_obj)},
    {MP_ROM_QSTR(MP_QSTR_boot_build_id),
     MP_ROM_PTR(&mod_trezorutils_boot_build_id_obj)},
    {MP_ROM_QSTR(MP_QSTR_board_version),
     MP_ROM_PTR(&mod_trezorutils_board_version_obj)},
    {MP_ROM_QSTR(MP_QSTR_board_hash),
     MP_ROM_PTR(&mod_trezorutils_board_hash_obj)},
    {MP_ROM_QSTR(MP_QSTR_board_build_id),
     MP_ROM_PTR(&mod_trezorutils_board_build_id_obj)},
    {MP_ROM_QSTR(MP_QSTR_se_version),
     MP_ROM_PTR(&mod_trezorutils_se_version_obj)},
    {MP_ROM_QSTR(MP_QSTR_se_hash), MP_ROM_PTR(&mod_trezorutils_se_hash_obj)},
    {MP_ROM_QSTR(MP_QSTR_se_build_id),
     MP_ROM_PTR(&mod_trezorutils_se_build_id_obj)},
    {MP_ROM_QSTR(MP_QSTR_se_boot_version),
     MP_ROM_PTR(&mod_trezorutils_se_boot_version_obj)},
    {MP_ROM_QSTR(MP_QSTR_se_boot_hash),
     MP_ROM_PTR(&mod_trezorutils_se_boot_hash_obj)},
    {MP_ROM_QSTR(MP_QSTR_se_boot_build_id),
     MP_ROM_PTR(&mod_trezorutils_se_boot_build_id_obj)},

    {MP_ROM_QSTR(MP_QSTR_usb_data_connected),
     MP_ROM_PTR(&mod_trezorutils_usb_data_connected_obj)},
    {MP_ROM_QSTR(MP_QSTR_get_tick), MP_ROM_PTR(&mod_trezorutils_get_tick_obj)},
    // various built-in constants
    {MP_ROM_QSTR(MP_QSTR_SCM_REVISION),
     MP_ROM_PTR(&mod_trezorutils_revision_obj)},
    {MP_ROM_QSTR(MP_QSTR_BUILD_ID), MP_ROM_PTR(&mod_trezorutils_build_id_obj)},
    {MP_ROM_QSTR(MP_QSTR_VERSION_MAJOR), MP_ROM_INT(VERSION_MAJOR)},
    {MP_ROM_QSTR(MP_QSTR_VERSION_MINOR), MP_ROM_INT(VERSION_MINOR)},
    {MP_ROM_QSTR(MP_QSTR_VERSION_PATCH), MP_ROM_INT(VERSION_PATCH)},
    {MP_ROM_QSTR(MP_QSTR_ONEKEY_VERSION), MP_ROM_PTR(&mp_ONEKEY_VERSION)},
    {MP_ROM_QSTR(MP_QSTR_LVGL_UI), MP_ROM_QSTR(MP_QSTR(LVGL_UI))},
    {MP_ROM_QSTR(MP_QSTR_MODEL), MP_ROM_QSTR(MP_QSTR_T)},

#ifdef TREZOR_EMULATOR
    {MP_ROM_QSTR(MP_QSTR_EMULATOR), mp_const_true},
    MEMINFO_DICT_ENTRIES
#else
    {MP_ROM_QSTR(MP_QSTR_EMULATOR), mp_const_false},
#endif
#if PRODUCTION
    {MP_ROM_QSTR(MP_QSTR_PRODUCTION), mp_const_true},
#else
    {MP_ROM_QSTR(MP_QSTR_PRODUCTION), mp_const_false},
#endif
#if BITCOIN_ONLY
    {MP_ROM_QSTR(MP_QSTR_BITCOIN_ONLY), mp_const_true},
#else
    {MP_ROM_QSTR(MP_QSTR_BITCOIN_ONLY), mp_const_false},
#endif
#if USE_THD89
    {MP_ROM_QSTR(MP_QSTR_USE_THD89), mp_const_true},
#endif
    {MP_ROM_QSTR(MP_QSTR_BW_STANDARD), MP_ROM_INT(bw_standard)},
    {MP_ROM_QSTR(MP_QSTR_BW_URL), MP_ROM_INT(bw_uri)},
    {MP_ROM_QSTR(MP_QSTR_BW_MINIMAL), MP_ROM_INT(bw_minimal)},
    {MP_ROM_QSTR(MP_QSTR_bytewords_decode),
     MP_ROM_PTR(&mod_trezorutils_bytewords_decode_obj)},
    {MP_ROM_QSTR(MP_QSTR_enter_lowpower),
     MP_ROM_PTR(&mod_trezorutils_enter_lowpower_obj)},
};

STATIC MP_DEFINE_CONST_DICT(mp_module_trezorutils_globals,
                            mp_module_trezorutils_globals_table);

const mp_obj_module_t mp_module_trezorutils = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&mp_module_trezorutils_globals,
};

MP_REGISTER_MODULE(MP_QSTR_trezorutils, mp_module_trezorutils,
                   MICROPY_PY_TREZORUTILS);

#endif  // MICROPY_PY_TREZORUTILS
