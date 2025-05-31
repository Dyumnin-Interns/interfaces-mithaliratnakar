import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

async def reset_dut(dut):
    dut.RST_N.value = 0
    await Timer(10, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

@cocotb.test()
async def basic_test(dut):
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Test writes (no assertions yet)
    dut.write_en.value = 1
    dut.write_address.value = 4  # a_ff
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)
    
    dut.write_address.value = 5  # b_ff
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)
    
    # Check reads (non-fatal checks)
    dut.write_en.value = 0
    dut.read_en.value = 1
    
    for addr in range(4):
        dut.read_address.value = addr
        await RisingEdge(dut.CLK)
        dut._log.info(f"Read addr {addr}: data={dut.read_data.value}")
    
    await Timer(100, units="ns")
    dut._log.info("Test completed (no assertions failed)")
