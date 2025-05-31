import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge
from cocotb.utils import get_sim_time
import random

@cocotb.test()
async def test_fifo_comprehensive(dut):
    """Comprehensive FIFO test with error detection and waveform debugging"""

    DEBUG = True  # Set to False to reduce log output
    CLK_PERIOD_NS = 10  # 100MHz clock
    RESET_DURATION_NS = 20
    TEST_ITERATIONS = 10
    

    def log_signal(name):
        if DEBUG and hasattr(dut, name):
            val = getattr(dut, name).value
            cocotb.log.debug(f"{name:15} = {val}")
    
    async def reset():
        """Apply and release reset"""
        cocotb.log.info("Applying reset...")
        dut.RST_N.value = 0
        dut.write_en.value = 0
        dut.read_en.value = 0
        await Timer(RESET_DURATION_NS, units="ns")
        dut.RST_N.value = 1
        await RisingEdge(dut.CLK)
        cocotb.log.info("Reset complete")
        
        # Post-reset checks
        assert dut.write_en.value == 0, "Write enable not reset"
        assert dut.read_en.value == 0, "Read enable not reset"
        if hasattr(dut, 'full'):
            assert dut.full.value == 0, "FIFO should not be full after reset"
        if hasattr(dut, 'empty'):
            assert dut.empty.value == 1, "FIFO should be empty after reset"
    
    async def write_fifo(addr, data):
        """Write to FIFO with logging"""
        cocotb.log.info(f"WRITE addr={addr:2d}, data=0x{data:02X}")
        dut.write_address.value = addr
        dut.write_data.value = data
        dut.write_en.value = 1
        log_signal('write_en')
        log_signal('write_address')
        log_signal('write_data')
        
        await RisingEdge(dut.CLK)
        dut.write_en.value = 0
        await RisingEdge(dut.CLK)  # Wait one cycle
        
        if hasattr(dut, 'full'):
            assert not dut.full.value, "FIFO became full unexpectedly"
    
    async def read_fifo(addr, expected=None):
        """Read from FIFO with optional verification"""
        cocotb.log.info(f"READ  addr={addr:2d}", extra={'expected': f"0x{expected:02X}" if expected is not None else None})
        dut.read_address.value = addr
        dut.read_en.value = 1
        log_signal('read_en')
        log_signal('read_address')
        
        await RisingEdge(dut.CLK)
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)  # Wait for data
        
        read_data = dut.read_data.value.integer
        log_signal('read_data')
        
        if expected is not None:
            assert read_data == expected, (
                f"Data mismatch at addr {addr}: "
                f"Expected 0x{expected:02X}, got 0x{read_data:02X}"
            )
        return read_data
    

    dut.RST_N.value = 0
    dut.CLK.value = 0
    dut.write_en.value = 0
    dut.write_address.value = 0
    dut.write_data.value = 0
    dut.read_en.value = 0
    dut.read_address.value = 0
    
    # Start clock
    clock = Clock(dut.CLK, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))
    
    # Apply reset
    await reset()

    random_seed = cocotb.plusargs.get("SEED", random.randint(0, 2**32-1))
    random.seed(random_seed)
    cocotb.log.info(f"Using random seed: {random_seed}")
    
    # Test 1: Basic write/read
    await write_fifo(0, 0xAA)
    await read_fifo(0, 0xAA)
    
    # Test 2: Multiple addresses
    test_data = [(i, random.randint(0, 255)) for i in range(1, 5)]
    for addr, data in test_data:
        await write_fifo(addr, data)
    for addr, data in test_data:
        await read_fifo(addr, data)
    
    # Test 3: Random operations
    for _ in range(TEST_ITERATIONS):
        addr = random.randint(0, 15)
        data = random.randint(0, 255)
        
        await write_fifo(addr, data)
        await read_fifo(addr, data)
        
        # Random delay between 0-3 cycles
        for _ in range(random.randint(0, 3)):
            await RisingEdge(dut.CLK)
    
    # Test 4: Back-to-back operations
    cocotb.log.info("Testing back-to-back operations")
    burst_data = [(i, random.randint(0, 255)) for i in range(5, 10)]
    for addr, data in burst_data:
        await write_fifo(addr, data)
    for addr, data in burst_data:
        await read_fifo(addr, data)
    
 
    cocotb.log.info("Verifying all written data...")
    for addr, data in test_data + burst_data:
        await read_fifo(addr, data)
    
    cocotb.log.info("All tests completed successfully!")
