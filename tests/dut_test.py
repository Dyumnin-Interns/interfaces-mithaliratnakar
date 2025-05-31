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
    
    # Test write operations
    dut.write_address.value = 4
    dut.write_data.value = 1
    dut.write_en.value = 1
    await RisingEdge(dut.CLK)
    
    dut.write_address.value = 5
    dut.write_data.value = 0
    await RisingEdge(dut.CLK)
    
    dut.write_en.value = 0
    
    # Wait for processing
    for _ in range(10):
        await RisingEdge(dut.CLK)
    
    # Test read operations
    dut.read_address.value = 0  # Check a_ff notFull
    await Timer(1, units="ns")
    print(f"a_ff notFull: {dut.read_data.value}")
    
    dut.read_address.value = 1  # Check b_ff notFull
    await Timer(1, units="ns")
    print(f"b_ff notFull: {dut.read_data.value}")
    
    dut.read_address.value = 2  # Check y_ff notEmpty
    await Timer(1, units="ns")
    print(f"y_ff notEmpty: {dut.read_data.value}")
    
    dut.read_address.value = 3  # Read y_ff data and dequeue
    dut.read_en.value = 1
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await Timer(1, units="ns")
    print(f"y_ff data: {dut.read_data.value}")
    
    # Add more test cases as needed
    await RisingEdge(dut.CLK)
