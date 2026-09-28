/* STM32G474RETx - minimal bare-metal linker script */

ENTRY(Reset_Handler)

_estack = ORIGIN(RAM) + LENGTH(RAM);

_Min_Heap_Size = 0x0000;
_Min_Stack_Size = 0x1000;

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
    RAM   (xrw)  : ORIGIN = 0x20000000, LENGTH = 96K
}

SECTIONS
{
    /* Interrupt vector table + program code */
    .isr_vector :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))
        . = ALIGN(4);
    } > FLASH

    .text :
    {
        . = ALIGN(4);

        *(.text)
        *(.text*)

        *(.glue_7)
        *(.glue_7t)

        KEEP(*(.init))
        KEEP(*(.fini))

        . = ALIGN(4);
        _etext = .;
    } > FLASH

    /* Read-only constants */
    .rodata :
    {
        . = ALIGN(4);
        *(.rodata)
        *(.rodata*)
        . = ALIGN(4);
    } > FLASH

    /* ARM exception tables, if generated */
    .ARM.extab :
    {
        . = ALIGN(4);
        *(.ARM.extab*)
        . = ALIGN(4);
    } > FLASH

    .ARM :
    {
        . = ALIGN(4);
        __exidx_start = .;
        *(.ARM.exidx*)
        __exidx_end = .;
        . = ALIGN(4);
    } > FLASH

    /* Initialized data:
       stored in FLASH, copied to RAM at startup */
    .data :
    {
        . = ALIGN(4);
        _sdata = .;

        *(.data)
        *(.data*)

        . = ALIGN(4);
        _edata = .;
    } > RAM AT> FLASH

    _sidata = LOADADDR(.data);

    /* Zero-initialized data */
    .bss :
    {
        . = ALIGN(4);
        _sbss = .;

        *(.bss)
        *(.bss*)
        *(COMMON)

        . = ALIGN(4);
        _ebss = .;
    } > RAM

    /* Reserve stack */
    ._user_heap_stack :
    {
        . = ALIGN(8);

        . = . + _Min_Heap_Size;
        . = . + _Min_Stack_Size;

        . = ALIGN(8);
    } > RAM

    /* Remove unnecessary sections */
    /DISCARD/ :
    {
        *(.note.GNU-stack)
        *(.comment)
    }
}