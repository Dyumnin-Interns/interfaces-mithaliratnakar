from cocotb.triggers import RisingEdge

class DutMonitor:
    def __init__(self, dut, callback=None):
        self.dut = dut
        self.callback = callback

    def start(self):
        pass 

