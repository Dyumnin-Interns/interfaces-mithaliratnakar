import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time
import random

async def wait_for_ready(signal, clk, label="signal", timeout_cycles=100):
    for _ in range(timeout_cycles):
        if signal.value.is_resolvable and signal.value == 1:
            return
        await RisingEdge(clk)
    raise AssertionError(f"{label} not ready within timeout")


@cocotb.test()
async def test_fifo_deep_debug(dut):
    """FIFO test with transaction-level debugging and failure isolation"""

    # Configuration
    FIFO_DEPTH = 8
    CLK_PERIOD_NS = 10
    RANDOM_SEED = random.randint(0, 2**32 - 1)
    random.seed(RANDOM_SEED)

    # Logging test parameters
    dut._log.info(f"Starting test with RANDOM_SEED={RANDOM_SEED}")
    dut._log.info(f"FIFO Depth: {FIFO_DEPTH}")

    # Clock generation
    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Initialize inputs
    dut.reset_n.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    dut.write_data.value = 0
    dut.write_address.value = 0
    dut.read_address.value = 0

    # Extended reset
    for _ in range(5):
        await RisingEdge(dut.clk)
    dut.reset_n.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Wait until write_rdy becomes valid
    await wait_for_ready(dut.write_rdy, dut.clk, "write_rdy after reset")

    # --- Test Scenario Class ---
    class TestScenario:
        def __init__(self):
            self.expected_data = {}
            self.operations = []
            self.fifo_count = 0

        def add_write(self, addr, data, sim_time):
            self.expected_data[addr] = data
            self.operations.append(('write', addr, data, sim_time))
            self.fifo_count = min(self.fifo_count + 1, FIFO_DEPTH)

        def add_read(self, addr, actual_data, sim_time):
            self.operations.append(('read', addr, actual_data, sim_time))
            if addr in self.expected_data:
                expected = self.expected_data[addr]
                if actual_data != expected:
                    self.report_failure(addr, expected, actual_data)
            self.fifo_count = max(self.fifo_count - 1, 0)

        def report_failure(self, addr, expected, actual):
            dut._log.error("\n" + "=" * 60)
            dut._log.error("DATA MISMATCH DETECTED")
            dut._log.error(f"Address: {addr}")
            dut._log.error(f"Expected: 0x{expected:02X} ({bin(expected)})")
            dut._log.error(f"Received: 0x{actual:02X} ({bin(actual)})")
            dut._log.error("\nOperation History:")
            for i, op in enumerate(self.operations[-10:]):
                dut._log.error(f"{i:2d}: {op[0]:5s} addr={op[1]} data=0x{op[2]:02X} @ {op[3]} ps")
            dut._log.error("=" * 60 + "\n")
            assert False, f"Data mismatch at address {addr}"

    scenario = TestScenario()

    # --- Basic Write/Read Test ---
    dut._log.info("\n=== Basic Write/Read Test ===")
    addr = 0
    test_data = 0x55

    await wait_for_ready(dut.write_rdy, dut.clk, "write_rdy")
    dut.write_address.value = addr
    dut.write_data.value = test_data
    dut.write_en.value = 1
    scenario.add_write(addr, test_data, get_sim_time())
    await RisingEdge(dut.clk)
    dut.write_en.value = 0

    await wait_for_ready(dut.read_rdy, dut.clk, "read_rdy")
    dut.read_address.value = addr
    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    dut.read_en.value = 0
    await RisingEdge(dut.clk)
    read_val = dut.read_data.value
    scenario.add_read(addr, read_val.integer, get_sim_time())

    # --- Randomized Read/Write Traffic ---
    dut._log.info("\n=== Random Traffic Test ===")
    for _ in range(20):  # Use more iterations for stress testing
        addr = random.randint(0, FIFO_DEPTH - 1)
        is_write = random.choice([True, False])

        if is_write or scenario.fifo_count == 0:
            # Write
            data = random.randint(0, 255)
            await wait_for_ready(dut.write_rdy, dut.clk, "write_rdy")
            dut.write_address.value = addr
            dut.write_data.value = data
            dut.write_en.value = 1
            scenario.add_write(addr, data, get_sim_time())
            await RisingEdge(dut.clk)
            dut.write_en.value = 0
        else:
            # Read
            await wait_for_ready(dut.read_rdy, dut.clk, "read_rdy")
            dut.read_address.value = addr
            dut.read_en.value = 1
            await RisingEdge(dut.clk)
            dut.read_en.value = 0
            await RisingEdge(dut.clk)
            read_val = dut.read_data.value
            scenario.add_read(addr, read_val.integer, get_sim_time())

    dut._log.info("Test finished successfully.")
