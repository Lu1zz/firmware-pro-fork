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

#include <string.h>

#include "blake2s.h"
#include "common.h"
#include "compiler_traits.h"
#include "display.h"
#include "emmc.h"
#include "emmc_fs.h"
#include "flash.h"
#include "fw_keys.h"
#include "i2c.h"
#include "image.h"
#include "lowlevel.h"
#include "memzero.h"
#include "mipi_lcd.h"
#include "mpu.h"
#include "rng.h"
#include "sdcard.h"
#include "sdram.h"
#include "systick.h"
#include "touch.h"
#include "usart.h"
#include "usb.h"
#include "usbd_desc.h"
#include "util_macros.h"
#include "version.h"

#include STM32_HAL_H

// helper macros
#define _TO_STR(x) #x
#define TO_STR(x) _TO_STR(x)

// defines
#define VERSION_STR \
  TO_STR(VERSION_MAJOR) "." TO_STR(VERSION_MINOR) "." TO_STR(VERSION_PATCH)
#define PIXEL_STEP 5

typedef struct {
  char version[16];
  char build_id[16];
} board_info_t;

const board_info_t board_info __attribute__((section(".version_section"))) = {
    .version = VERSION_STR,
    .build_id = BUILD_COMMIT,
};

// clang-format off
static const uint8_t toi_icon_onekey[] = {
    // magic
    'T', 'O', 'I', 'f',
    // width (16-bit), height (16-bit)
    0x80, 0x00, 0x80, 0x00,
    // compressed data length (32-bit)
    0x4c, 0x05, 0x00, 0x00,
    // compressed data
    0xed, 0x92, 0x2b, 0x8e, 0xeb, 0x30, 0x14, 0x86, 0x0d, 0x0c, 0x0c, 0x02, 0x0c, 0xba, 0x01, 0x2f, 0x21, 0x5b, 0x30, 0x1c, 0x58, 0x38, 0x34, 0x68, 0x34, 0x1a, 0x70, 0x15, 0x05, 0x44, 0x95, 0x49, 0x14, 0x05, 0x54, 0x57, 0x01, 0x55, 0x35, 0x28, 0xb4, 0x30, 0x70, 0xa0, 0xb7, 0x90, 0x25, 0x64, 0x03, 0x03, 0x0c, 0x02, 0x0c, 0x02, 0x7c, 0x55, 0x5d, 0x55, 0xd3, 0x36, 0x7d, 0x24, 0xed, 0xc9, 0x73, 0xf2, 0x85, 0xb5, 0xb6, 0xff, 0xf3, 0x9d, 0x73, 0x10, 0x9a, 0x99, 0x99, 0x99, 0x99, 0x99, 0x99, 0x99, 0x99, 0x99, 0x81, 0x85, 0xe1, 0xe5, 0xda, 0xb1, 0x42, 0x9a, 0x14, 0x49, 0x21, 0x75, 0x5e, 0xee, 0x3f, 0x73, 0xc6, 0xfe, 0xb7, 0xcc, 0x97, 0x3a, 0xf5, 0x92, 0x22, 0xa4, 0x8e, 0xc5, 0x89, 0x1d, 0x8d, 0xd9, 0x99, 0x06, 0x9c, 0xbc, 0x7f, 0x24, 0x45, 0xd5, 0xb4, 0x09, 0x99, 0x9f, 0x7a, 0x21, 0xe5, 0x84, 0x06, 0x63, 0xf2, 0xde, 0x6e, 0x32, 0xdf, 0x00, 0x93, 0xf9, 0xdb, 0xcd, 0x72, 0x3d, 0xe4, 0x3e, 0xd0, 0xc0, 0xb1, 0xa4, 0x56, 0xc2, 0xb4, 0x4a, 0xea, 0xbd, 0x7e, 0x0f, 0xaf, 0x0b, 0xfb, 0x99, 0xb7, 0x6d, 0xfe, 0x83, 0x12, 0x49, 0xc1, 0xc9, 0x70, 0xdc, 0xa5, 0x36, 0x3d, 0x20, 0xf5, 0xeb, 0xf7, 0x6f, 0x75, 0x3f, 0x90, 0x97, 0xfd, 0xf5, 0x80, 0xe1, 0x7e, 0xdd, 0x0f, 0xa4, 0x1e, 0xc3, 0xdd, 0xdb, 0xbf, 0x7f, 0x28, 0x61, 0x06, 0xc3, 0x4a, 0xfd, 0xc6, 0xc9, 0x1f, 0x93, 0xf9, 0x5d, 0x6d, 0x01, 0x27, 0x43, 0x9a, 0xfc, 0x0f, 0x79, 0x69, 0x47, 0x5d, 0xec, 0xbd, 0x19, 0x30, 0x6e, 0xdc, 0xae, 0xfd, 0x4a, 0x99, 0x81, 0xb3, 0x52, 0xbf, 0xd9, 0xbe, 0xcd, 0x0e, 0x0c, 0x7b, 0xf3, 0x8f, 0x71, 0x63, 0x78, 0x7b, 0x3b, 0x32, 0x23, 0x82, 0x13, 0x58, 0x7b, 0x86, 0xf3, 0x72, 0x4c, 0xfe, 0x4a, 0x30, 0x0c, 0xe9, 0x9f, 0xf9, 0x66, 0x64, 0x48, 0x0d, 0x67, 0xbf, 0x52, 0x66, 0x84, 0xb8, 0x31, 0x8c, 0x3d, 0xc3, 0x66, 0x94, 0x28, 0xc1, 0x30, 0x84, 0x7f, 0xea, 0x99, 0x91, 0x22, 0xf5, 0xf3, 0xf6, 0x8e, 0x65, 0x46, 0x0c, 0x27, 0xcf, 0xfa, 0xe7, 0x25, 0x5c, 0x35, 0x79, 0x79, 0xeb, 0x1b, 0xe2, 0x06, 0x40, 0x4e, 0x3f, 0x29, 0x6e, 0x25, 0x31, 0x3c, 0xc4, 0x0d, 0x90, 0x1a, 0xae, 0x92, 0x97, 0xb7, 0x3e, 0xfc, 0x9f, 0xd9, 0x00, 0x4e, 0xe0, 0xea, 0x50, 0xe2, 0x76, 0x56, 0x5b, 0xfe, 0xcf, 0x6c, 0xc0, 0x6e, 0x01, 0x57, 0x45, 0x52, 0xf4, 0xe5, 0xbf, 0xdd, 0x3c, 0x66, 0x4f, 0x03, 0x25, 0xe0, 0xaa, 0x78, 0x79, 0xeb, 0xcb, 0x5f, 0x09, 0x1a, 0x3c, 0xe2, 0xef, 0x58, 0x90, 0x55, 0xdc, 0xab, 0xa1, 0x3d, 0x7f, 0x63, 0x1c, 0xeb, 0x11, 0xff, 0xd4, 0x83, 0xab, 0xe0, 0xeb, 0xf3, 0x5e, 0x5a, 0x9b, 0xfe, 0x52, 0x37, 0xb7, 0xa7, 0x01, 0x64, 0x05, 0x21, 0x65, 0xf8, 0xf8, 0xab, 0x6e, 0x43, 0x9b, 0xfe, 0x4a, 0xdc, 0xdb, 0xbe, 0x2a, 0xcb, 0xb5, 0x69, 0x91, 0xa4, 0xe8, 0xd2, 0xdf, 0x18, 0x4e, 0x9a, 0xfa, 0x6f, 0x37, 0x53, 0xf2, 0xdf, 0x6e, 0x9a, 0xfa, 0x67, 0xfe, 0x94, 0xfc, 0x33, 0xbf, 0x99, 0x3d, 0x0d, 0x8c, 0x99, 0x92, 0xbf, 0x31, 0x34, 0x68, 0xe2, 0xcf, 0xc9, 0xd4, 0xfc, 0x39, 0x69, 0xe2, 0x1f, 0xd2, 0xa9, 0xf9, 0xbb, 0x71, 0x13, 0xff, 0xd4, 0x9b, 0x9a, 0x7f, 0x35, 0xf1, 0x16, 0x99, 0x3f, 0x35, 0xff, 0xbc, 0x6c, 0xe2, 0x6f, 0xcc, 0xd4, 0xfc, 0x8d, 0xa9, 0x6f, 0x6f, 0x47, 0x53, 0xf4, 0x67, 0xb8, 0xae, 0x3f, 0x27, 0x53, 0xf4, 0x7f, 0x79, 0xab, 0xeb, 0xef, 0x58, 0x53, 0xf4, 0x77, 0xac, 0xba, 0xfe, 0x21, 0x9d, 0xa2, 0x7f, 0x48, 0xeb, 0xfa, 0xef, 0x16, 0x53, 0xf4, 0xaf, 0x66, 0x5e, 0x23, 0xf5, 0x7e, 0xb7, 0xbf, 0xd4, 0x53, 0xf4, 0x97, 0xba, 0xae, 0x7f, 0xe6, 0xb7, 0x5f, 0x8b, 0x63, 0x9d, 0x7e, 0x6e, 0xdc, 0x76, 0x66, 0x5e, 0xd6, 0xf5, 0xcf, 0x4b, 0x33, 0x41, 0x66, 0xff, 0xba, 0xfe, 0xdd, 0x55, 0xf4, 0xff, 0xeb, 0x2a, 0x6f, 0x28, 0xfe, 0x52, 0xbf, 0x7f, 0xd8, 0x11, 0x0d, 0x7e, 0x12, 0xed, 0xe8, 0xfd, 0x43, 0xea, 0xe9, 0xfb, 0x2b, 0x11, 0xd2, 0x63, 0xef, 0x53, 0x18, 0xde, 0x2d, 0xa6, 0xec, 0x2f, 0x35, 0xc3, 0xf7, 0xb2, 0xdb, 0xec, 0x41, 0xbf, 0xfe, 0x6e, 0x5c, 0x37, 0x3f, 0xa4, 0x53, 0xf3, 0x57, 0x62, 0xb9, 0x46, 0x0d, 0x58, 0xae, 0x95, 0x98, 0x92, 0x7f, 0x33, 0xfb, 0xff, 0x1d, 0x98, 0x8e, 0x7f, 0x48, 0xd1, 0x03, 0xb8, 0x71, 0x5f, 0xfe, 0x79, 0x09, 0x99, 0x9a, 0x14, 0x97, 0x53, 0x68, 0xc0, 0x89, 0x63, 0x39, 0x16, 0x27, 0x34, 0xb8, 0x7c, 0x42, 0x6a, 0xc8, 0x3a, 0xf2, 0xb2, 0x1f, 0x7f, 0x86, 0xab, 0x09, 0x9c, 0x9c, 0xba, 0xa5, 0x9e, 0x1d, 0x55, 0x4f, 0x31, 0xac, 0xc4, 0xd8, 0xfd, 0x2f, 0x4d, 0xff, 0xef, 0x9f, 0x4b, 0x27, 0xff, 0xfe, 0xa9, 0x9e, 0x0c, 0x29, 0x5c, 0x25, 0x99, 0x5f, 0xd7, 0x1f, 0x72, 0xef, 0xaa, 0xd3, 0xbf, 0xfe, 0xba, 0xd4, 0xd5, 0x0d, 0x80, 0xab, 0xa4, 0xfa, 0xfa, 0x35, 0x76, 0x8b, 0xf6, 0x32, 0x2f, 0xcf, 0xfe, 0xfa, 0x0e, 0xc0, 0xcd, 0xe2, 0xeb, 0xb3, 0x7b, 0x7f, 0x37, 0x6e, 0x3a, 0x4f, 0x4e, 0x4e, 0x6f, 0xb8, 0x31, 0x54, 0x2d, 0x49, 0x51, 0xd7, 0x3f, 0xa4, 0x50, 0x99, 0xe7, 0x36, 0xf7, 0x3b, 0x7b, 0xbe, 0x31, 0x9c, 0x40, 0xd5, 0x12, 0xd2, 0xba, 0xfe, 0x8e, 0x05, 0x95, 0x49, 0x83, 0xe3, 0x77, 0x69, 0x70, 0xff, 0x86, 0x12, 0xcd, 0xef, 0xd4, 0xc3, 0xb1, 0xea, 0xfa, 0x2f, 0xd7, 0x30, 0x89, 0x4a, 0x3c, 0x32, 0x4b, 0x3b, 0x3a, 0xbd, 0xa5, 0x44, 0x3b, 0xbb, 0x78, 0x1d, 0x86, 0x61, 0x12, 0xf3, 0xf2, 0x91, 0xbe, 0x9e, 0xcf, 0x29, 0x2f, 0x61, 0xaa, 0x39, 0xef, 0xeb, 0x2d, 0xda, 0xf1, 0x77, 0xac, 0x3a, 0xb7, 0x5e, 0xde, 0xda, 0xf1, 0x47, 0x0d, 0x80, 0xc9, 0x54, 0xe2, 0xf4, 0x55, 0x3b, 0x7a, 0x64, 0x4f, 0x95, 0x80, 0xa8, 0x25, 0xf3, 0x9b, 0xf8, 0xef, 0x16, 0x30, 0x3d, 0xa7, 0xc1, 0xf1, 0xab, 0x34, 0xa8, 0xe3, 0x72, 0x5a, 0x09, 0x0d, 0x60, 0x2a, 0xf9, 0xfa, 0x6c, 0xe2, 0xef, 0xc6, 0x30, 0xa9, 0xe7, 0xb3, 0x94, 0xfa, 0xde, 0x8d, 0xa4, 0x38, 0xbd, 0xc1, 0x09, 0x4c, 0x25, 0x21, 0x6d, 0xe2, 0x0f, 0x95, 0xea, 0xc6, 0x4d, 0xdf, 0x65, 0xb8, 0x9b, 0x49, 0xdc, 0x06, 0x6a, 0xeb, 0xa4, 0x3e, 0x7f, 0x79, 0xbb, 0x69, 0x36, 0xa5, 0xfb, 0x1b, 0x53, 0x0f, 0x1a, 0xa0, 0x46, 0x64, 0x3e, 0x4c, 0xae, 0x1d, 0x9d, 0xbf, 0xbc, 0x5b, 0x5c, 0x3b, 0xbb, 0x5b, 0x9c, 0x9f, 0x65, 0x18, 0xa6, 0x8a, 0xcc, 0x47, 0x0d, 0xb9, 0x3d, 0xa7, 0xfa, 0x24, 0x45, 0xf5, 0xed, 0x90, 0x5e, 0x3a, 0xb9, 0xdd, 0x54, 0x4f, 0x5e, 0xef, 0x55, 0x33, 0x2e, 0xbd, 0x7d, 0x1b, 0x4e, 0x0c, 0x10, 0x0c, 0x57, 0x5f, 0x67, 0x78, 0xb7, 0x50, 0xe2, 0x70, 0x42, 0x89, 0xa4, 0xe0, 0xe4, 0xd2, 0x29, 0xa8, 0x1a, 0x5e, 0xde, 0x9a, 0xfa, 0xd3, 0xe0, 0xa7, 0xbe, 0xe7, 0x90, 0xfa, 0x7a, 0x8f, 0x39, 0x59, 0xae, 0xed, 0x88, 0x06, 0x97, 0xff, 0x97, 0x1a, 0xca, 0xff, 0x5a, 0xc2, 0x2d, 0xe0, 0xd2, 0x57, 0x0a, 0x3d, 0xc0, 0x4a, 0x41, 0xe5, 0x7f, 0x7d, 0x3e, 0x92, 0xef, 0x58, 0x06, 0x8c, 0xd7, 0xef, 0xa6, 0xe9, 0xaf, 0xdf, 0x7d, 0xa6, 0xef, 0xa1, 0x81, 0x12, 0x7d, 0xd5, 0x00, 0x69, 0xaf, 0x04, 0x0d, 0xd0, 0x43, 0x6c, 0x37, 0x06, 0x90, 0x95, 0xaa, 0x9b, 0x0b, 0xb7, 0xf9, 0x7b, 0x92, 0x02, 0x3d, 0x08, 0x27, 0x06, 0x94, 0xbc, 0x64, 0xf8, 0x5e, 0xa6, 0x1d, 0x49, 0x0d, 0x9b, 0xca, 0x09, 0x7a, 0x18, 0xe8, 0x5a, 0xf6, 0xd3, 0xb8, 0xde, 0x03, 0x4e, 0x76, 0x0b, 0xe8, 0x3c, 0xa9, 0xd1, 0x13, 0x40, 0x6f, 0xc0, 0x7f, 0x32, 0x3f, 0xa4, 0x9c, 0xd0, 0xe0, 0x90, 0x42, 0x03, 0x4e, 0x56, 0x0a, 0xbe, 0xd7, 0x7b, 0x5e, 0xbf, 0xd1, 0x53, 0xb4, 0x53, 0xd5, 0x81, 0xbc, 0xcc, 0xcb, 0x76, 0xdf, 0x47, 0x4f, 0xd2, 0xce, 0x06, 0x74, 0xc5, 0xb3, 0xd3, 0x6f, 0x7f, 0x03, 0xda, 0x24, 0x29, 0x10, 0x00, 0x0c, 0x2b, 0x31, 0x4e, 0x7f, 0x86, 0x11, 0x08, 0x6e, 0x3c, 0x46, 0xfb, 0x90, 0x22, 0x30, 0xa4, 0x1e, 0x9b, 0x7d, 0xe6, 0x23, 0x40, 0x18, 0x56, 0x62, 0x4c, 0xf6, 0x79, 0xc9, 0x30, 0x02, 0x85, 0x93, 0x31, 0xf9, 0xdb, 0x11, 0x02, 0xc7, 0x8d, 0xc7, 0x62, 0xef, 0xc6, 0xa8, 0x15, 0x42, 0x3a, 0x06, 0xfb, 0x90, 0xa2, 0xd6, 0x18, 0x7e, 0x07, 0xda, 0xb4, 0xdf, 0xe3, 0xc6, 0x43, 0xb6, 0x6f, 0x6b, 0xf3, 0x8f, 0xb1, 0xa3, 0xbc, 0x1c, 0xa2, 0xbb, 0x12, 0x9c, 0xa0, 0x4e, 0x60, 0x38, 0xf3, 0x87, 0x66, 0x2f, 0x35, 0xc3, 0xa8, 0x43, 0x42, 0x3a, 0xa4, 0xc9, 0x77, 0xb1, 0xf7, 0xd5, 0x2d, 0x48, 0xbd, 0xdf, 0x38, 0xf9, 0x63, 0x1c, 0x2b, 0x2f, 0xfb, 0x75, 0xe7, 0x04, 0xf5, 0x8c, 0x63, 0x49, 0xfd, 0x5b, 0xdd, 0x0f, 0x70, 0xb2, 0x5b, 0x28, 0xd1, 0x95, 0xb9, 0x12, 0xdb, 0xcd, 0x70, 0xdc, 0x0f, 0xd0, 0xc0, 0xb1, 0x52, 0xaf, 0x6d, 0x73, 0xa9, 0x1d, 0x8b, 0x06, 0x68, 0xb0, 0xd0, 0x60, 0xb9, 0xde, 0x6e, 0x32, 0x1f, 0xda, 0x3c, 0xf3, 0xf7, 0x33, 0x1f, 0xb2, 0xf9, 0x79, 0x1f, 0x38, 0x09, 0x69, 0xea, 0x3d, 0xd7, 0x89, 0xbc, 0x4c, 0x8a, 0xf7, 0x8f, 0x31, 0x79, 0x5f, 0xc2, 0x8e, 0x38, 0x71, 0xac, 0x90, 0x26, 0x45, 0xea, 0x49, 0x9d, 0xf9, 0x79, 0x99, 0x97, 0x55, 0xd3, 0xfd, 0x27, 0x75, 0x52, 0x24, 0x45, 0x48, 0x1d, 0x6b, 0xb9, 0x66, 0x18, 0xcd, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0x00, 0xf3, 0x0f,
};

static const uint8_t toi_icon_safeos[] = {
    // magic
    'T', 'O', 'I', 'f',
    // width (16-bit), height (16-bit)
    0x8c, 0x00, 0x1e, 0x00,
    // compressed data length (32-bit)
    0x4c, 0x05, 0x00, 0x00,
    // compressed data
    0xAD, 0x92, 0xA1, 0xAE, 0xAC, 0x3C, 0x10, 0xC7, 0x8F, 0x40, 0x20, 0x10, 0x15, 0x2B, 0x10, 0xC7, 0xF0, 0x08, 0xBC, 0x02, 0x8F, 0x80, 0xFC, 0x2C, 0x4F, 0x70, 0x42, 0x56, 0x10, 0x82, 0x21, 0x04, 0x41, 0x4E, 0x10, 0x84, 0xAC, 0xB8, 0xC1, 0xAE, 0x5C, 0xB9, 0x12, 0x8B, 0x44, 0x5E, 0x89, 0xBD, 0xE2, 0x8A, 0x0A, 0x04, 0x02, 0xC1, 0x97, 0x86, 0x34, 0x33, 0x2D, 0x2D, 0xB0, 0xF7, 0xEC, 0xA0, 0x68, 0x67, 0xA6, 0xF3, 0xFF, 0xCD, 0xFF, 0xE3, 0x03, 0x82, 0xA4, 0x9E, 0x59, 0x57, 0x8F, 0x6B, 0x3B, 0xB5, 0xD3, 0xE3, 0x9A, 0x11, 0xCF, 0xFC, 0x78, 0x63, 0xE0, 0xEE, 0x7E, 0xF1, 0x9E, 0x9E, 0x6E, 0x1E, 0x96, 0xCD, 0xC8, 0x27, 0xAE, 0x2B, 0xBF, 0x70, 0x8C, 0xB3, 0xD3, 0x40, 0x65, 0x33, 0x86, 0xA5, 0xAE, 0x8E, 0xA4, 0x31, 0xA5, 0xC9, 0x22, 0xC5, 0x30, 0x07, 0xD6, 0x7B, 0x14, 0xF8, 0x05, 0xEE, 0x9E, 0x91, 0x9F, 0x53, 0x8E, 0xE9, 0x30, 0x2F, 0x8A, 0x68, 0xA7, 0xA3, 0x99, 0x1D, 0xE3, 0x7E, 0x51, 0xD5, 0x6D, 0xB7, 0xE5, 0x18, 0x7D, 0xB4, 0x68, 0x62, 0x98, 0xCF, 0xEE, 0x40, 0x1F, 0x31, 0x15, 0x7B, 0xFE, 0x94, 0x4B, 0x60, 0x6D, 0x77, 0x78, 0x76, 0x66, 0x71, 0x43, 0x62, 0x7C, 0x7F, 0x89, 0xEC, 0xD5, 0xE4, 0xE1, 0x15, 0x37, 0xFF, 0x99, 0xDB, 0xE5, 0x8E, 0x3F, 0xE1, 0x42, 0xD2, 0x66, 0x5C, 0x4E, 0x44, 0x4C, 0xCF, 0xCD, 0x22, 0x46, 0x1F, 0x91, 0x94, 0xE7, 0x8A, 0xAE, 0xA2, 0x49, 0x67, 0x77, 0xB6, 0xC8, 0xF4, 0x67, 0x9E, 0x69, 0x27, 0xDC, 0xFD, 0x7E, 0xB9, 0x5F, 0x8E, 0x9C, 0xBE, 0x47, 0x45, 0xEF, 0xEC, 0x33, 0x64, 0x44, 0x07, 0xFC, 0xF9, 0xEC, 0xEC, 0xDF, 0xBF, 0xC4, 0xAA, 0x66, 0x5C, 0x33, 0x1D, 0x03, 0xEB, 0xF7, 0x4C, 0xDE, 0xC1, 0x33, 0xF1, 0x04, 0x8F, 0xEB, 0xBF, 0x2B, 0x79, 0x8F, 0x4F, 0xD6, 0x78, 0x5C, 0xC5, 0x1D, 0x66, 0xC4, 0x33, 0xD7, 0x0D, 0x93, 0xD4, 0x33, 0xC5, 0x0D, 0x2F, 0x4B, 0x58, 0x8A, 0xD5, 0x81, 0x05, 0x77, 0x75, 0xC5, 0x9D, 0x41, 0xD2, 0xC0, 0xC2, 0xBC, 0xFC, 0x42, 0xCC, 0xDD, 0xBA, 0x22, 0x23, 0x90, 0x0D, 0xC4, 0x5E, 0x0B, 0xCF, 0x84, 0xFE, 0x3F, 0xA5, 0x12, 0x53, 0xAC, 0x3A, 0x23, 0xE0, 0x79, 0x1E, 0x8E, 0x21, 0xB2, 0x71, 0x73, 0x7C, 0xFB, 0xBC, 0xC9, 0xAE, 0x80, 0x3A, 0x70, 0xC1, 0x3A, 0x27, 0x68, 0x97, 0x73, 0xF1, 0x7E, 0x3A, 0x5B, 0x7C, 0x01, 0x77, 0x74, 0x8C, 0xED, 0x7C, 0x2A, 0x2E, 0x9D, 0x7D, 0xE4, 0x2C, 0xD6, 0x4B, 0x7F, 0x8F, 0x9D, 0xCD, 0xB7, 0xAA, 0x0A, 0xBC, 0xCD, 0x76, 0xC2, 0x37, 0xA0, 0x7D, 0xBB, 0x65, 0xC7, 0xA0, 0xC9, 0xEA, 0xC1, 0xD5, 0x49, 0xC0, 0x57, 0xE5, 0x72, 0x92, 0xD2, 0xA4, 0x19, 0x55, 0x5E, 0x21, 0x69, 0x58, 0xB6, 0xD3, 0xDA, 0x8B, 0x75, 0x6B, 0xA7, 0xC0, 0x12, 0x33, 0xEA, 0xAA, 0x19, 0x9B, 0x91, 0x93, 0x65, 0x39, 0xEC, 0x9F, 0x7D, 0xB2, 0x7A, 0xCF, 0x6C, 0x46, 0xDE, 0x69, 0x59, 0xFA, 0xA8, 0xAE, 0x54, 0x7C, 0xB0, 0x13, 0xC2, 0x72, 0x8F, 0x70, 0x5D, 0xA9, 0x7D, 0xFE, 0xE7, 0x93, 0x9F, 0xAA, 0xFA, 0x07, 0x16, 0x4D, 0xC0, 0x83, 0xD0, 0x43, 0x64, 0xBB, 0x1F, 0x61, 0x09, 0x3A, 0x20, 0x86, 0x19, 0xBF, 0x07, 0x53, 0xC8, 0x81, 0x67, 0x75, 0x8C, 0x76, 0x52, 0xE5, 0xC4, 0x54, 0xDE, 0x03, 0xDC, 0xA9, 0x9C, 0x2D, 0x6F, 0x53, 0xA5, 0x0A, 0x26, 0x52, 0x7B, 0x00, 0xFB, 0x3E, 0xB0, 0xF4, 0xB3, 0xE8, 0x22, 0xA6, 0x3A, 0xC5, 0x34, 0x71, 0xF3, 0x57, 0xB8, 0xB8, 0xB9, 0x8A, 0xAF, 0x4A, 0xBD, 0x5F, 0xC0, 0x8D, 0x6A, 0xDB, 0xF2, 0xDE, 0x20, 0x1B, 0xD4, 0x3E, 0x6F, 0x30, 0xE7, 0x51, 0x0F, 0xCC, 0x96, 0xD1, 0xF5, 0x8B, 0x7F, 0xA7, 0xB2, 0xBE, 0xC8, 0xE7, 0x38, 0xE6, 0xE2, 0x18, 0x7A, 0x2A, 0x2C, 0xBE, 0xBF, 0xE0, 0x55, 0xF0, 0x75, 0x67, 0x1F, 0x6F, 0x0E, 0xAB, 0x0A, 0x2C, 0x7E, 0xEA, 0x99, 0x22, 0x77, 0xEC, 0xDB, 0x6D, 0x64, 0x44, 0x9E, 0xE7, 0x71, 0x0D, 0x2C, 0x1D, 0x4F, 0xC7, 0x80, 0xBC, 0x61, 0x0E, 0x4B, 0x37, 0x77, 0x0C, 0xCF, 0xBC, 0x5F, 0xE0, 0x94, 0x7B, 0xF4, 0x79, 0xEB, 0xEC, 0xCE, 0xEE, 0x23, 0x20, 0xC6, 0xFE, 0xD9, 0xC7, 0x3D, 0x35, 0xCC, 0x70, 0x97, 0x11, 0xC6, 0x93, 0xA4, 0x7E, 0x01, 0xA7, 0xD8, 0x59, 0xED, 0xC4, 0xCF, 0xC2, 0xF2, 0x8C, 0xA7, 0x21, 0x9F, 0xCF, 0x23, 0x9E, 0x72, 0x05, 0x7B, 0x74, 0xE4, 0x6C, 0xEE, 0x1D, 0x15, 0x1D, 0xC7, 0xE8, 0xEC, 0xF5, 0xBE, 0x8F, 0xC0, 0xA1, 0x78, 0x9F, 0xC3, 0x8C, 0xF3, 0x61, 0x47, 0xF2, 0x9E, 0xC1, 0x77, 0xC3, 0x8C, 0xDF, 0x21, 0x29, 0xB0, 0x6C, 0x27, 0x7E, 0x0A, 0xEE, 0x3B, 0x76, 0x34, 0x0B, 0xD8, 0x54, 0x33, 0xE2, 0xE9, 0x31, 0x75, 0xD8, 0x8A, 0x8E, 0x0E, 0xA8, 0x92, 0x79, 0xC6, 0x54, 0xE5, 0x99, 0xFB, 0x45, 0xD4, 0xC2, 0xD4, 0x40, 0xD5, 0x39, 0x2E, 0x30, 0x21, 0x38, 0x9D, 0xF7, 0xA7, 0x89, 0xEC, 0x18, 0xE0, 0xA2, 0xDF, 0x2F, 0x8E, 0x8C, 0xA8, 0xB8, 0xE8, 0xC8, 0xAC, 0x5A, 0xE5, 0x39, 0x58, 0x04, 0xD6, 0xEF, 0x5F, 0xBA, 0xFC, 0xAD, 0x6B, 0x18, 0x07, 0xF9, 0xE4, 0x35, 0x2E, 0x70, 0x2E, 0xFA, 0x4B, 0x76, 0x70, 0x58, 0xBE, 0x97, 0xCB, 0xAA, 0x55, 0xC7, 0xE6, 0xFB, 0x4B, 0xD5, 0xCB, 0xCD, 0xEB, 0x4A, 0x55, 0x31, 0xCC, 0x5B, 0x0A, 0x2B, 0x1B, 0x37, 0x0F, 0xAC, 0x8C, 0x34, 0x63, 0x1F, 0xC1, 0x86, 0xCF, 0x71, 0x09, 0x4B, 0x70, 0x71, 0x3B, 0xC9, 0x1F, 0x74, 0xE3, 0xAA, 0x80, 0x8B, 0x6A, 0xAB, 0xDB, 0x78, 0xDE, 0x78, 0x7E, 0x5D, 0xA9, 0xEE, 0xFD, 0xE2, 0x7E, 0xC1, 0x33, 0xEF, 0x93, 0x59, 0xE9, 0x84, 0xA5, 0xEC, 0x1D, 0x99, 0x39, 0x49, 0x63, 0x0A, 0x3B, 0x95, 0xE3, 0x0C, 0x97, 0xBA, 0x5A, 0x4E, 0xC5, 0xF3, 0x76, 0x4E, 0xA7, 0x1C, 0x7D, 0x24, 0x3B, 0x4E, 0x15, 0x9E, 0x79, 0xBF, 0xC8, 0x4E, 0xD8, 0xF7, 0xA3, 0x63, 0xDC, 0x2F, 0x38, 0x1B, 0x3B, 0x26, 0xA6, 0xFB, 0x5A, 0xCE, 0x70, 0x11, 0xBB, 0xEB, 0x83, 0x57, 0x65, 0x04, 0xDC, 0x7B, 0x4C, 0xC5, 0x31, 0xCE, 0xEA, 0x5C, 0x67, 0x04, 0xEA, 0xCB, 0xD2, 0x4E, 0xB8, 0x8F, 0x3A, 0x1F, 0xB2, 0xC1, 0xBD, 0x8F, 0xAB, 0x6A, 0x7E, 0xEC, 0xB0, 0x77, 0x72, 0xE1, 0xEE, 0xC0, 0xB3, 0x1C, 0x2B, 0x85, 0xEE, 0x5B, 0x8A, 0x78, 0xC3, 0x6A, 0xFF, 0xAE, 0x19, 0x7E, 0xD1, 0x4E, 0x34, 0x51, 0x67, 0xB7, 0x13, 0xCF, 0xCD, 0xC8, 0xD6, 0x2B, 0x34, 0x79, 0xDE, 0x32, 0x12, 0x58, 0x2B, 0xD5, 0xD7, 0xB8, 0x84, 0x25, 0x3F, 0x7F, 0xDE, 0x1C, 0x43, 0xFF, 0xC1, 0x5C, 0x34, 0xE1, 0x15, 0x7D, 0x74, 0xDE, 0x2D, 0xCD, 0x88, 0x89, 0xC4, 0x94, 0x26, 0xD8, 0x0F, 0xF8, 0x0E, 0xFA, 0xBB, 0x79, 0x60, 0xF1, 0xBF, 0xEF, 0x2F, 0x55, 0x36, 0xB8, 0x97, 0x73, 0x19, 0x66, 0xF0, 0x9B, 0xC8, 0xF2, 0x35, 0x2E, 0x70, 0xBE, 0xDD, 0xA8, 0x3A, 0x60, 0x16, 0xDD, 0xB4, 0x5C, 0x21, 0xCC, 0xB8, 0x2C, 0xEB, 0xCE, 0xD6, 0x8D, 0x72, 0xAD, 0x6A, 0xBF, 0xFD, 0xF9, 0x04, 0x3F, 0x62, 0x77, 0xC6, 0x74, 0x9B, 0xFB, 0xBC, 0xF1, 0xDB, 0xB0, 0x64, 0xFF, 0x6E, 0xAE, 0x7A, 0x71, 0x75, 0xDD, 0x6B, 0x5C, 0xF0, 0x7E, 0xB6, 0x73, 0x3A, 0x86, 0x6A, 0x76, 0xAC, 0x57, 0x35, 0xED, 0x5A, 0xD9, 0x47, 0x6A, 0xB7, 0x80, 0x16, 0x9A, 0x88, 0xB3, 0xCB, 0x1E, 0x63, 0xB7, 0x7B, 0x6F, 0xFD, 0xF7, 0x17, 0xEE, 0xD6, 0x39, 0x41, 0x25, 0x4D, 0xF4, 0x3B, 0x3A, 0xC3, 0x05, 0xEF, 0x5F, 0x9E, 0xD3, 0x31, 0x58, 0xB7, 0x76, 0x92, 0xD9, 0xE0, 0x2D, 0x32, 0x9F, 0x6D, 0xD9, 0x05, 0x16, 0xD0, 0x66, 0x19, 0xB8, 0x2F, 0xAE, 0x1E, 0xE6, 0xC0, 0x12, 0x2B, 0xBF, 0xBF, 0x44, 0xFF, 0xCA, 0x6F, 0x85, 0xA5, 0x67, 0x3A, 0x06, 0xDB, 0xD7, 0xFD, 0x82, 0xCF, 0xB7, 0x54, 0x61, 0x2A, 0x92, 0xB6, 0x13, 0xEE, 0x72, 0x8E, 0x0B, 0x76, 0x0C, 0x4D, 0x62, 0xBA, 0x6A, 0x20, 0x69, 0x58, 0xC2, 0x79, 0x3B, 0x89, 0x35, 0x61, 0xB9, 0x08, 0xD1, 0x47, 0x75, 0xE5, 0x17, 0xCC, 0xF7, 0x81, 0x55, 0x57, 0x98, 0x89, 0xCA, 0x15, 0x75, 0x85, 0xEF, 0xDB, 0x29, 0xB0, 0xDC, 0x9C, 0x69, 0xF5, 0x0B, 0x3C, 0x7F, 0x46, 0xE4, 0xBD, 0xE9, 0xC3, 0x2F, 0x78, 0x6F, 0xAC, 0xA5, 0x19, 0x03, 0x6B, 0x3B, 0xCF, 0x59, 0x2E, 0x5B, 0x95, 0x34, 0x91, 0x3B, 0xC9, 0x5B, 0x3D, 0x37, 0xED, 0xDA, 0xCB, 0xCD, 0x3F, 0x36, 0xD1, 0x47, 0x47, 0x75, 0xD8, 0x63, 0x47, 0x6F, 0x71, 0x82, 0xFB, 0xB9, 0xA0, 0xE9, 0x2C, 0x97, 0xA3, 0x97, 0xF1, 0xBB, 0x10, 0x7E, 0x31, 0xCC, 0xAF, 0xA8, 0x13, 0x3D, 0xFA, 0xB8, 0xEE, 0xD3, 0x14, 0xEB, 0x3C, 0x53, 0xF7, 0x16, 0x4D, 0xC2, 0x52, 0xEC, 0x7D, 0xBF, 0xA8, 0xF2, 0xEA, 0x0A, 0xCE, 0xCF, 0x73, 0x61, 0x9E, 0x51, 0xBF, 0xBC, 0x7D, 0x17, 0xC2, 0x31, 0xD4, 0x33, 0xF0, 0xCA, 0x8C, 0x90, 0xF4, 0x43, 0x1B, 0xFA, 0x5D, 0xF4, 0x91, 0x8A, 0x66, 0x60, 0x75, 0xF6, 0xB9, 0x17, 0x02, 0x4B, 0xD4, 0xD2, 0xD9, 0x9E, 0x89, 0x79, 0xBD, 0xC2, 0x65, 0x55, 0x29, 0xF6, 0xA3, 0x49, 0x5D, 0xA9, 0xF7, 0x8D, 0xAB, 0xEA, 0x6A, 0x4B, 0xB4, 0xB3, 0xC3, 0x72, 0x8F, 0x89, 0xEE, 0x45, 0x56, 0x19, 0x58, 0xFA, 0x0A, 0x92, 0x7A, 0x66, 0x60, 0x65, 0x24, 0x2C, 0x03, 0xCB, 0xCD, 0xF7, 0x7A, 0xBB, 0x39, 0xCF, 0x3B, 0x52, 0x70, 0x2E, 0x3C, 0xD3, 0x2F, 0xC2, 0xF2, 0xF8, 0x5D, 0x59, 0x21, 0xCC, 0xEB, 0x99, 0xC7, 0x44, 0x44, 0x05, 0xEC, 0xC5, 0x8C, 0x04, 0x96, 0x5F, 0xC8, 0x95, 0xFF, 0x03,
};
// clang-format on

extern volatile uint32_t system_reset;

// axi ram 512k
uint8_t *boardloader_buf = (uint8_t *)0x24000000;

// this is mainly for ignore/supress faults during flash read (for check
// purpose). if bus fault enabled, it will catched by BusFault_Handler, then we
// could ignore it. if bus fault disabled, it will elevate to hard fault, this
// is not what we want
static secbool handle_flash_ecc_error = secfalse;
static inline void set_handle_flash_ecc_error(secbool val) {
  handle_flash_ecc_error = val;
}

// fault handlers
void HardFault_Handler(void) {
  error_shutdown("Internal error", "(HF)", NULL, NULL);
}

void MemManage_Handler_MM(void) {
  error_shutdown("Internal error", "(MM)", NULL, NULL);
}

void MemManage_Handler_SO(void) {
  error_shutdown("Internal error", "(SO)", NULL, NULL);
}

void BusFault_Handler(void) {
  // if want handle flash ecc error
  if (handle_flash_ecc_error == sectrue) {
    // dbgprintf_Wait("Internal flash ECC error detected at 0x%X", SCB->BFAR);

    // check if it's triggered by flash DECC
    if (flash_check_ecc_fault()) {
      // reset flash controller error flags
      flash_clear_ecc_fault(SCB->BFAR);

      // reset bus fault error flags
      SCB->CFSR &= ~(SCB_CFSR_BFARVALID_Msk | SCB_CFSR_PRECISERR_Msk);
      __DSB();
      SCB->SHCSR &= ~(SCB_SHCSR_BUSFAULTACT_Msk);
      __DSB();

      // try to fix ecc error and reboot
      if (flash_fix_ecc_fault_BOOTLOADER(SCB->BFAR)) {
        error_shutdown("Internal flash ECC error", "Cleanup successful",
                       "Bootloader reinstall may required",
                       "If the issue persists, contact support.");
      } else {
        error_shutdown("Internal error", "Cleanup failed",
                       "Reboot to try again",
                       "If the issue persists, contact support.");
      }
    }
  }

  // normal route
  error_shutdown("Internal error", "(BF)", NULL, NULL);
}

void UsageFault_Handler(void) {
  error_shutdown("Internal error", "(UF)", NULL, NULL);
}

const char *const STAY_REASON_str[] = {
    ENUM_NAME_ARRAY_ITEM(STAY_REASON_NONE),
    ENUM_NAME_ARRAY_ITEM(STAY_REASON_REQUIRED_BY_FLAG),
    ENUM_NAME_ARRAY_ITEM(STAY_REASON_MANUAL_OVERRIDE),
    ENUM_NAME_ARRAY_ITEM(STAY_REASON_INVALID_DEPENDENCY),
    ENUM_NAME_ARRAY_ITEM(STAY_REASON_INVALID_NEXT_TARGET),
    ENUM_NAME_ARRAY_ITEM(STAY_REASON_UPDATE_NEXT_TARGET),
    ENUM_NAME_ARRAY_ITEM(STAY_REASON_UNKNOWN),
};
static inline void display_boardloader_title(char *message,
                                             STAY_REASON stay_reason) {
  if ((stay_reason < STAY_REASON_NONE) || (stay_reason > STAY_REASON_UNKNOWN))
    stay_reason = STAY_REASON_UNKNOWN;
  display_backlight(255);
  display_clear();
  display_printf("OneKey Boardloader " VERSION_STR "\n");
  display_printf("---------------------------------------\n");
  display_printf("%s\n", STAY_REASON_str[stay_reason]);
  display_printf("---------------------------------------\n");
  display_print(message, -1);
}

void show_poweron_bar(void) {
  static bool forward = true;
  static uint32_t step = 0, location = 0, indicator = 0;

  if (forward) {
    step += PIXEL_STEP;
    if (step <= 90) {
      indicator += PIXEL_STEP;
    } else if (step <= 160) {
      location += PIXEL_STEP;
    } else if (step < 250) {
      location += PIXEL_STEP;
      indicator -= PIXEL_STEP;
    } else {
      forward = false;
    }
  } else {
    step -= PIXEL_STEP;
    if (step > 160) {
      location -= PIXEL_STEP;
      indicator += PIXEL_STEP;
    } else if (step > 90) {
      location -= PIXEL_STEP;
    } else if (step > 0) {
      indicator -= PIXEL_STEP;
    } else {
      forward = true;
    }
  }

  display_bar_radius(160, 352, 160, 4, COLOR_DARK, COLOR_BLACK, 2);
  display_bar_radius(160 + location, 352, indicator, 4, COLOR_WHITE,
                     COLOR_BLACK, 2);
}

static void bootloader_update_cb(int pos) {
  // pass pos=-1 to reset last_pos is acceptable
  // since only 0-100 will be printed
  static int last_pos = -1;

  if (pos != last_pos) {
    if (pos >= 0 && pos <= 100) {
      display_printf("\rProgress: %u%%", pos);
    }
    last_pos = pos;
  }
}

static secbool try_bootloader_update(bool do_update, bool auto_reboot) {
  memzero(boardloader_buf, BOOTLOADER_IMAGE_MAXSIZE);

  // read file
  char new_bootloader_path_legacy[] = "0:boot/bootloader.bin";
  char new_bootloader_path[] = "0:updates/bootloader.bin";

  char *new_bootloader_path_p = NULL;

  // check file exists
  if (emmc_fs_path_exist(new_bootloader_path)) {
    new_bootloader_path_p = new_bootloader_path;
  } else if (emmc_fs_path_exist(new_bootloader_path_legacy)) {
    new_bootloader_path_p = new_bootloader_path_legacy;
  }
  if (new_bootloader_path_p == NULL) return secfalse;

  // check file size
  EMMC_PATH_INFO file_info;
  if (!emmc_fs_path_info(new_bootloader_path_p, &file_info)) return secfalse;
  if (file_info.size > BOOTLOADER_IMAGE_MAXSIZE) return secfalse;

  // read file to buffer
  uint32_t num_of_read = 0;
  if (!emmc_fs_file_read(new_bootloader_path_p, 0, boardloader_buf,
                         file_info.size, &num_of_read))
    return secfalse;

  // check read size matchs file size
  if (num_of_read != file_info.size) return secfalse;

  // validate new bootloader
  image_header file_hdr;

  if (sectrue != load_image_header(boardloader_buf, BOOTLOADER_IMAGE_MAGIC,
                                   BOOTLOADER_IMAGE_MAXSIZE, FW_KEY_M, FW_KEY_N,
                                   FW_KEYS, &file_hdr))
    return secfalse;

  if (sectrue != check_image_contents_ADV(NULL, &file_hdr,
                                          boardloader_buf + file_hdr.hdrlen, 0,
                                          file_hdr.codelen, true))
    return secfalse;

  // check header stated size matchs file size
  if ((file_hdr.hdrlen + file_hdr.codelen) != file_info.size) return secfalse;

  // if not actually doing the update, return as update file validate result
  if (!do_update) return sectrue;

  // validate current bootloader
  image_header flash_hdr;
  secbool flash_hdr_valid = secfalse;
  // secbool code_valid = secfalse;
  FORCE_IGNORE_RETURN(
      verify_bootloader(&flash_hdr, &flash_hdr_valid, NULL, NULL, 0));

#if PRODUCTION
  // handle downgrade or invalid bootloader
  if (flash_hdr_valid == sectrue) {
    if (memcmp(&file_hdr.version, &flash_hdr.version, 4) < 0) {
      return secfalse;
    }
  }
#endif

  // update process
  display_boardloader_title("Bootloader Update\n",
                            STAY_REASON_UPDATE_NEXT_TARGET);
  display_printf("!!! DO NOT POWER OFF !!!\n");
  display_printf("\r\n");

  char err_msg[64];

  // install bootloader
  if (sectrue != install_bootloader(boardloader_buf, file_info.size, err_msg,
                                    sizeof(err_msg), NULL,
                                    bootloader_update_cb)) {
    display_printf("Install error! Bootloader will be erased!\n");
    display_printf("Detail: %s", err_msg);
    FORCE_IGNORE_RETURN(flash_erase_sectors(BOOTLOADER_SECTORS,
                                            BOOTLOADER_SECTORS_COUNT, NULL));
    return secfalse;
  }
  display_printf("\n");

  // verify new bootloader
  if (sectrue !=
      verify_bootloader(NULL, NULL, NULL, err_msg, sizeof(err_msg))) {
    // if not valid, erase anyways
    display_printf("\n");
    display_printf("Verify error! Bootloader will be erased!\n");
    display_printf("Detail: %s\n", err_msg);
    FORCE_IGNORE_RETURN(flash_erase_sectors(BOOTLOADER_SECTORS,
                                            BOOTLOADER_SECTORS_COUNT, NULL));
    return secfalse;
  }
  display_printf("\n");

  // remove file
  display_printf("\rRemoving Payload: ");
  if (!emmc_fs_file_delete(new_bootloader_path_p))
    display_printf(" fail\n");
  else
    display_printf(" done\n");

  // reboot
  if (auto_reboot) {
    for (int i = 3; i >= 0; i--) {
      display_printf("\rRestarting in %d second(s)", i);
      hal_delay(1000);
    }

    restart();
  }
  return sectrue;
}

typedef enum {
  // C = center
  // T = top
  // L = left
  TOUCH_AREA_OTHER = 0,  //
  TOUCH_AREA_C,          //
  TOUCH_AREA_TL,         //
  TOUCH_AREA_TR,         //
  TOUCH_AREA_BL,         //
  TOUCH_AREA_BR,         //
} TOUCH_AREA;

const char *TOUCH_AREA_str[] = {
    ENUM_NAME_ARRAY_ITEM(TOUCH_AREA_OTHER),  //
    ENUM_NAME_ARRAY_ITEM(TOUCH_AREA_C),      //
    ENUM_NAME_ARRAY_ITEM(TOUCH_AREA_TL),     //
    ENUM_NAME_ARRAY_ITEM(TOUCH_AREA_TR),     //
    ENUM_NAME_ARRAY_ITEM(TOUCH_AREA_BL),     //
    ENUM_NAME_ARRAY_ITEM(TOUCH_AREA_BR),     //
};

static const uint16_t touch_area_block_size = 50;
static TOUCH_AREA touch_pos_to_area(uint16_t x, uint16_t y) {
  if (x < 0 || x > MAX_DISPLAY_RESX) return TOUCH_AREA_OTHER;
  if (x < 0 || x > MAX_DISPLAY_RESY) return TOUCH_AREA_OTHER;

  if (x <= touch_area_block_size && y <= touch_area_block_size)
    return TOUCH_AREA_TL;
  if (x >= MAX_DISPLAY_RESX - touch_area_block_size &&
      y <= touch_area_block_size)
    return TOUCH_AREA_TR;

  if (x <= touch_area_block_size &&
      y >= MAX_DISPLAY_RESY - touch_area_block_size)
    return TOUCH_AREA_BL;
  if (x >= MAX_DISPLAY_RESX - touch_area_block_size &&
      y >= MAX_DISPLAY_RESY - touch_area_block_size)
    return TOUCH_AREA_BR;

  if ((x >= (MAX_DISPLAY_RESX / 2 - (touch_area_block_size / 2)) &&
       x <= (MAX_DISPLAY_RESX / 2 + (touch_area_block_size / 2))) &&
      (y >= (MAX_DISPLAY_RESY / 2 - (touch_area_block_size / 2)) &&
       y <= (MAX_DISPLAY_RESY / 2 + (touch_area_block_size / 2))))
    return TOUCH_AREA_C;

  return TOUCH_AREA_OTHER;
}
#if false
// testing and calibrating purpose functions
static void touch_area_display()
{
  display_clear();
  display_bar(0, 0, touch_area_block_size, touch_area_block_size, COLOR_RED); // TOUCH_AREA_TL
  display_bar(
      MAX_DISPLAY_RESX - touch_area_block_size, 0, touch_area_block_size, touch_area_block_size, COLOR_BLUE
  ); // TOUCH_AREA_TR
  display_bar(
      0, MAX_DISPLAY_RESY - touch_area_block_size, touch_area_block_size, touch_area_block_size, COLOR_GREEN
  ); // TOUCH_AREA_BL
  display_bar(
      MAX_DISPLAY_RESX - touch_area_block_size, MAX_DISPLAY_RESY - touch_area_block_size, touch_area_block_size,
      touch_area_block_size, COLOR_DARK
  ); // TOUCH_AREA_BR
  display_bar(
      (MAX_DISPLAY_RESX / 2 - (touch_area_block_size / 2)), (MAX_DISPLAY_RESY / 2 - (touch_area_block_size / 2)),
      touch_area_block_size, touch_area_block_size, COLOR_WHITE
  ); // TOUCH_AREA_C
}
static void touch_area_test()
{
  // check manual overrides
  uint32_t touch_data = 0;
  uint16_t touch_start_pos[2] = {0, 0}; // {x,y}
  uint16_t touch_move_pos[2] = {0, 0}; // {x,y}
  uint16_t touch_end_pos[2] = {0, 0}; // {x,y}
  TOUCH_AREA ta_start = TOUCH_AREA_OTHER;
  TOUCH_AREA ta_end = TOUCH_AREA_OTHER;
  bool touch_center_cross = false;

  while(true){

    // pull touch screen
    touch_data = touch_read();
    if (touch_data != 0) {
      if(touch_data & TOUCH_START)
      {
        // reset on new touch event
        touch_center_cross = false;
        ta_start = TOUCH_AREA_OTHER;
        ta_end = TOUCH_AREA_OTHER;

        touch_start_pos[0] = (touch_data >> 12) & 0xFFF;
        touch_start_pos[1] = (touch_data >> 0) & 0xFFF;
        
        ta_start = touch_pos_to_area(touch_start_pos[0], touch_start_pos[1]);
      }
      if(touch_data & TOUCH_MOVE)
      {
        touch_move_pos[0] = (touch_data >> 12) & 0xFFF;
        touch_move_pos[1] = (touch_data >> 0) & 0xFFF;

        if(TOUCH_AREA_C == touch_pos_to_area(touch_move_pos[0], touch_move_pos[1]))
          touch_center_cross = true;
      }
      if(touch_data & TOUCH_END)
      {
        touch_end_pos[0] = (touch_data >> 12) & 0xFFF;
        touch_end_pos[1] = (touch_data >> 0) & 0xFFF;

        ta_end = touch_pos_to_area(touch_end_pos[0], touch_end_pos[1]);

        display_print_clear();
        display_printf("start=%s \nend=%s \ncenter_cross=%s \n", TOUCH_AREA_str[ta_start], TOUCH_AREA_str[ta_end], (touch_center_cross?"Y":"N"));
      }
    }

    // check if condition meet
    if(touch_center_cross && ta_start == TOUCH_AREA_TL && ta_end == TOUCH_AREA_BR)
    {
      display_print_clear();
      display_printf("BOOT_TARGET_BOARDLOADER\n");
      while(!touch_click()){}
      break;
    }

    if(touch_center_cross && ta_start == TOUCH_AREA_TR && ta_end == TOUCH_AREA_BL)
    {
      display_print_clear();
      display_printf("BOOT_TARGET_BOOTLOADER\n");
      while(!touch_click()){}
      break;
    }
  }
}
#endif

static BOOT_TARGET decide_boot_target(STAY_REASON *stay_reason,
                                      image_header *const hdr,
                                      secbool *hdr_valid, secbool *code_valid) {
  // get boot target flag
  BOOT_TARGET boot_target = *BOOT_TARGET_FLAG_ADDR;  // cache flag
  *BOOT_TARGET_FLAG_ADDR = BOOT_TARGET_NORMAL;       // consume(reset) flag

  // handle stay reason
  STAY_REASON dummy_stay_reason;
  if (stay_reason == NULL) {
    stay_reason = &dummy_stay_reason;
  }
  *stay_reason = STAY_REASON_NONE;

  // if boot target already set to this level, no more checks
  if (boot_target == BOOT_TARGET_BOARDLOADER) {
    *stay_reason = STAY_REASON_REQUIRED_BY_FLAG;
    return boot_target;
  }

  // check manual overrides
  uint32_t touch_data = 0;
  uint16_t touch_start_pos[2] = {0, 0};  // {x,y}
  uint16_t touch_move_pos[2] = {0, 0};   // {x,y}
  uint16_t touch_end_pos[2] = {0, 0};    // {x,y}
  TOUCH_AREA ta_start = TOUCH_AREA_OTHER;
  TOUCH_AREA ta_end = TOUCH_AREA_OTHER;
  bool touch_center_cross = false;

  for (int timer = 0; timer < 1600; timer++) {
    // display bar
    if (timer % 8 == 0) {
      show_poweron_bar();
    }

    // pull touch screen
    touch_data = touch_read();
    if (touch_data != 0) {
      if (touch_data & TOUCH_START) {
        // reset on new touch event
        touch_center_cross = false;
        ta_start = TOUCH_AREA_OTHER;
        ta_end = TOUCH_AREA_OTHER;

        touch_start_pos[0] = (touch_data >> 12) & 0xFFF;
        touch_start_pos[1] = (touch_data >> 0) & 0xFFF;

        ta_start = touch_pos_to_area(touch_start_pos[0], touch_start_pos[1]);
      }
      if (touch_data & TOUCH_MOVE) {
        touch_move_pos[0] = (touch_data >> 12) & 0xFFF;
        touch_move_pos[1] = (touch_data >> 0) & 0xFFF;

        if (TOUCH_AREA_C ==
            touch_pos_to_area(touch_move_pos[0], touch_move_pos[1]))
          touch_center_cross = true;
      }
      if (touch_data & TOUCH_END) {
        touch_end_pos[0] = (touch_data >> 12) & 0xFFF;
        touch_end_pos[1] = (touch_data >> 0) & 0xFFF;

        ta_end = touch_pos_to_area(touch_end_pos[0], touch_end_pos[1]);
      }
    }

    // check if condition meet
    if (touch_center_cross && ta_start == TOUCH_AREA_TL &&
        ta_end == TOUCH_AREA_BR) {
      boot_target = BOOT_TARGET_BOARDLOADER;
      *stay_reason = STAY_REASON_MANUAL_OVERRIDE;
      break;
    }

    if (touch_center_cross && ta_start == TOUCH_AREA_TR &&
        ta_end == TOUCH_AREA_BL) {
      boot_target = BOOT_TARGET_BOOTLOADER;
      *stay_reason = STAY_REASON_MANUAL_OVERRIDE;
      break;
    }

    // delay
    hal_delay(1);
  }

  // clear poweron bar
  display_bar(160, 352, 160, 4, COLOR_BLACK);

  // if manual override stay at this level no more checks
  if ((*stay_reason == STAY_REASON_MANUAL_OVERRIDE) &&
      (boot_target == BOOT_TARGET_BOARDLOADER)) {
    return boot_target;
  }

  // check bootloader update
  if (sectrue == try_bootloader_update(false, false)) {
    boot_target = BOOT_TARGET_BOARDLOADER;
    *stay_reason = STAY_REASON_UPDATE_NEXT_TARGET;
    return boot_target;
  }

  // check res
  if (!emmc_fs_path_exist("0:res/.ONEKEY_RESOURCE")) {
    boot_target = BOOT_TARGET_BOARDLOADER;
    *stay_reason = STAY_REASON_INVALID_DEPENDENCY;
    return boot_target;
  }

  // check bootloader
  if (sectrue != verify_bootloader(hdr, hdr_valid, code_valid, NULL, 0)) {
    boot_target = BOOT_TARGET_BOARDLOADER;
    *stay_reason = STAY_REASON_INVALID_NEXT_TARGET;
    return boot_target;
  }

  return boot_target;
}

static secbool get_device_serial(char *serial, size_t len) {
  // init
  uint8_t otp_serial[FLASH_OTP_BLOCK_SIZE] = {0};
  memzero(otp_serial, sizeof(otp_serial));
  memzero(serial, len);

  // get OTP serial
  if (sectrue != flash_otp_is_locked(FLASH_OTP_DEVICE_SERIAL)) return secfalse;

  if (sectrue != flash_otp_read(FLASH_OTP_DEVICE_SERIAL, 0, otp_serial,
                                sizeof(otp_serial))) {
    return secfalse;
  }

  // make sure last element is '\0'
  otp_serial[FLASH_OTP_BLOCK_SIZE - 1] = '\0';

  // check if all is ascii
  for (uint32_t i = 0; i < sizeof(otp_serial); i++) {
    if (otp_serial[i] == '\0') {
      break;
    }
    if (otp_serial[i] < ' ' || otp_serial[i] > '~') {
      return secfalse;
    }
  }

  // copy to output buffer
  memcpy(serial, otp_serial, MIN(len, sizeof(otp_serial)));

  // cutoff by strlen
  serial[strlen(serial)] = '\0';

  return sectrue;
}

static void usb_connect_switch(void) {
  static bool usb_opened = false;
  static uint32_t counter0 = 0, counter1 = 0;

  if (usb_3320_host_connected()) {
    counter0++;
    counter1 = 0;
    hal_delay(1);
    if (counter0 > 5) {
      counter0 = 0;
      if (!usb_opened) {
        usb_start();
        usb_opened = true;
      }
    }
  } else {
    counter0 = 0;
    counter1++;
    hal_delay(1);
    if (counter1 > 5) {
      counter1 = 0;
      if (usb_opened) {
        usb_stop();
        usb_opened = false;
      }
    }
  }
}

int main(void) {
  // minimal initialize
  reset_flags_reset();
  periph_init();
  system_clock_config();
  dwt_init();
  cpu_cache_enable();
  sdram_init();

  // enforce protection
  flash_option_bytes_init();

  mpu_config_boardloader(sectrue, sectrue);
  mpu_config_bootloader(sectrue, secfalse);
  mpu_config_base();  // base config last as it contains deny access layers and
                      // mpu may already running
  mpu_ctrl(sectrue);  // ensure enabled

  // user interface
  lcd_init();
  display_clear();
  lcd_pwm_init();
  display_backlight(128);
  touch_init();

  // fault handler
  bus_fault_enable();  // it's here since requires user interface
  set_handle_flash_ecc_error(sectrue);

  // periph initialize
  flash_otp_init();
  rng_init();
  clear_otg_hs_memory();

  // emmc init and volume check
  emmc_fs_init();
  if (!emmc_fs_is_partitioned()) {
    emmc_fs_recreate(true, true, true);
  }
  emmc_fs_mount(true, true);

  // display boot screen
  display_image((DISPLAY_RESX - 128) / 2, 190, 128, 128, toi_icon_onekey + 12,
                sizeof(toi_icon_onekey) - 12);
  display_image((DISPLAY_RESX - 140) / 2, DISPLAY_RESY - 120, 140, 30,
                toi_icon_safeos + 12, sizeof(toi_icon_safeos) - 12);
  display_text_center(DISPLAY_RESX / 2, DISPLAY_RESY - 64, "Powered by OneKey",
                      -1, FONT_NORMAL, COLOR_GRAY, COLOR_BLACK);
#if !PRODUCTION
  display_text_center(DISPLAY_RESX / 2, DISPLAY_RESY / 2, "TEST VERSION", -1,
                      FONT_NORMAL, COLOR_RED, COLOR_BLACK);
#endif

  STAY_REASON stay_reason;
  image_header hdr;
  secbool hdr_valid = secfalse;
  secbool code_valid = secfalse;
  BOOT_TARGET boot_target =
      decide_boot_target(&stay_reason, &hdr, &hdr_valid, &code_valid);

  if (boot_target == BOOT_TARGET_BOARDLOADER) {
    if (stay_reason == STAY_REASON_UPDATE_NEXT_TARGET) {
      try_bootloader_update(true, true);
    } else {
      display_boardloader_title("USB Mass Storage Mode\n", stay_reason);

      char serial[USB_SIZ_STRING_SERIAL];
      get_device_serial(serial, sizeof(serial));
      usb_msc_init(serial, sizeof(serial));

      while (1) {
        usb_connect_switch();
        if (system_reset == 1) {
          hal_delay(5);
          restart();
        }
      }
    }
  }

  *BOOT_TARGET_FLAG_ADDR = boot_target;  // set flag for bootloader to comsume

  set_handle_flash_ecc_error(secfalse);
  bus_fault_disable();

  SCB_CleanDCache();  // TODO: needed?

  mpu_config_bootloader(sectrue, sectrue);

  jump_to(BOOTLOADER_START + hdr.hdrlen);

  return 0;
}
