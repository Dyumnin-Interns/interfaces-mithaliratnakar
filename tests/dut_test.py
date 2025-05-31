import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge
from cocotb.utils import get_sim_time

@cocotb.test()
async def test_fifo_basic_operations(dut):
    """Test basic FIFO operations with extensive debugging"""
 
    cocotb.log.setLevel(cocotb.log.DEBUG)
    debug = True  # Set to False to reduce log output

    def log_signal(name):
        if debug and hasattr(dut, name):
            cocotb.log.debug(f"{name} = {getattr(dut, name).value}")
    
    async def reset():
        cocotb.log.info("Resetting DUT")
        dut.RST_N.value = 0
        dut.write_en.value = 0
        dut.read_en.value = 0
        await Timer(20, units="ns")
        dut.RST_N.value = 1
        await RisingEdge(dut.CLK)
        cocotb.log.info("Reset complete")
    
    # Start clock (100MHz)
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start(start_high=False))
    
    await reset()

    async def test_write_read(addr, data):
        """Helper function to test single write-read cycle"""
        cocotb.log.info(f"\n=== Testing addr {addr} with data 0x{data:02X} ===")
        
        # Write operation
        cocotb.log.debug("Starting write operation")
        dut.write_address.value = addr
        dut.write_data.value = data
        dut.write_en.value = 1
        await RisingEdge(dut.CLK)
        log_signal('write_en')
        log_signal('write_address')
        log_signal('write_data')
        dut.write_en.value = 0
        
        # Wait 2 cycles (adjust based on your FIFO latency)
        for i in range(2):
            await RisingEdge(dut.CLK)
            cocotb.log.debug(f"Wait cycle {i+1}")
            log_signal('full') if hasattr(dut, 'full') else None
            log_signal('empty') if hasattr(dut, 'empty') else None
        
        # Read operation
        cocotb.log.debug("Starting read operation")
        dut.read_address.value = addr
        dut.read_en.value = 1
        await RisingEdge(dut.CLK)
        log_signal('read_en')
        log_signal('read_address')
        dut.read_en.value = 0
        
        # Wait for data to appear
        await RisingEdge(dut.CLK)
        read_data = dut.read_data.value.integer
        cocotb.log.info(f"Read data from addr {addr}: 0x{read_data:02X}")
        
        # Verification with better error reporting
        if read_data != data:
            cocotb.log.error(f"MISMATCH at addr {addr}: Expected 0x{data:02X}, got 0x{read_data:02X}")
            # Additional debug for failed case
            for _ in range(3):
                await RisingEdge(dut.CLK)
                log_signal('read_data')
            assert False, f"Data mismatch at addr {addr}"
        
        return read_data

    import os
    random_seed = int(os.getenv('RANDOM_SEED', '123456789'))
    cocotb.log.info(f"Running with RANDOM_SEED={random_seed}")
    
    # Simple test pattern that should work for any FIFO
    test_pattern = [
        (0, 0xAA),
        (1, 0x55),
        (2, 0x01),
        (3, 0x80),
        (4, 0xFF)
    ]
    
    # Run tests
    for addr, data in test_pattern:
        await test_write_read(addr, data)

    cocotb.log.info("Running additional diagnostics...")
    
    # Check if all addresses retain their values
    cocotb.log.info("Verifying address retention...")
    for addr, expected_data in test_pattern:
        dut.read_address.value = addr
        dut.read_en.value = 1
        await RisingEdge(dut.CLK)
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)
        read_data = dut.read_data.value.integer
        if read_data != expected_data:
            cocotb.log.error(f"Retention failed at addr {addr}: Expected 0x{expected_data:02X}, got 0x{read_data:02X}")
            assert False, f"Address {addr} retention failure"
    
    cocotb.log.info("All tests completed successfully!")
