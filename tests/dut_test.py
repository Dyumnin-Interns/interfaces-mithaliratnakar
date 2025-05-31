import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time
import random
from cocotb.queue import Queue

class FIFOSequenceItem:
    def __init__(self):
        self.addr = 0
        self.data = 0
        self.delay = 0

class FIFOTransaction:
    def __init__(self):
        self.write_en = 0
        self.write_addr = 0
        self.write_data = 0
        self.read_en = 0
        self.read_addr = 0
        self.expected_data = 0

@cocotb.test()
async def test_fifo_randomized(dut):
    """FIFO test with randomized write control and sequence checking"""

    CLK_PERIOD_NS = 10
    RESET_CYCLES = 2
    TEST_ITERATIONS = 20
    DATA_QUEUE = Queue()
    

    def randomize_transaction():
        """Generate random transaction with constraints"""
        item = FIFOSequenceItem()
        item.addr = random.randint(0, 7)  # 3-bit address
        item.data = random.randint(0, 255)
        item.delay = random.randint(0, 3)
        return item

    async def reset():
        """Reset sequence"""
        dut.reset_n.value = 0
        dut.write_en.value = 0
        dut.read_en.value = 0
        dut.write_address.value = 0
        dut.read_address.value = 0
        
        for _ in range(RESET_CYCLES):
            await RisingEdge(dut.clk)
            
        dut.reset_n.value = 1
        await RisingEdge(dut.clk)
        
        assert dut.write_rdy.value == 1, "Write not ready after reset"
        assert dut.read_rdy.value == 1, "Read not ready after reset"

    async def driver():
        """Randomized transaction driver"""
        for _ in range(TEST_ITERATIONS):
            item = randomize_transaction()
            
            # Random delay before write
            for _ in range(item.delay):
                await RisingEdge(dut.clk)
            
            # Create write transaction
            trans = FIFOTransaction()
            trans.write_en = 1
            trans.write_addr = item.addr
            trans.write_data = item.data
            
            # Wait for write ready
            while dut.write_rdy.value != 1:
                await RisingEdge(dut.clk)
            
            # Drive write signals
            dut.write_en.value = trans.write_en
            dut.write_address.value = trans.write_addr
            dut.write_data.value = trans.write_data
            await RisingEdge(dut.clk)
            dut.write_en.value = 0
            
            # Store expected read data
            trans.expected_data = item.data
            await DATA_QUEUE.put(trans)
            
            cocotb.log.info(f"Driven write: addr={item.addr}, data=0x{item.data:02X}")

    async def monitor():
        """Transaction monitor and checker"""
        for _ in range(TEST_ITERATIONS):
            # Get expected transaction
            expected = await DATA_QUEUE.get()
            
            # Wait for read ready
            while dut.read_rdy.value != 1:
                await RisingEdge(dut.clk)
            
            # Drive read signals
            dut.read_en.value = 1
            dut.read_address.value = expected.write_addr
            await RisingEdge(dut.clk)
            dut.read_en.value = 0
            
            # Capture read data
            await RisingEdge(dut.clk)
            actual_data = dut.read_data.value.integer
            
            # Verify
            assert actual_data == expected.expected_data, (
                f"Data mismatch at addr {expected.write_addr}: "
                f"Expected 0x{expected.expected_data:02X}, "
                f"got 0x{actual_data:02X}"
            )
            
            cocotb.log.info(f"Verified read: addr={expected.write_addr}, data=0x{actual_data:02X}")

 
    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())
    
    # Apply reset
    await reset()
    
    # Run driver and monitor in parallel
    await cocotb.start(driver())
    await cocotb.start(monitor())
    
    # Wait for completion
    for _ in range(TEST_ITERATIONS * 5):  # Timeout safeguard
        await RisingEdge(dut.clk)
    
    cocotb.log.info("All randomized transactions verified successfully!")
