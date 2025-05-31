import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_fifo_operations(dut):
    """Test FIFO with explicit timing checks"""
    
    # 1. Clock Setup (100MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # 2. Reset Sequence
    dut.reset_n.value = 0
    await Timer(20, units="ns")  # Hold reset for 2 cycles
    dut.reset_n.value = 1
    await RisingEdge(dut.clk)
    
    # 3. Post-Reset Checks
    assert dut.write_rdy.value == 1, "Write not ready after reset"
    assert dut.read_rdy.value == 1, "Read not ready after reset"
    
    # 4. Basic Write Operation
    test_addr = 0
    test_data = 0xAA
    
    dut.write_address.value = test_addr
    dut.write_data.value = test_data
    dut.write_en.value = 1
    await RisingEdge(dut.clk)
    dut.write_en.value = 0
    
    # 5. Wait for write completion (2 cycles)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # 6. Read Operation
    dut.read_address.value = test_addr
    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    dut.read_en.value = 0
    await RisingEdge(dut.clk)  # Data should be ready
    
    # 7. Verification - Fixed assertions
    read_val = dut.read_data.value
    if read_val.is_resolvable:
        read_val = read_val.integer
        assert read_val == test_data, (
            f"Data mismatch! Wrote 0x{test_data:02X}, got 0x{read_val:02X}"
        )
    else:
        assert False, f"Read data is unresolved: {read_val}"
    
    cocotb.log.info("Basic FIFO test passed")
