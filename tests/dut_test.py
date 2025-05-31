import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

async def initialize(dut):
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())
    dut.RST_N.value = 0
    await Timer(20, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

@cocotb.test()
async def basic_test(dut):
    await initialize(dut)

    dut.write_address.value = 4
    dut.write_data.value = 1
    dut.write_en.value = 1
    await RisingEdge(dut.CLK)
    
    dut.write_address.value = 5
    dut.write_data.value = 0
    await RisingEdge(dut.CLK)
    
    dut.write_en.value = 0
    
    for _ in range(10):
        await RisingEdge(dut.CLK)
    
    dut.read_address.value = 0  
    await Timer(1, units="ns")
    print(f"a_ff notFull: {dut.read_data.value}")
    
    dut.read_address.value = 1 
    await Timer(1, units="ns")
    print(f"b_ff notFull: {dut.read_data.value}")
    
    dut.read_address.value = 2  
    await Timer(1, units="ns")
    print(f"y_ff notEmpty: {dut.read_data.value}")
    
    dut.read_address.value = 3  
    dut.read_en.value = 1
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await Timer(1, units="ns")
    print(f"y_ff data: {dut.read_data.value}")
    
    await RisingEdge(dut.CLK)
