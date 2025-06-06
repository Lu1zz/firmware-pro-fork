/* TREZORv2 firmware linker script */

ENTRY(reset_handler)

MEMORY {
  FLASH  (rx)  : ORIGIN = 0x08060000, LENGTH = 1536K
  FLASH2 (r)   : ORIGIN = 0x90000000, LENGTH = 4096K
  AXIRAM (wal) : ORIGIN = 0x24000000, LENGTH = 512K
  SRAM   (wal) : ORIGIN = 0x20000000, LENGTH = 128K
  SRAM1   (wal) : ORIGIN = 0x30000000, LENGTH = 128K
  SRAM2   (wal) : ORIGIN = 0x30020000, LENGTH = 128K
  /* SRAM3 is used for DMA */
  SRAM3   (wal) : ORIGIN = 0x30040000, LENGTH = 32K
  EXRAM   (wal) : ORIGIN = 0xD1B00000, LENGTH = 1024K
  FW_RAM  (wal) : ORIGIN = 0xD1C00000, LENGTH = 4096K
}

main_stack_base = ORIGIN(SRAM) + LENGTH(SRAM); /* 8-byte aligned full descending stack */
_sstack = main_stack_base - SIZEOF(.stack);
_estack = main_stack_base;

/* used by the startup code to populate variables used by the C code */
data_lma = LOADADDR(.data);
data_vma = ADDR(.data);
data_size = SIZEOF(.data);

/* used by the startup code to wipe memory */
axiram_start = ORIGIN(AXIRAM);
axiram_end = ORIGIN(AXIRAM) + LENGTH(AXIRAM);

/* used by the startup code to wipe memory */
sram_start = ORIGIN(SRAM);
sram_end = ORIGIN(SRAM) + LENGTH(SRAM);
_ram_start = sram_start;
_ram_end = sram_end;

_codelen = LENGTH(FLASH) - SIZEOF(.vendorheader) - SIZEOF(.header) + SIZEOF(.flash2);
_flash_start = ORIGIN(FLASH);
_flash_end = ORIGIN(FLASH) + LENGTH(FLASH);
_heap_start = ADDR(.heap);
_heap_end = ADDR(.heap) + SIZEOF(.heap);

_flash2_load_addr = LOADADDR(.flash2);
_flash2_start = ORIGIN(FW_RAM);
_flash2_end = _flash2_start + SIZEOF(.flash2);

SECTIONS {
  .vendorheader : ALIGN(4) {
    KEEP(*(.vendorheader))
  } >FLASH AT>FLASH

  .header : ALIGN(4) {
    KEEP(*(.header));
  } >FLASH AT>FLASH

  .flash2 : ALIGN(512) {
    build/firmware/frozen_mpy.o(.rodata*);
    build/firmware/vendor/secp256k1-zkp/src/secp256k1.o(.rodata*);
    . = ALIGN(512);
  } >FW_RAM AT>FLASH2

  .qrcode_buf (NOLOAD): ALIGN(4) {
    KEEP(*(.qrcode_buf));
    . = 25K;
  } >EXRAM

  .flash : ALIGN(512) {
    _stext = .;
    KEEP(*(.vector_table_ex));
    . = ALIGN(1024);
    _vector_offset = .;
    KEEP(*(.vector_table));
    . = ALIGN(4);
    *(.text*);
    . = ALIGN(4);
    *(.rodata*);
    . = ALIGN(4);
    /* KEEP(*(.bootloader)); */
    /* *(.bootloader*); */
    /*. = ALIGN(512); */
    _etext = .;
  } >FLASH AT>FLASH

  .data : ALIGN(4) {
    *(.data*);
    . = ALIGN(512);
  } >SRAM AT>FLASH

  .sram1 : {
		*(sram1)
	} >SRAM1

  .sram3 : ALIGN(4) {
    *(.sram3*);
    . = ALIGN(4);
  } >SRAM3

  .exram : ALIGN(4) {
    *(.exram);
    . = ALIGN(4);
  } >EXRAM

  .bss2 : ALIGN(4) {
    *(.bss.global_image);
    *(.bss.global_feature);
    *(.bss.global_templet);
    *(.bss.totaledata1);
    *(.bss.totaledata2);
    *(.bss.g_FeatureCmp);
    . = ALIGN(4);
  } >SRAM2

  .bss : ALIGN(4) {
    *(.bss*);
    . = ALIGN(4);
  } >SRAM

  .stack : ALIGN(8) {
    . = 16K; /* this acts as a build time assertion that at least this much memory is available for stack use */
  } >SRAM

  .heap : ALIGN(4) {
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = 512K; /* this acts as a build time assertion that at least this much memory is available for heap use */
    /*. = ABSOLUTE(sram_end - 16K);  this explicitly sets the end of the heap effectively giving the stack at most 16K */
  } >AXIRAM
}
