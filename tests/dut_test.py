import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.result import TestFailure


async def reset_dut(dut, duration_ns=100):
    """Reset DUT"""
    dut.RST.value = 1
    dut.CLR.value = 1
    await Timer(duration_ns, units="ns")
    dut.RST.value = 0
    dut.CLR.value = 0
    await RisingEdge(dut.CLK)
    await RisingEdge(dut.CLK)


@cocotb.test()
async def dut_test(dut):
    """Basic FIFO1 and FIFO2 test"""

    # Generate clock (Assuming clk toggles every 10 ns)
    cocotb.fork(clock_gen(dut.CLK))

    # Reset DUT
    await reset_dut(dut)

    # Test parameters
    data_width = len(dut.FIFO1_D_IN)
    test_data = [i for i in range(1, 4)]  # Test data sequence

    # Initialize inputs
    dut.FIFO1_ENQ.value = 0
    dut.FIFO1_DEQ.value = 0
    dut.FIFO2_ENQ.value = 0
    dut.FIFO2_DEQ.value = 0
    dut.FIFO1_D_IN.value = 0
    dut.FIFO2_D_IN.value = 0

    await RisingEdge(dut.CLK)

    # Enqueue data into FIFO1 and FIFO2
    for val in test_data:
        dut.FIFO1_D_IN.value = val
        dut.FIFO2_D_IN.value = val + 10  # Different data for FIFO2

        dut.FIFO1_ENQ.value = 1
        dut.FIFO2_ENQ.value = 1
        dut.FIFO1_DEQ.value = 0
        dut.FIFO2_DEQ.value = 0
        await RisingEdge(dut.CLK)

        dut.FIFO1_ENQ.value = 0
        dut.FIFO2_ENQ.value = 0
        await RisingEdge(dut.CLK)

    # Dequeue data from FIFO1 and FIFO2 and check correctness
    for i, val in enumerate(test_data):
        dut.FIFO1_DEQ.value = 1
        dut.FIFO2_DEQ.value = 1
        await RisingEdge(dut.CLK)

        fifo1_out = dut.FIFO1_D_OUT.value.integer
        fifo2_out = dut.FIFO2_D_OUT.value.integer

        if fifo1_out != val:
            raise TestFailure(f"FIFO1 output mismatch at {i}: expected {val}, got {fifo1_out}")
        if fifo2_out != val + 10:
            raise TestFailure(f"FIFO2 output mismatch at {i}: expected {val + 10}, got {fifo2_out}")

        dut.FIFO1_DEQ.value = 0
        dut.FIFO2_DEQ.value = 0
        await RisingEdge(dut.CLK)

    # Check FIFO empty signals
    if dut.FIFO1_EMPTY_N.value != 0:
        raise TestFailure("FIFO1 should be empty after dequeuing all data")
    if dut.FIFO2_EMPTY_N.value != 0:
        raise TestFailure("FIFO2 should be empty after dequeuing all data")

    # Check FIFO full signals (should not be full)
    if dut.FIFO1_FULL_N.value != 1:
        raise TestFailure("FIFO1 should not be full at end of test")
    if dut.FIFO2_FULL_N.value != 1:
        raise TestFailure("FIFO2 should not be full at end of test")


async def clock_gen(clk, period_ns=20):
    """Simple clock generator"""
    while True:
        clk.value = 0
        await Timer(period_ns // 2, units="ns")
        clk.value = 1
        await Timer(period_ns // 2, units="ns")
