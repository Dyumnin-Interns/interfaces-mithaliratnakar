import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, First
from cocotb.utils import get_sim_time
from cocotb.binary import BinaryValue
import random

@cocotb.test()
async def test_fifo_randomized(dut):
    """FIFO test with randomized traffic and detailed debugging"""
    
    # Configuration
    CLK_PERIOD_NS = 10
    RESET_CYCLES = 5  # Extended reset for stability
    TEST_ITERATIONS = 20
    RANDOM_SEED = random.randint(0, 2**32-1)
    random.seed(RANDOM_SEED)
    
    # Log test configuration
    dut._log.info(f"Starting test with RANDOM_SEED={RANDOM_SEED}")
    
    # Clock generation with phase offset
    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False, phase=3))
    
    # Initialize
    dut.reset_n.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    dut.write_data.value = 0
    dut.write_address.value = 0
    dut.read_address.value = 0
    
    # Reset sequence with waveform markers
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.reset_n.value = 1
    await Timer(2, 'ns')  # Hold after reset
    
    # Post-reset checks
    assert dut.reset_n.value == 1, "Reset not deasserted"
    await First(
        RisingEdge(dut.clk),
        Timer(100, 'ns')
    )
    
    # Test operations storage for debugging
    operations = []
    
    for i in range(TEST_ITERATIONS):
        # Randomize operation type (write or read)
        is_write = random.choice([True, False])
        addr = random.randint(0, 7)
        data = random.randint(0, 255) if is_write else None
        
        try:
            if is_write:
                # Write operation
                await First(
                    RisingEdge(dut.clk) & (dut.write_rdy.value == 1),
                    Timer(200, 'ns')
                )
                assert dut.write_rdy.value == 1, f"Write timeout @ iter {i}"
                
                dut.write_address.value = addr
                dut.write_data.value = data
                dut.write_en.value = 1
                await RisingEdge(dut.clk)
                dut.write_en.value = 0
                
                operations.append(('write', addr, data, get_sim_time()))
                
            else:
                # Read operation
                await First(
                    RisingEdge(dut.clk) & (dut.read_rdy.value == 1),
                    Timer(200, 'ns')
                )
                assert dut.read_rdy.value == 1, f"Read timeout @ iter {i}"
                
                dut.read_address.value = addr
                dut.read_en.value = 1
                await RisingEdge(dut.clk)
                dut.read_en.value = 0
                await RisingEdge(dut.clk)  # Data delay
                
                read_val = dut.read_data.value
                operations.append(('read', addr, read_val.integer, get_sim_time()))
                
                # Verify against last write to same address
                expected_data = next(
                    (op[2] for op in reversed(operations) 
                    if op[0] == 'write' and op[1] == addr),
                    None
                )
                
                if expected_data is not None:
                    assert read_val.integer == expected_data, (
                        f"Data mismatch @ addr {addr} (iter {i}):\n"
                        f"Expected: 0x{expected_data:02X} ({bin(expected_data)})\n"
                        f"Received: 0x{read_val.integer:02X} ({read_val.binstr})\n"
                        f"Operations history:\n{format_operations(operations)}"
                    )
                    
        except AssertionError as e:
            dut._log.error(f"Failure at iteration {i}:")
            dut._log.error(f"Current operation: {'write' if is_write else 'read'} addr {addr}")
            if is_write:
                dut._log.error(f"Write data: 0x{data:02X}")
            else:
                dut._log.error(f"Read data: 0x{read_val.integer:02X}")
            dut._log.error(f"Operations history:\n{format_operations(operations)}")
            raise

def format_operations(ops):
    """Format operations history for debugging"""
    return "\n".join(
        f"{i:3d}: {op[0]:5s} addr={op[1]} data=0x{op[2]:02X} @ {op[3]} ps"
        for i, op in enumerate(ops)
    )
