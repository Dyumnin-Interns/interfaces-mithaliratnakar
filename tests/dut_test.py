import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.result import TestFailure

@cocotb.test()
async def test_fifo_deep_debug(dut):
    """Test writing to a_ff and b_ff, then reading from y_ff."""

    # Create a clock and start it
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Apply reset
    dut.reset_n.value = 0  # Assert active-low reset
    dut.write_en.value = 0
    dut.read_en.value = 0
    await Timer(100, units="ns") # Hold reset for 100ns
    dut.reset_n.value = 1  # Deassert reset
    await RisingEdge(dut.clk) # Wait for a clock edge after reset

    # Write 1-bit values to a_ff (address 0) and b_ff (address 5)
    # Based on dut.v:
    # a_data$whas = write_en && write_address == 3'd0
    # b_data$whas = write_en && write_address == 3'd5
    
    dut.write_en.value = 1

    # Write to a_ff (use address 0 as per dut.v)
    dut.write_address.value = 0 # CORRECTED: Changed from 4 to 0
    dut.write_data.value = 1
    dut._log.info(f"Writing {dut.write_data.value.integer} to a_ff (addr {dut.write_address.value.integer})")
    await RisingEdge(dut.clk)

    # Write to b_ff (address 5)
    dut.write_address.value = 5
    dut.write_data.value = 1
    dut._log.info(f"Writing {dut.write_data.value.integer} to b_ff (addr {dut.write_address.value.integer})")
    await RisingEdge(dut.clk)

    dut.write_en.value = 0 # Deassert write enable
    await RisingEdge(dut.clk) # Wait one more clock cycle

    dut._log.info("Waiting for counter to reach 50 and y_ff to enqueue...")
    for i in range(55): # Wait for 55 clock cycles (50 for counter + a few extra)
        await RisingEdge(dut.clk)
        # Optional: Log counter value for debugging
        # dut._log.info(f"Cycle {i+1}: Counter = {dut.counter.value.integer}")


    # Read from y_ff (address 3)
    # In dut.v: read_data = y_ff_dout when read_address is 3'd3
    dut.read_address.value = 3
    dut.read_en.value = 1
    await RisingEdge(dut.clk) # Wait for the read to propagate
    actual_val = dut.read_data.value.integer
    dut.read_en.value = 0 # Deassert read enable

    # Expected value: 1 (from a_ff) bitwise OR 1 (from b_ff) = 1
    expected_val = 1 | 1
    
    assert actual_val == expected_val, f"Mismatch: expected {expected_val}, got {actual_val}"

    dut._log.info(f"Test passed. y_ff output = {actual_val}")
