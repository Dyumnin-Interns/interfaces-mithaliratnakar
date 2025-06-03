import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_fifo_deep_debug(dut):
    """Test writing to a_ff and b_ff, then reading from y_ff."""

    # Start the clock
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the DUT
    dut.RST_N.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    await Timer(100, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

    # Write to a_ff (write_address = 0)
    dut.write_en.value = 1
    dut.write_address.value = 0
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)
    dut._log.info(f"Writing {dut.write_data.value.integer} to a_ff (addr {dut.write_address.value.integer})")

    # Write to b_ff (write_address = 5)
    dut.write_address.value = 5
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)
    dut._log.info(f"Writing {dut.write_data.value.integer} to b_ff (addr {dut.write_address.value.integer})")

    # Stop writing
    dut.write_en.value = 0
    await RisingEdge(dut.CLK)

    # Wait for y_ff to enqueue output
    dut._log.info("Waiting for counter to reach 50 and y_ff to enqueue...")
    for i in range(55):
        await RisingEdge(dut.CLK)
        dut._log.info(
            f"Cycle {i+1} (Counter: {dut.counter_out.value.integer}): "
            f"a_ff_empty_n={dut.a_ff_EMPTY_N.value.integer}, "
            f"b_ff_empty_n={dut.b_ff_EMPTY_N.value.integer}, "
            f"y_ff_enq={dut.y_ff_enq.value.integer}, "
            f"y_ff_din={dut.y_ff_din.value.integer}"
        )


    dut.read_address.value = 3
    dut.read_en.value = 1
    await RisingEdge(dut.CLK)
    actual_val = dut.read_data.value.integer
    dut.read_en.value = 0

    expected_val = 1 | 1
    assert actual_val == expected_val, f"Mismatch: expected {expected_val}, got {actual_val}"
    dut._log.info(f"Test passed. y_ff output = {actual_val}")
