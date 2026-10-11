.DEFAULT_GOAL := sim
SIM ?= icarus
TOPLEVEL_LANG := verilog
VERILOG_SOURCES := $(abspath ../src/event_pkg.sv) $(abspath ../src/capture_engine.sv)
COCOTB_TOPLEVEL := capture_engine
COCOTB_TEST_MODULES := test_capture_engine
export PYTHONPATH := $(CURDIR)/unit:$(CURDIR):$(PYTHONPATH)
COMPILE_ARGS += -g2012
COCOTB_CONFIG ?= ../.venv/bin/cocotb-config
override PYTHON_BIN := $(abspath ../.venv/bin/python)
export PATH := $(abspath ../.venv/bin):$(PATH)

.PHONY: help
help:
	@echo "make -C verification: run capture-engine cocotb tests"
	@echo "make -C verification WAVES=1: also record waveforms"

ifneq ($(MAKECMDGOALS),help)
include $(shell $(COCOTB_CONFIG) --makefiles)/Makefile.sim
endif
