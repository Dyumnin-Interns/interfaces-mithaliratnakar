import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from coverage import FunctionalCoverage

fcov = FunctionalCoverage()

async def start_clock(dut):
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())

async def reset_dut(dut):
    dut.RST_N.value = 0
    await Timer(50, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

async def write_to_fifo(dut, data, addr):
    dut.write_en.value = 1
    dut.write_address.value = addr
    dut.write_data.value = data
    await RisingEdge(dut.CLK)
    dut.write_en.value = 0
    await RisingEdge(dut.CLK)
    fcov.track_write_address(addr)

@cocotb.test()
async def corner_complete_coverage_fill(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("complete_coverage_fill")

    or_cases = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for a, b in or_cases:
        fcov.track_or_input(a, b)

    for addr in [4, 5]:
        await write_to_fifo(dut, 1, addr)  # already tracks

    for addr in [0, 1, 2, 3]:
        dut.read_en.value = 1
        dut.read_address.value = addr
        fcov.track_read_address(addr)
        await RisingEdge(dut.CLK)
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)

@cocotb.test()
async def corner_write_same_repeatedly(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("write_same_repeatedly")
    dut._log.info("Writing 1 repeatedly to a_ff and b_ff")
    for i in range(3):
        await write_to_fifo(dut, 1, 4)  # to a_ff
        await write_to_fifo(dut, 1, 5)  # to b_ff
        await Timer(10, units="ns")

@cocotb.test()
async def corner_write_when_full(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("write_when_full")
    dut._log.info("Testing write to a_ff when full")
    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 0, 4)
    await write_to_fifo(dut, 1, 4)
    await Timer(20, units="ns")

@cocotb.test()
async def corner_read_y_ff_when_empty(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("read_y_ff_when_empty")
    fcov.track_read_address(3)
    dut._log.info("Attempting to read from y_ff when it is empty")
    dut.read_en.value = 1
    dut.read_address.value = 3
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await RisingEdge(dut.CLK)
    read_val = dut.read_data.value.integer
    dut._log.info(f"Read value from y_ff when empty: {read_val}")
    assert read_val == 0, f"Expected 0 from empty y_ff, got {read_val}"

@cocotb.test()
async def corner_rapid_toggle(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("rapid_toggle")
    dut._log.info("Rapid toggling of write_en and read_en") 
    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 0, 5)
    for _ in range(3):
        await RisingEdge(dut.CLK)

    for i in range(4):
        dut.write_en.value = 1
        dut.write_address.value = 4
        dut.write_data.value = i % 2
        fcov.track_write_address(4)
        fcov.track_or_input(i % 2, i % 2)

        dut.read_en.value = 1
        dut.read_address.value = 3
        fcov.track_read_address(3)

        await RisingEdge(dut.CLK)

        dut.write_en.value = 0
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)

        dut._log.info(f"Cycle {i}: Wrote {i%2} to a_ff, tried reading from y_ff")

    await RisingEdge(dut.CLK)
    read_val = dut.read_data.value.integer
    dut._log.info(f"Final read from y_ff: {read_val}")

@cocotb.test()
async def corner_all_fifos_full(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("all_fifos_full")
    dut._log.info("Corner 3: Filling all FIFOs")
    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 0, 4)
    await write_to_fifo(dut, 1, 5)
    for _ in range(4):
        await RisingEdge(dut.CLK)
    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 0, 5)
    dut._log.info("Tried writing to full FIFOs. Observe ENQ signals in waveform.")
    await Timer(20, units="ns")

@cocotb.test()
async def corner_over_read_y_ff(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("over_read_y_ff")
    dut._log.info("Corner 4: Over-read y_ff")

    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 0, 5)
    fcov.track_or_input(1, 0)
    for _ in range(3):
        await RisingEdge(dut.CLK)

    for i in range(3):
        dut.read_en.value = 1
        dut.read_address.value = 3
        fcov.track_read_address(3)
        await RisingEdge(dut.CLK)
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)
        val = dut.read_data.value.integer
        dut._log.info(f"Read {i}: value from y_ff = {val}")

@cocotb.test()
async def corner_mid_reset(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("mid_reset")
    dut._log.info("Corner 5: Mid-operation reset")

    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 1, 5)
    fcov.track_or_input(1, 1)
    for _ in range(3):
        await RisingEdge(dut.CLK)

    dut._log.info("Asserting reset mid-test")
    dut.RST_N.value = 0
    await Timer(30, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

    await write_to_fifo(dut, 0, 4)
    await write_to_fifo(dut, 1, 5)
    fcov.track_or_input(0, 1)
    for _ in range(3):
        await RisingEdge(dut.CLK)

    dut.read_en.value = 1
    dut.read_address.value = 3
    fcov.track_read_address(3)
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await RisingEdge(dut.CLK)

    val = dut.read_data.value.integer
    dut._log.info(f"Read after reset: y_ff = {val}")

@cocotb.test()
async def zzz_final_coverage_report(dut):
    """Run this test last to report coverage"""
    fcov.report()
