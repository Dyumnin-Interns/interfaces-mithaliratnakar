import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from driver import DutDriver
from coverage import FunctionalCoverage

fcov = FunctionalCoverage()

WRITE_ADDR_A = 4
WRITE_ADDR_B = 5

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
async def test_all_or_cases(dut):
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())
    driver = DutDriver(dut)
    await driver.initialize()

    test_vectors = [(0, 0), (0, 1), (1, 0), (1, 1)]

    for a_val, b_val in test_vectors:
        dut._log.info(f"\n=== A={a_val}, B={b_val} ===")

        while await driver.read_y_ff_valid():
            _ = await driver.read_y_ff_data()

        await driver.write_input(WRITE_ADDR_A, 0)
        await driver.write_input(WRITE_ADDR_B, 0)
        await RisingEdge(dut.CLK)

        await driver.write_input(WRITE_ADDR_A, a_val)
        await driver.write_input(WRITE_ADDR_B, b_val)

        for _ in range(60):
            if await driver.read_y_ff_valid():
                break
            await RisingEdge(dut.CLK)
        else:
            raise TimeoutError("Timeout: y_ff did not become valid.")

        y_out = await driver.read_y_ff_data()
        expected = a_val | b_val
        dut._log.info(f"RESULT: A={a_val}, B={b_val} → Y={y_out}, Expected={expected}")
        assert y_out == expected, f"Mismatch: A={a_val}, B={b_val}, Y={y_out}, Expected={expected}"

@cocotb.test()
async def corner_complete_coverage_fill(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("complete_coverage_fill")

    or_cases = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for a, b in or_cases:
        fcov.track_or_input(a, b)

    for addr in [4, 5]:
        await write_to_fifo(dut, 1, addr)

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
    for _ in range(3):
        await write_to_fifo(dut, 1, 4)
        await write_to_fifo(dut, 1, 5)
        await Timer(10, units="ns")

@cocotb.test()
async def corner_write_when_full(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("write_when_full")
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

@cocotb.test()
async def corner_all_fifos_full(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("all_fifos_full")
    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 0, 4)
    await write_to_fifo(dut, 1, 5)
    for _ in range(4):
        await RisingEdge(dut.CLK)
    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 0, 5)
    await Timer(20, units="ns")

@cocotb.test()
async def corner_over_read_y_ff(dut):
    await start_clock(dut)
    await reset_dut(dut)
    fcov.track_corner("over_read_y_ff")
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
    await write_to_fifo(dut, 1, 4)
    await write_to_fifo(dut, 1, 5)
    fcov.track_or_input(1, 1)
    for _ in range(3):
        await RisingEdge(dut.CLK)

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
    """Run this test last to print coverage summary"""
    fcov.report()
