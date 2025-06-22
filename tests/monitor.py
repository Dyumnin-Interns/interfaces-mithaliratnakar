import cocotb
from cocotb.triggers import RisingEdge

class DutMonitor:
    def __init__(self, dut, callback):
        self.dut = dut
        self.callback = callback
        self._monitor_task = None

    def start(self):
        self._monitor_task = cocotb.start_soon(self._monitor_output())

    async def _monitor_output(self):
        while True:
            await RisingEdge(self.dut.CLK)
            if self.dut.read_en.value == 1 and self.dut.read_rdy.value == 1:
                read_val = int(self.dut.read_data.value)
                self.callback(read_val)
