import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge
from cocotb.utils import get_sim_time
from cocotb.binary import BinaryValue

@cocotb.test()
async def test_fifo_deep_debug(dut):
    """Enhanced FIFO test with comprehensive debugging"""
    
    CLK_PERIOD_NS = 10  
    RESET_CYCLES = 3    
    DEBUG = True
    TIMEOUT_CYCLES = 100
  
    def log_signals():
        if DEBUG:
            cocotb.log.info(f"Time {get_sim_time()} ps - Signals:")
            for sig in ['clk', 'reset_n', 'write_en', 'write_rdy', 
                       'read_en', 'read_rdy', 'write_data', 'read_data']:
                if hasattr(dut, sig):
                    val = getattr(dut, sig).value
                    cocotb.log.info(f"{sig:15} = {val}")

    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))
    
    dut.reset_n.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    dut.write_address.value = 0
    dut.write_data.value = 0
    dut.read_address.value = 0
  
    cocotb.log.info("Applying extended reset...")
    for _ in range(RESET_CYCLES):
        await RisingEdge(dut.clk)
    dut.reset_n.value = 1
    await RisingEdge(dut.clk)
    log_signals()
   if hasattr(dut, 'write_rdy'):
        await cocotb.triggers.First(dut.write_rdy.value == 1, Timer(CLK_PERIOD_NS*10, 'ns'))
        assert dut.write_rdy.value == 1, "Write not ready after reset"
    
    if hasattr(dut, 'read_rdy'):
        await cocotb.triggers.First(dut.read_rdy.value == 1, Timer(CLK_PERIOD_NS*10, 'ns'))
        assert dut.read_rdy.value == 1, "Read not ready after reset"
    
    test_cases = [
        (0, 0x55),  
        (1, 0xAA), 
        (2, 0x01), 
        (3, 0x80)  
    ]
    
    for addr, data in test_cases:
        cocotb.log.info(f"\n=== Writing 0x{data:02X} to addr {addr} ===")
       
        timeout = TIMEOUT_CYCLES
        while dut.write_rdy.value != 1 and timeout > 0:
            await RisingEdge(dut.clk)
            timeout -= 1
        assert timeout > 0,
       
        dut.write_address.value = addr
        dut.write_data.value = data
        dut.write_en.value = 1
        await RisingEdge(dut.clk)
        dut.write_en.value = 0
        log_signals()
        cocotb.log.info(f"\n=== Reading from addr {addr} ===")

        timeout = TIMEOUT_CYCLES
        while dut.read_rdy.value != 1 and timeout > 0:
            await RisingEdge(dut.clk)
            timeout -= 1
        assert timeout > 0, "Timeout waiting for read_rdy"
        

        dut.read_address.value = addr
        dut.read_en.value = 1
        await RisingEdge(dut.clk)
        dut.read_en.value = 0
        log_signals()
        
        await RisingEdge(dut.clk)

       read_val = dut.read_data.value
        if not read_val.is_resolvable:
            assert False, f"Read data is unresolved: {read_val}"
        
        read_int = read_val.integer
        assert read_int == data, (
            f"Data mismatch at addr {addr}: "
            f"Expected 0x{data:02X}, got 0x{read_int:02X}\n"
            f"Binary: {read_val.binstr}"
        )
        
        cocotb.log.info(f"Verified addr {addr} successfully")
    
    cocotb.log.info("All tests passed!")
