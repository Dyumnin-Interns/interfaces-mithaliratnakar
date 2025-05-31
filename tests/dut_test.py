import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

async def initialize(dut):
    clock = Clock(dut.clk, 10, units="ns")  # 100MHz clock
    cocotb.start_soon(clock.start())
    dut.reset_n.value = 0
    await Timer(20, units="ns")
    dut.reset_n.value = 1
    await RisingEdge(dut.clk)

@cocotb.test()
async def basic_test(dut):
    await initialize(dut)

    dut._log.info("Starting test")
    
    dut.write_addr.value = 4
    dut.write_data.value = 1
    dut.write_en.value = 1
    await RisingEdge(dut.clk)
    dut._log.info(f"Write to addr 4: {dut.write_data.value}")
    
    dut.write_addr.value = 5
    dut.write_data.value = 0
    await RisingEdge(dut.clk)
    dut._log.info(f"Write to addr 5: {dut.write_data.value}")
    
    dut.write_en.value = 0
    
    for i in range(10):
        await RisingEdge(dut.clk)
    
    test_cases = [
        (0, "a_ff notFull"),
        (1, "b_ff notFull"),
        (2, "y_ff notEmpty"),
        (3, "y_ff data")
    ]
    
    for addr, desc in test_cases:
        dut.read_addr.value = addr
        await Timer(1, units="ns")
        dut._log.info(f"{desc}: {dut.read_data.value}")
        if addr == 3:  
            dut.read_en.value = 1
            await RisingEdge(dut.clk)
            dut.read_en.value = 0
    
    await RisingEdge(dut.clk)
    dut._log.info("Test completed")
