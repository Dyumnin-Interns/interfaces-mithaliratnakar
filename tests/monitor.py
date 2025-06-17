# fifo_monitor.py

from cocotb.triggers import RisingEdge, Event

class FifoMonitor:
    def __init__(self, dut):
        self.dut = dut
        self.observed_reads = []
        self.read_event = Event()
        self.last_read_data = None

    async def monitor_reads(self):
        """Watches read_en and captures output data."""
        while True:
            await RisingEdge(self.dut.CLK)
            if self.dut.RD_EN.value == 1:
                await RisingEdge(self.dut.CLK)  # Wait for valid data
                value = int(self.dut.DATA_OUT.value)
                self.observed_reads.append(value)
                self.last_read_data = value
                self.read_event.set()
                self.dut._log.info(f"[MONITOR] Observed read: 0x{value:02X}")







