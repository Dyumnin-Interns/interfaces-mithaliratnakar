from cocotb.triggers import RisingEdge
from cocotb_coverage.coverage import coverage_db
from driver import DutDriver
from monitor import DutMonitor
from scoreboard import Scoreboard


class DutEnv:
    def __init__(self, dut):
        self.dut = dut
        self.driver = DutDriver(dut)
        self.scoreboard = Scoreboard()
        self.monitor = DutMonitor(dut, self.scoreboard.compare)

    async def reset(self):
        """Apply reset to the DUT."""
        self.dut.RST_N.value = 0
        await RisingEdge(self.dut.CLK)
        await RisingEdge(self.dut.CLK)
        self.dut.RST_N.value = 1
        await RisingEdge(self.dut.CLK)
        await RisingEdge(self.dut.CLK)

    async def start(self):
        """Start the environment."""
        await self.driver.initialize()
        self.monitor.start()
        await self.reset()

    async def write(self, address: int, data: int):
        """Convenience wrapper to perform a write through driver."""
        await self.driver.write(address, data)

    async def read(self, address: int):
        """Convenience wrapper to perform a read through driver."""
        await self.driver.read(address)

    def check_scoreboard(self, expected):
        """Compare with expected output value."""
        self.scoreboard.expect(expected)

    def expect_empty_read(self):
        """For read when FIFO is empty — can add assertions or logs."""
        if not self.scoreboard.was_read_expected():
            raise AssertionError("Unexpected read occurred while FIFO was empty.")

    def report_coverage(self):
        """Export coverage to YAML file."""
        coverage_db.export_to_yaml(filename="coverage.yml")
