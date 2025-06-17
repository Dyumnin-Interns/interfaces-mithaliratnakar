import cocotb
from cocotb.triggers import RisingEdge
from env import FifoEnv

@cocotb.test()
async def fifo_write_read_test(dut):
    env = FifoEnv(dut)
    await env.start()

    test_data = [0x12, 0x34, 0x56]

    for val in test_data:
        # Write one value
        dut.D_IN.value = val
        dut.write_en.value = 1
        await RisingEdge(dut.CLK)
        dut.write_en.value = 0
        await RisingEdge(dut.CLK)

        # Register expected value in scoreboard
        env.scoreboard.add_expected(val)
        dut._log.info(f"[TEST] Wrote: 0x{val:02X}")

        # Read that value
        dut.read_en.value = 1
        await RisingEdge(dut.CLK)
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)

    # Allow monitor to complete processing
    await RisingEdge(dut.CLK)
