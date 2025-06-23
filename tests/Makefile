TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(shell pwd)/../FIFO1.v \
                  $(shell pwd)/../FIFO2.v \
                  $(shell pwd)/../dut.v \
                  $(shell pwd)/../dut_wrapper.v
TOPLEVEL = dut_wrapper
MODULE = dut_test
SIM = icarus
include $(shell cocotb-config --makefiles)/Makefile.sim
