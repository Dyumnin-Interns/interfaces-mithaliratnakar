import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.result import TestFailure

@cocotb.test()
async def test_fifo_deep_debug(dut):
    """Test writing to a_ff and b_ff, then reading from y_ff."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset_n.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    await Timer(100, units="ns")
    dut.resert_n.value = 1
    await RisingEdge(dut.clk)

    # Write 1-bit values to a_ff (addr=4) and b_ff (addr=5)
    dut.write_en.value = 1
    dut.write_address.value = 4
    dut.write_data.value = 1
    await RisingEdge(dut.clk)

    dut.write_address.value = 5
    dut.write_data.value = 1
    await RisingEdge(dut.clk)

    dut.write_en.value = 0
    await RisingEdge(dut.clk)

    # Wait for counter to hit 50
    for _ in range(55):
        await RisingEdge(dut.clk)

    # Read from y_ff.D_OUT (addr = 3)
    dut.read_address.value = 3
    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    actual_val = dut.read_data.value.integer
    dut.read_en.value = 0

    expected_val = 1 | 1  # a_ff || b_ff → 1
    assert actual_val == expected_val, f"Mismatch: expected {expected_val}, got {actual_val}"

    dut._log.info(f"Test passed. y_ff output = {actual_val}")
