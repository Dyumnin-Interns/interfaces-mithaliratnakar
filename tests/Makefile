SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(PWD)/../hdl/dut_wrapper.v \
                  $(PWD)/../hdl/dut.v \
                  $(PWD)/../hdl/FIFO1.v \
                  $(PWD)/../hdl/FIFO2.v \
                  $(PWD)/../hdl/delayed_dut.v
TOPLEVEL = dut_wrapper  # Must match wrapper module name
MODULE = dut_test
EXTRA_ARGS += --vcd=$(PWD)/tests/waveform.vcd
include $(shell cocotb-config --makefiles)/Makefile.sim
