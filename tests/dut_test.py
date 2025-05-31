import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time
import random

@cocotb.test()
async def test_fifo_aligned(dut):
    """FIFO testbench aligned with waveform signals and robust checks"""
    
    
    DEBUG = True
    CLK_PERIOD_NS = 10  # 100MHz clock
    RESET_CYCLES = 2    # Minimum 2 clock cycles for reset
    TEST_ITERATIONS = 5 # Reduced for quicker debugging
    
    
   
    def log_signal(name):
        """Log signal value if it exists"""
        if DEBUG and hasattr(dut, name):
            val = getattr(dut, name).value
            cocotb.log.debug(f"{get_sim_time():>8}ps {name:15} = {val}")
    
    async def reset():
        """Proper reset sequence matching waveform"""
        cocotb.log.info("Applying reset...")
        dut.reset_n.value = 0  # Active low reset
        
        # Initialize all control signals
        dut.write_en.value = 0
        dut.read_en.value = 0
        dut.write_address.value = 0
        dut.write_data.value = 0
        dut.read_address.value = 0
        
        # Wait sufficient reset time
        for _ in range(RESET_CYCLES):
            await RisingEdge(dut.clk)  # Using 'clk' to match common naming
            
        # Release reset
        dut.reset_n.value = 1
        await RisingEdge(dut.clk)
        cocotb.log.info("Reset released")
        
        # Post-reset checks
        assert dut.write_en.value == 0, "Write enable not reset"
        assert dut.read_en.value == 0, "Read enable not reset"
        if hasattr(dut, 'write_rdy'):
            assert dut.write_rdy.value == 1, "Write not ready after reset"
        if hasattr(dut, 'read_rdy'):
            assert dut.read_rdy.value == 1, "Read not ready after reset"

    async def wait_ready(signal_name):
        """Wait for ready signal to be asserted"""
        if hasattr(dut, signal_name):
            while getattr(dut, signal_name).value != 1:
                await RisingEdge(dut.clk)
            await Timer(1, units="ns")  # Small delay after ready

    async def write_operation(addr, data):
        """Safe write operation with ready checking"""
        await wait_ready('write_rdy')
        
        cocotb.log.info(f"Writing 0x{data:02X} to addr {addr}")
        dut.write_address.value = addr
        dut.write_data.value = data
        dut.write_en.value = 1
        await RisingEdge(dut.clk)
        dut.write_en.value = 0
        
        # Verify write was accepted
        if hasattr(dut, 'write_rdy'):
            assert dut.write_rdy.value == 1, "Write not accepted"

    async def read_operation(addr, expected=None):
        """Safe read operation with ready checking"""
        await wait_ready('read_rdy')
        
        cocotb.log.info(f"Reading from addr {addr}")
        dut.read_address.value = addr
        dut.read_en.value = 1
        await RisingEdge(dut.clk)
        dut.read_en.value = 0
        await RisingEdge(dut.clk)  # Wait for data
        
        # Verify read data
        read_data = dut.read_data.value.integer
        if expected is not None:
            assert read_data == expected, (
                f"Data mismatch at addr {addr}: "
                f"Expected 0x{expected:02X}, got 0x{read_data:02X}"
            )
        return read_data

  
    required_signals = ['clk', 'reset_n', 'write_en', 'write_data', 
                       'write_address', 'read_en', 'read_data', 'read_address']
    for sig in required_signals:
        if not hasattr(dut, sig):
            raise cocotb.result.TestError(f"Required signal {sig} not found in DUT")

    # Start clock (using 'clk' to match common naming)
    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Apply reset
    await reset()

    
    test_data = [
        (0, 0xAA),  # Simple pattern
        (1, 0x55),  # Alternating bits
        (2, 0x01),  # Single bit
        (3, 0xFF)   # All ones
    ]

    # Test 1: Basic write/read sequence
    for addr, data in test_data:
        await write_operation(addr, data)
        readback = await read_operation(addr)
        assert readback == data, f"Basic test failed at addr {addr}"

    # Test 2: Verify data persistence
    cocotb.log.info("Verifying data persistence...")
    for addr, data in test_data:
        readback = await read_operation(addr, data)

    # Test 3: Random access test
    random.seed(cocotb.plusargs.get("SEED", 42))
    for _ in range(TEST_ITERATIONS):
        addr = random.randint(0, 15)
        data = random.randint(0, 255)
        await write_operation(addr, data)
        await read_operation(addr, data)
        await Timer(random.randint(1, 3)*CLK_PERIOD_NS, units="ns")

    cocotb.log.info("All tests completed successfully!")
