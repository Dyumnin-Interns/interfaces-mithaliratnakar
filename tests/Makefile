SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(PWD)/../hdl/dut.v \
                  $(PWD)/../hdl/FIFO1.v \
                  $(PWD)/../hdl/FIFO2.v
TOPLEVEL = dut
MODULE = dut_test
EXTRA_ARGS += --vcd=waveform.vcd
include $(shell cocotb-config --makefiles)/Makefile.sim
