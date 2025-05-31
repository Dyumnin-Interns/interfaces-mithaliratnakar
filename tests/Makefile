SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(PWD)/../hdl/dut_wrapper.v \
                  $(PWD)/../hdl/dut.v \
                  $(PWD)/../hdl/FIFO1.v \
                  $(PWD)/../hdl/FIFO2.v
TOPLEVEL = dut_wrapper
MODULE = dut_test

# Ensure VCD is generated in the correct directory
EXTRA_ARGS += --vcd=waveform.vcd 
COCOTB_RESULTS_FILE = results.xml  

include $(shell cocotb-config --makefiles)/Makefile.sim
