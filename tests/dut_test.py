import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge
from cocotb.utils import get_sim_time
from cocotb.binary import BinaryValue

@cocotb.test()
async def test_fifo_deep_debug(dut):
    """Enhanced FIFO test with comprehensive debugging"""
    
    # Configuration
    CLK_PERIOD_NS = 10  # 100MHz
    RESET_CYCLES = 3     # Extended reset duration
    DEBUG = True
    
    # Signal monitoring function
    def log_signals():
        if DEBUG:
            cocotb.log.info(f"Time {get_sim_time()} ps - Signals:")
            for sig in ['clk', 'reset_n', 'write_en', 'write_rdy', 
                       'read_en', 'read_rdy', 'write_data', 'read_data']:
                if hasattr(dut, sig):
                    val = getattr(dut, sig).value
                    cocotb.log.info(f"{sig:15} = {val}")

    # Clock generation
    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))
    
    # Initialize all signals
    dut.reset_n.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    dut.write_address.value = 0
    dut.write_data.value = 0
    dut.read_address.value = 0
    
    # Extended reset sequence
    cocotb.log.info("Applying extended reset...")
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.reset_n.value = 1
    await RisingEdge(dut.clk)
    log_signals()
    
    # Post-reset verification
    assert dut.reset_n.value == 1, "Reset not deasserted"
    if hasattr(dut, 'write_rdy'):
        assert dut.write_rdy.value == 1, "Write not ready post-reset"
    if hasattr(dut, 'read_rdy'):
        assert dut.read_rdy.value == 1, "Read not ready post-reset"
    
    # Test sequence with comprehensive logging
    test_cases = [
        (0, 0x55),  # Basic pattern
        (1, 0xAA),  # Alternating bits
        (2, 0x01),  # Single bit
        (3, 0x80)   # High bit
    ]
    
    for addr, data in test_cases:
        # Write operation
        cocotb.log.info(f"\n=== Writing 0x{data:02X} to addr {addr} ===")
        dut.write_address.value = addr
        dut.write_data.value = data
        dut.write_en.value = 1
        await RisingEdge(dut.clk)
        log_signals()
        dut.write_en.value = 0
        
        # Wait 2 cycles for write completion
        for i in range(2):
            await RisingEdge(dut.clk)
            cocotb.log.info(f"Write wait cycle {i+1}")
            log_signals()
        
        # Read operation
        cocotb.log.info(f"\n=== Reading from addr {addr} ===")
        dut.read_address.value = addr
        dut.read_en.value = 1
        await RisingEdge(dut.clk)
        log_signals()
        dut.read_en.value = 0
        
        # Wait for data
        await RisingEdge(dut.clk)
        log_signals()
        
        # Robust value checking
        read_val = dut.read_data.value
        if not read_val.is_resolvable:
            assert False, f"Read data is unresolved: {read_val}"
        
        read_int = read_val.integer
        assert read_int == data, (
            f"Data mismatch at addr {addr}: "
            f"Expected 0x{data:02X}, got 0x{read_int:02X}\n"
            f"Full binary: {BinaryValue(read_val.binstr)}"
        )
        
        cocotb.log.info(f"Successfully verified addr {addr}")
    
    cocotb.log.info("All tests completed successfully!")
