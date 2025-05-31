import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_fifo_write_read(dut):
    """ Test basic write to FIFO and read from output """

    dut.RST_N.value = 0
    dut.CLK.value = 0
    dut.write_en.value = 0
    dut.write_address.value = 0
    dut.write_data.value = 0
    dut.read_en.value = 0
    dut.read_address.value = 0

 
    clock = Clock(dut.CLK, 10, units="ns")  
    cocotb.start_soon(clock.start())


    await Timer(20, units='ns')
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

    dut.write_address.value = 4
    dut.write_data.value = 1
    dut.write_en.value = 1
    await RisingEdge(dut.CLK)
    dut.write_en.value = 0

    await RisingEdge(dut.CLK)
    dut.write_address.value = 5
    dut.write_data.value = 0
    dut.write_en.value = 1
    await RisingEdge(dut.CLK)
    dut.write_en.value = 0

    for _ in range(50):
        await RisingEdge(dut.CLK)

    dut.read_address.value = 3
    dut.read_en.value = 1
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await RisingEdge(dut.CLK)

    # Read data
    read_data = dut.read_data.value.integer
    cocotb.log.info(f"Read data from y FIFO first element: {read_data}")

    assert read_data == 1, f"Expected 1, got {read_data}"
