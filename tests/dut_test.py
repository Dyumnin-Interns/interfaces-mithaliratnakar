import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from env import DutEnv
WRITE_ADDR_A = 4
WRITE_ADDR_B = 5
READ_ADDR_Y_VALID = 2
READ_ADDR_Y_DATA = 3
@cocotb.test()
async def test_all_or_cases(dut):
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())
    env = DutEnv(dut)
    await env.reset()
    test_vectors = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for a_val, b_val in test_vectors:
        dut._log.info(f"\n===== Testing combination: A={a_val}, B={b_val} =====")
        await env.driver.write_input(WRITE_ADDR_A, a_val)
        await env.driver.write_input(WRITE_ADDR_B, b_val)
        for _ in range(1):
            await RisingEdge(dut.CLK)
        while not await env.driver.read_y_ff_valid():
            await RisingEdge(dut.CLK)
            
