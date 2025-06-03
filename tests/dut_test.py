import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock

async def reset_dut(dut):
    dut.RST.value = 1
    await Timer(10, units='ns')
    dut.RST.value = 0
    await Timer(10, units='ns')

@cocotb.test()
async def dut_test(dut):
    """Basic FIFO write-read test"""
    # Start clock
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())

    # Reset DUT
    await reset_dut(dut)

    # Write some data
    dut.WR_EN.value = 1
    dut.DATA_IN.value = 0xA5
    await RisingEdge(dut.CLK)
    dut.WR_EN.value = 0

    # Read back the data
    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    dut.RD_EN.value = 0

    # Wait for output to stabilize
    await Timer(1, units="ns")
    assert dut.DATA_OUT.value == 0xA5, f"Expected 0xA5, got {dut.DATA_OUT.value}"
