import cocotb
from cocotb.triggers import RisingEdge
from env import FifoEnv

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
    """Hits all functional coverage bins for FIFO"""
    env = FifoEnv(dut)
    await env.start()

    # Bin 1: write_when_empty
      GNU nano 7.2                                                                   dut_test.py                                                                                dut.DATA_IN.value = 0xAA
    dut.WR_EN.value = 1
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)
    env.coverage.sample(dut)  # sample while writing
    dut.WR_EN.value = 0
    await RisingEdge(dut.CLK)

    if dut.FULL.value == 0:
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

    # Bin 5: simultaneous read + write
    dut.DATA_IN.value = 0xCC
    dut.WR_EN.value = 1
    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    env.coverage.sample(dut)
    dut.WR_EN.value = 0
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)

    if dut.FULL.value == 0:
        env.scoreboard.add_expected(0xCC)

    env.coverage.report()
