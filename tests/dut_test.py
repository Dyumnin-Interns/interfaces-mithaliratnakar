import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge
from cocotb.utils import get_sim_time
from cocotb.binary import BinaryValue

@cocotb.test()
async def test_fifo_debug(dut):
    """Enhanced FIFO test with waveform-friendly timing and detailed checks"""
    
    # Configuration
    CLK_PERIOD_NS = 10
    RESET_CYCLES = 3
    DEBUG = True
    
    # Clock generation with phase offset for clearer waveforms
    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False, phase=5))  # 5ns phase for edge visibility
    
    # Initialize
    dut.reset_n.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    dut.write_data.value = 0
    dut.write_address.value = 0
    dut.read_address.value = 0
    
    # Reset sequence with waveform markers
    await Timer(1, 'ns')  # Initial delay for waveform clarity
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.reset_n.value = 1
    await Timer(2, 'ns')  # Padding for waveform viewer
    
    # Post-reset checks
    assert dut.reset_n.value == 1, "Reset not deasserted"
    await RisingEdge(dut.clk)
    
    # Test data with distinctive patterns
    test_vectors = [
        (0, 0x55),  # 01010101 - alternating bits
        (1, 0xAA),  # 10101010 - inverse pattern
        (2, 0x01),  # 00000001 - single bit set
        (3, 0x80)   # 10000000 - high bit set
    ]
    
    for addr, data in test_vectors:
        # --- Write Operation ---
        # Wait for write ready with timeout
        timeout = 20
        while dut.write_rdy.value != 1 and timeout > 0:
            await RisingEdge(dut.clk)
            timeout -= 1
        assert timeout > 0, f"Timeout waiting for write_rdy @ addr {addr}"
        
        # Setup write with clean timing
        await FallingEdge(dut.clk)  # Setup during clock low
        dut.write_address.value = addr
        dut.write_data.value = data
        await Timer(1, 'ns')  # Hold before edge
        dut.write_en.value = 1
        
        # Execute write
        await RisingEdge(dut.clk)
        await Timer(1, 'ns')  # Hold after edge
        dut.write_en.value = 0
        
        # --- Read Operation ---
        # Wait for read ready
        timeout = 20
        while dut.read_rdy.value != 1 and timeout > 0:
            await RisingEdge(dut.clk)
            timeout -= 1
        assert timeout > 0, f"Timeout waiting for read_rdy @ addr {addr}"
        
        # Setup read
        await FallingEdge(dut.clk)
        dut.read_address.value = addr
        await Timer(1, 'ns')
        dut.read_en.value = 1
        
        # Execute read
        await RisingEdge(dut.clk)
        await Timer(1, 'ns')
        dut.read_en.value = 0
        
        # Validate read data
        await RisingEdge(dut.clk)  # Allow 1 cycle for data
        await Timer(2, 'ns')  # Sampling delay
        
        # Enhanced error reporting
        observed = dut.read_data.value
        if not observed.is_resolvable:
            assert False, (f"Unresolved read data @ {get_sim_time()} ps: "
                          f"{observed.binstr} (address {addr})")
        
        assert observed.integer == data, (
            f"Data mismatch @ {get_sim_time()} ps (address {addr}):\n"
            f"Expected: {bin(data)} (0x{data:02X})\n"
            f"Observed: {observed.binstr} (0x{observed.integer:02X})\n"
            f"Write timing: {dut.write_en.value} (en) | {dut.write_rdy.value} (rdy)\n"
            f"Read timing:  {dut.read_en.value} (en) | {dut.read_rdy.value} (rdy)"
        )
    
    # Final check for FIFO empty state
    await RisingEdge(dut.clk)
    assert dut.read_rdy.value == 1, "FIFO not empty after all reads"
