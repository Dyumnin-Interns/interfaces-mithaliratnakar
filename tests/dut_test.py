import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.result import TestFailure


@cocotb.test()
async def dut_test(dut):

    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())

    dut.RST_N.value = 0
    await Timer(20, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    print("Reset released.")

    dut.write_en.value = 1
    dut.write_address.value = 4
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)

    dut.write_address.value = 5
    dut.write_data.value = 0
    await RisingEdge(dut.CLK)

    dut.write_en.value = 0
    await RisingEdge(dut.CLK)

    dut.read_en.value = 1
    dut.read_address.value = 2
    await RisingEdge(dut.CLK)
    print(f"y_ff notEmpty = {dut.read_data.value}")

    dut.read_address.value = 3
    await RisingEdge(dut.CLK)
    print("Triggered y_ff deq")
    
    dut.read_address.value = 3
    await RisingEdge(dut.CLK)
    print(f"Read y_ff data = {dut.read_data.value}")

    dut.read_en.value = 0
    await Timer(50, units="ns")
