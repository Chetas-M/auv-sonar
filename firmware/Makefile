# ==============================================================================
# Makefile for STM32G474 AUV Adaptive Sonar Transmitter Payload (SIH PS 26058)
# Supports both ARM GCC cross-compilation and Host GCC syntax/link verification.
# ==============================================================================

PROJECT = auv_sonar_transmitter

# Directories
INC_DIRS = Inc inc ../outputs/headers
SRC_DIRS = Src src
BUILD_DIR = build

# Source files (supports both Src and src casing)
SRCS = $(wildcard $(addsuffix /*.c, $(SRC_DIRS)))
OBJS = $(patsubst %.c, $(BUILD_DIR)/%.o, $(notdir $(SRCS)))

# Include flags
INCLUDES = $(addprefix -I, $(INC_DIRS))

# ------------------------------------------------------------------------------
# Target Toolchain (ARM Cortex-M4F for STM32G474)
# ------------------------------------------------------------------------------
CROSS_COMPILE ?= arm-none-eabi-
CC_ARM = $(CROSS_COMPILE)gcc
OBJCOPY = $(CROSS_COMPILE)objcopy
SIZE    = $(CROSS_COMPILE)size

ARM_FLAGS = -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard \
            -DSTM32G474xx -O2 -Wall -Wextra -std=c11 $(INCLUDES)

# ------------------------------------------------------------------------------
# Host Toolchain (x86_64 GCC for verification without hardware)
# ------------------------------------------------------------------------------
CC_HOST = gcc
HOST_FLAGS = -O2 -Wall -Wextra -std=c11 $(INCLUDES)

.PHONY: all host target clean

all: host

# Host verification build
host: $(BUILD_DIR)/$(PROJECT)_host.exe
	@echo "Host build successful: $(BUILD_DIR)/$(PROJECT)_host.exe"

$(BUILD_DIR)/$(PROJECT)_host.exe: $(SRCS) | $(BUILD_DIR)
	$(CC_HOST) $(HOST_FLAGS) $^ -o $@

# ARM Target cross-compilation (when arm-none-eabi-gcc is available)
target: $(BUILD_DIR)/$(PROJECT).elf $(BUILD_DIR)/$(PROJECT).bin $(BUILD_DIR)/$(PROJECT).hex

$(BUILD_DIR)/$(PROJECT).elf: $(OBJS) | $(BUILD_DIR)
	$(CC_ARM) $(ARM_FLAGS) $^ -o $@
	$(SIZE) $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf
	$(OBJCOPY) -O binary $< $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf
	$(OBJCOPY) -O ihex $< $@

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC_ARM) $(ARM_FLAGS) -c $< -o $@

ifeq ($(OS),Windows_NT)
    CLEAN_CMD = if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)
    MKDIR_CMD = if not exist $(BUILD_DIR) mkdir $(BUILD_DIR)
else
    CLEAN_CMD = rm -rf $(BUILD_DIR)
    MKDIR_CMD = mkdir -p $(BUILD_DIR)
endif

$(BUILD_DIR):
	@$(MKDIR_CMD)

clean:
	@$(CLEAN_CMD)
