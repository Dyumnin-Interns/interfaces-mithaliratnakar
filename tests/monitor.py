from cocotb.triggers import Event, RisingEdge
class FifoMonitor:
    def __init__(self, dut):
        self.dut = dut
        self.read_event = Event()
        self.last_read_data = 0
        self._callback = None

    def set_callback(self, callback):
        self._callback = callback

    async def monitor_reads(self):
        while True:
            await RisingEdge(self.dut.CLK)
            if self.dut.RD_EN.value and not self.dut.EMPTY.value:
                self.last_read_data = int(self.dut.DATA_OUT.value)
                self.read_event.set()
                if self._callback:
                    await self._callback(self.last_read_data)







