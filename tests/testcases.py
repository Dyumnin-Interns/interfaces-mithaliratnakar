import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from env import FifoEnv

async def reset_dut(dut):
    dut.RST.value = 1
    dut.WR_EN.value = 0
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)
    dut.RST.value = 0
    await RisingEdge(dut.CLK)

@cocotb.test()
async def test_fifo_basic_write_read(dut):
    """Basic test: write one value, read it back"""
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())

    await reset_dut(dut)

    dut.DATA_IN.value = 0xAB
    dut.WR_EN.value = 1
    await RisingEdge(dut.CLK)
    dut.WR_EN.value = 0
    await RisingEdge(dut.CLK)

    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    dut.RD_EN.value = 0
    await RisingEdge(dut.CLK)
    assert dut.DATA_OUT.value == 0xAB, f"Expected 0xAB, got {hex(int(dut.DATA_OUT.value))}"
    dut._log.info("Basic write-read test passed.")

@cocotb.test()
async def test_read_when_empty(dut):
    """Corner Case: Try reading from an empty FIFO"""
       cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())
    await reset_dut(dut)

    dut._log.info("Attempting read when FIFO is empty")
    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    dut.RD_EN.value = 0

    assert dut.EMPTY.value == 1 or dut.empty_n.value == 0, "FIFO should be empty"
    dut._log.info(f"DATA_OUT after empty read: {hex(int(dut.DATA_OUT.value))}")


@cocotb.test()
async def test_fifo_overwrite_corner_case(dut):
    """Corner Case 3: Write Twice Without Read — Check Overwrite Behavior"""

    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())
    dut.RST.value = 1
    await RisingEdge(dut.CLK)
    dut.RST.value = 0
    await RisingEdge(dut.CLK)

    dut.DATA_IN.value = 0xAA
    dut.WR_EN.value = 1
    await RisingEdge(dut.CLK)

    dut.DATA_IN.value = 0xBB
    await RisingEdge(dut.CLK)

    dut.WR_EN.value = 0
    await RisingEdge(dut.CLK)

    dut.RD_EN.value = 1
    await RisingEdge(dut.CLK)
    dut.RD_EN.value = 0

    output_val = dut.DATA_OUT.value.integer
    dut._log.info(f"Read value: {hex(output_val)}")
    expected_val = 0xBB  # or 0xAA based on design
    assert output_val == expected_val, f"Expected {hex(expected_val)}, got {hex(output_val)}"

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
        # WR_EN high for 1 cycle
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
    """Corner Case: Apply reset while FIFO is full"""
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

    assert dut.EMPTY.value == 1, " FIFO not empty after reset!"
    assert dut.FULL.value == 0, " FIFO full flag still high after reset!"
    dut._log.info("[TEST] Reset handled correctly while FIFO was full.")

@cocotb.test()
async def fifo_one_cycle_toggle(dut):
    """Corner Case: Rapid 1-cycle toggle of WR_EN and RD_EN"""
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
        else:
            dut._log.warning(f"[TEST] FIFO full. Skipping expected for 0x{val:02X}")

    await Timer(10, units="ns")  
