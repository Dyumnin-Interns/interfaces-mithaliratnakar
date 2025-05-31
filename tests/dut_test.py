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
    # Create clock
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset DUT
    await reset_dut(dut)
    
    # Test write operations
    dut.write_en.value = 1
    dut.write_address.value = 4
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)
    
    dut.write_address.value = 5
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)
    
    # Test read operations
    dut.write_en.value = 0
    dut.read_en.value = 1
    
    # Read FIFO status
    for addr in range(4):
        dut.read_address.value = addr
        await RisingEdge(dut.CLK)
        await Timer(1, units="ns")
        print(f"Address {addr}: {dut.read_data.value}")
    
    # Add more test cases as needed
    await Timer(100, units="ns")
