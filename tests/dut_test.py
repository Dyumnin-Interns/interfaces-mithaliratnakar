import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

async def reset_dut(dut):
    dut.RST_N.value = 0  # Active-low reset
    await Timer(10, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

@cocotb.test()
async def test_fifo_operations(dut):
    # Generate clock (10ns period)
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the DUT
    await reset_dut(dut)

    # Test writing to FIFOs
    dut.write_en.value = 1
    dut.write_address.value = 4  # Address for a_ff
    dut.write_data.value = 1     # Write '1' to a_ff
    await RisingEdge(dut.CLK)

    dut.write_address.value = 5  # Address for b_ff
    dut.write_data.value = 1     # Write '1' to b_ff
    await RisingEdge(dut.CLK)

    # Check if FIFOs are not full
    dut.write_en.value = 0
    dut.read_en.value = 1
    dut.read_address.value = 0   # Check a_ff.notFull()
    await RisingEdge(dut.CLK)
    assert dut.read_data.value == 1, "a_ff should not be full"

    dut.read_address.value = 1   # Check b_ff.notFull()
    await RisingEdge(dut.CLK)
    assert dut.read_data.value == 1, "b_ff should not be full"

    # Wait for OR operation to complete
    await Timer(100, units="ns")

    # Check if y_ff has data (OR result)
    dut.read_address.value = 2   # Check y_ff.notEmpty()
    await RisingEdge(dut.CLK)
    assert dut.read_data.value == 1, "y_ff should have data"

    # Read the OR result (y_ff.first)
    dut.read_address.value = 3
    await RisingEdge(dut.CLK)
    assert dut.read_data.value == 1, "OR result should be 1"

    # Test passed
    dut._log.info("Test passed!")
