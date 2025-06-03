TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    ../hdl/FIFO1.v \
    ../hdl/FIFO2.v \
    ../hdl/dut.v \
    ../hdl/dut_wrapper.v
TOPLEVEL = dut_wrapper
MODULE = dut_test
SIM = icarus
WAVES = waveform.vcd
include $(shell cocotb-config --makefiles)/Makefile.sim

