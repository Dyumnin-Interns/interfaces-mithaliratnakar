SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/dut.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO1.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v
VERILOG_SOURCES += $(PWD)/../hdl/dut_wrapper.v
TOPLEVEL = dut_wrapper
MODULE = dut_test

ifeq ($(SIM),icarus)
    COMPILE_ARGS += -D COCOTB_SIM=1 -g2012
    PLUSARGS += -fst
    EXTRA_ARGS += --vcd=waves.vcd --wave=waves.fst
    EXTRA_ARGS += -D COCOTB_SIM
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
