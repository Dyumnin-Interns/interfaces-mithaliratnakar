import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from env import FifoEnv

async def reset_dut(dut):
    dut.RST_N.value = 0
    await Timer(5, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    await RisingEdge(dut.CLK)

@cocotb.test()
async def fifo_write_read_test(dut):
    env = FifoEnv(dut)
    await env.start()

    test_data = [0x12, 0x34, 0x56]
    for val in test_data:
        dut.DATA_IN.value = val
        dut.WR_EN.value = 1
        env.coverage.sample(dut)

        await RisingEdge(dut.CLK)
        dut.WR_EN.value = 0

        if not dut.FULL.value:
            env.scoreboard.add_expected(val)
            dut._log.info(f"[TEST] Wrote: 0x{val:02X}")

        await RisingEdge(dut.CLK)

        # Read back
        dut.RD_EN.value = 1
        env.coverage.sample(dut)
        await RisingEdge(dut.CLK)
        dut.RD_EN.value = 0
        await RisingEdge(dut.CLK)

@cocotb.test()
async def fifo_corner_coverage_test(dut):
    env = FifoEnv(dut)
    await env.start()

    # Bin 1: write_when_empty
    dut.DATA_IN.value = 0xAA
    dut.WR_EN.value = 1
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)
    env.coverage.sample(dut)
    dut.WR_EN.value = 0
    await RisingEdge(dut.CLK)
    if not dut.FULL.value:
        env.scoreboard.add_expected(0xAA)

    # Bin 2: write_when_full
    dut.DATA_IN.value = 0xBB
    dut.WR_EN.value = 1
    await RisingEdge(dut.CLK)
    env.coverage.sample(dut)
    dut.WR_EN.value = 0
    await RisingEdge(dut.CLK)

    # Bin 3: read_when_full
    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    env.coverage.sample(dut)
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)

    # Bin 4: read_when_empty
    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    env.coverage.sample(dut)
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)

    # Bin 5: simultaneous read/write
    dut.DATA_IN.value = 0xCC
    dut.WR_EN.value = 1
    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    env.coverage.sample(dut)
    dut.WR_EN.value = 0
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)
    if not dut.FULL.value:
        env.scoreboard.add_expected(0xCC)

    env.coverage.report()

@cocotb.test()
async def fifo_same_value_repeatedly(dut):
    env = FifoEnv(dut)
    await env.start()
    repeated_value = 0xAB

    for _ in range(4):
        dut.DATA_IN.value = repeated_value
        dut.WR_EN.value = 1
        await RisingEdge(dut.CLK)
        dut.WR_EN.value = 0
        if not dut.FULL.value:
            env.scoreboard.add_expected(repeated_value)
        await RisingEdge(dut.CLK)

    for _ in range(4):
        dut.RD_EN.value = 1
        await RisingEdge(dut.CLK)
        dut.RD_EN.value = 0
        await RisingEdge(dut.CLK)

@cocotb.test()
async def fifo_rapid_toggle_wr_rd(dut):
    env = FifoEnv(dut)
    await env.start()
    toggle_data = [0x11, 0x22, 0x33]

    for val in toggle_data:
        dut.DATA_IN.value = val
        dut.WR_EN.value = 1
        await RisingEdge(dut.CLK)
        dut.WR_EN.value = 0
        if not dut.FULL.value:
            env.scoreboard.add_expected(val)

        await RisingEdge(dut.CLK)
        dut.RD_EN.value = 1
        await RisingEdge(dut.CLK)
        dut.RD_EN.value = 0
        await RisingEdge(dut.CLK)

@cocotb.test()
async def fifo_reset_while_full(dut):
    env = FifoEnv(dut)
    await env.start()

    for val in [0x11, 0x22, 0x33]:
        dut.DATA_IN.value = val
        dut.WR_EN.value = 1
        await RisingEdge(dut.CLK)
        dut.WR_EN.value = 0
        await RisingEdge(dut.CLK)
        if not dut.FULL.value:
            env.scoreboard.add_expected(val)

    dut._log.info("[TEST] FIFO filled. Applying reset now.")
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)

    assert dut.EMPTY.value == 1, "FIFO not empty after reset!"
    assert dut.FULL.value == 0, "FIFO full flag still high after reset!"
    dut._log.info("[TEST] Reset handled correctly while FIFO was full.")

@cocotb.test()
async def fifo_one_cycle_toggle(dut):
    env = FifoEnv(dut)
    await env.start()

    test_data = [0x44, 0x55]
    for val in test_data:
        dut.DATA_IN.value = val
        dut.WR_EN.value = 1
        dut.RD_EN.value = 1
        await RisingEdge(dut.CLK)
        dut.WR_EN.value = 0
        dut.RD_EN.value = 0
        await RisingEdge(dut.CLK)

        env.coverage.sample(dut)
        dut._log.info(f"[TEST] Wrote and Read: 0x{val:02X}")
        if not dut.FULL.value:
            env.scoreboard.add_expected(val)

    await Timer(10, units="ns")
