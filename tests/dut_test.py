import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, First
from cocotb.utils import get_sim_time
from cocotb.binary import BinaryValue
import random

@cocotb.test()
async def test_fifo_deep_debug(dut):
    """FIFO test with transaction-level debugging and failure isolation"""
    
    # Configuration - REPLACE WITH YOUR ACTUAL PARAMETERS
    FIFO_DEPTH = 8  # Example - adjust based on your design
    CLK_PERIOD_NS = 10
    RANDOM_SEED = random.randint(0, 2**32-1)
    random.seed(RANDOM_SEED)
    
    # Log test configuration
    dut._log.info(f"Starting test with RANDOM_SEED={RANDOM_SEED}")
    dut._log.info(f"FIFO Depth: {FIFO_DEPTH}")
    
    # Clock generation
    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))
    
    # Initialize
    dut.reset_n.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    dut.write_data.value = 0
    dut.write_address.value = 0
    dut.read_address.value = 0
    
    # Extended reset sequence
    for _ in range(5):
        await RisingEdge(dut.clk)
    dut.reset_n.value = 1
    await RisingEdge(dut.clk) # Wait one full cycle after reset de-assertion
    
    # --- Test Scenario Builder ---
    class TestScenario:
        def __init__(self):
            self.expected_data = {}  # addr: data
            self.operations = []
            self.fifo_count = 0
            
        def add_write(self, addr, data, sim_time):
            self.expected_data[addr] = data
            self.operations.append(('write', addr, data, sim_time))
            self.fifo_count = min(self.fifo_count + 1, FIFO_DEPTH)
            
        def add_read(self, addr, actual_data, sim_time):
            self.operations.append(('read', addr, actual_data, sim_time))
            if addr in self.expected_data:
                expected = self.expected_data[addr]
                if actual_data != expected:
                    self.report_failure(addr, expected, actual_data)
            self.fifo_count = max(self.fifo_count - 1, 0)
            
        def report_failure(self, addr, expected, actual):
            dut._log.error("\n" + "="*60)
            dut._log.error("DATA MISMATCH DETECTED")
            dut._log.error(f"Address: {addr}")
            dut._log.error(f"Expected: 0x{expected:02X} ({bin(expected)})")
            dut._log.error(f"Received: 0x{actual:02X} ({bin(actual)})")
            dut._log.error("\nOperation History:")
            for i, op in enumerate(self.operations[-10:]):  # Last 10 ops
                dut._log.error(f"{i:2d}: {op[0]:5s} addr={op[1]} data=0x{op[2]:02X} @ {op[3]} ps")
            dut._log.error("="*60 + "\n")
            assert False, f"Data mismatch at address {addr}"
            
    scenario = TestScenario()
    
    # --- Test Sequence ---
    try:
        # First verify basic write/read
        addr = 0
        test_data = 0x55
        dut._log.info(f"\n=== Basic Write/Read Test ===")
        
        # Write
        await First(RisingEdge(dut.write_rdy), Timer(100, 'ns'))
        dut.write_address.value = addr
        dut.write_data.value = test_data
        dut.write_en.value = 1
        scenario.add_write(addr, test_data, get_sim_time())
        await Timer(1, units='ns') # Added: Small delay to ensure signals settle
        await RisingEdge(dut.clk)
        dut.write_en.value = 0
        
        # Read
        await First(RisingEdge(dut.read_rdy), Timer(100, 'ns'))
        dut.read_address.value = addr # Corrected: Completed assignment
        dut.read_en.value = 1
        await Timer(1, units='ns') # Added: Small delay to ensure signals settle
        await RisingEdge(dut.clk)
        dut.read_en.value = 0
        await RisingEdge(dut.clk)  # Data delay
        read_val = dut.read_data.value
        scenario.add_read(addr, read_val.integer, get_sim_time())
        
        # Random traffic test
        dut._log.info(f"\n=== Random Traffic Test ===")
        for i in range(20):  # Reduced from 100 for quicker failure
            is_write = random.choice([True, False])
            addr = random.randint(0, FIFO_DEPTH-1)
            
            if is_write or scenario.fifo_count == 0:
                # Force write if empty or random choice
                data = random.randint(0, 255)
                await First(RisingEdge(dut.write_rdy), Timer(100, 'ns'))
                dut.write_address.value = addr
                dut.write_data.value = data
                dut.write_en.value = 1
                scenario.add_write(addr, data, get_sim_time())
                await Timer(1, units='ns') # Added: Small delay
                await RisingEdge(dut.clk)
                dut.write_en.value = 0
            else:
                # Read operation
                await First(RisingEdge(dut.read_rdy), Timer(100, 'ns'))
                dut.read_address.value = addr
                dut.read_en.value = 1
                await Timer(1, units='ns') # Added: Small delay
                await RisingEdge(dut.clk)
                dut.read_en.value = 0
                await RisingEdge(dut.clk)  # Data delay
                read_val = dut.read_data.value
                scenario.add_read(addr, read_val.integer, get_sim_time()) # Corrected to use updated read_val
                
    except Exception as e:
        dut._log.error(f"Test failed with RANDOM_SEED={RANDOM_SEED}")
        dut._log.error(f"Last operation: {scenario.operations[-1] if scenario.operations else 'None'}")
        raise
