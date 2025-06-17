from driver import FifoDriver
from monitor import FifoMonitor
from scoreboard import FifoScoreboard
from cocotb.clock import Clock
from cocotb.triggers import Timer
import cocotb

class FifoEnv:
    def __init__(self, dut):
        self.dut = dut
        self.driver = FifoDriver(dut)
        self.monitor = FifoMonitor(dut)
        self.scoreboard = FifoScoreboard()

    async def start(self):
        """Start clock, reset, and connect monitor to scoreboard."""
        await self._start_clock()
        await self._reset_dut()
        self._start_monitor()

    async def _start_clock(self):
        cocotb.start_soon(Clock(self.dut.CLK, 10, units="ns").start())

    async def _reset_dut(self):
        self.dut.RST_N.value = 1
        await Timer(2, units="ns")
        self.dut.RST_N.value = 0
        await Timer(5, units="ns")
        self.dut.RST_N.value = 1
        await Timer(5, units="ns")

    def _start_monitor(self):
        """Start monitor and connect it to scoreboard callback."""
        async def monitor_callback():
            while True:
                await self.monitor.read_event.wait()
                data = self.monitor.last_read_data
                self.monitor.read_event.clear()
                self.dut._log.info(f"[MONITOR] Observed read: 0x{data:02X}")
                self.scoreboard.compare(data)
              
        cocotb.start_soon(self.monitor.monitor_reads())
        cocotb.start_soon(monitor_callback())


