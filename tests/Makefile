TOPLEVEL_LANG = verilog 
VERILOG_SOURCES = $(shell pwd)/FIFO1.v \
                  $(shell pwd)/FIFO2.v \
                  $(shell pwd)/dut.v \
                  $(shell pwd)/dut_wrapper.v

TOPLEVEL = dut_wrapper
MODULE = testcases

SIM = icarus
COMPILE_ARGS += -g2012

include $(shell cocotb-config --makefiles)/Makefile.sim
