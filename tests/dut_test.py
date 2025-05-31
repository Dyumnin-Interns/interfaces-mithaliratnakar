import cocotb
from cocotb.triggers import RisingEdge

@cocotb.test()
async def basic_test(dut):
    """Simple test for reset and I/O."""

    dut.rst_n.value = 0
    for _ in range(2):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    dut.write_en.value = 1
    dut.data_in.value = 0xA5
    await RisingEdge(dut.clk)
    dut.write_en.value = 0

    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    dut.read_en.value = 0

    await RisingEdge(dut.clk)
    cocotb.log.info(f"Read value: {dut.data_out.value}")
