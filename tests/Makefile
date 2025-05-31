SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Verilog source files
VERILOG_SOURCES = $(PWD)/../hdl/dut_wrapper.v \
                  $(PWD)/../hdl/dut.v \
                  $(PWD)/../hdl/FIFO1.v \
                  $(PWD)/../hdl/FIFO2.v

# Top-level module (now using the wrapper)
TOPLEVEL = dut_wrapper

# Python test module
MODULE = dut_test

# Simulation options
EXTRA_ARGS += --vcd=waveform.vcd  
EXTRA_ARGS += -Wall               
