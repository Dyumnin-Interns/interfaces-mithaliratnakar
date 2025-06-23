TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(shell pwd)/../hdl/FIFO1.v \
                  $(shell pwd)/../hdl/FIFO2.v \
                  $(shell pwd)/../hdl/dut.v \
                  $(shell pwd)/../hdl/dut_wrapper.v

TOPLEVEL = dut_wrapper
MODULE = dut_test  # If your top test is in `dut_test.py`. Change if needed.

SIM = icarus
COMPILE_ARGS += -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim
