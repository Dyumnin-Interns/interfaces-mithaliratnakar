TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    ../hdl/dut_wrapper.v \
    ../hdl/dut.v \
    ../hdl/FIFO1.v \
    ../hdl/FIFO2.v 
TOPLEVEL = dut_wrapper
MODULE = dut_test
SIM = icarus
WAVES = waveform.vcd
include $(shell cocotb-config --makefiles)/Makefile.sim

