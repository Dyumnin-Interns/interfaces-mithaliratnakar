import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

async def reset_dut(dut):
    dut.RST_N.value = 0  # Active-low reset asserted
    await Timer(20, units="ns")
    dut.RST_N.value = 1  # Release reset
    await RisingEdge(dut.CLK)
    await Timer(10, units="ns")  # allow signals to settle

@cocotb.test()
async def smoke_test(dut):
    """Basic sanity check with no assertions."""

    # Start clock
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.write_en.value = 0
    dut.write_address.value = 0
    dut.write_data.value = 0
    dut.read_en.value = 0
    dut.read_address.value = 0

    await reset_dut(dut)

    # Perform writes
    dut.write_en.value = 1

    dut.write_address.value = 4  # write to a_ff
    dut.write_data.value = 1
    await RisingEdge(dut.CLK)

    dut.write_address.value = 5  # write to b_ff
    dut.write_data.value = 0
    await RisingEdge(dut.CLK)

    dut.write_en.value = 0

    # Perform reads
    dut.read_en.value = 1
    for addr in range(4):
        dut.read_address.value = addr
        await RisingEdge(dut.CLK)
        dut._log.info(f"Read addr {addr}: data={dut.read_data.value}")

    await Timer(100, units="ns")
    dut._log.info("Smoke test passed (no assertions)")
