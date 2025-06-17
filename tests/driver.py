import cocotb
from cocotb.triggers import RisingEdge

class FifoDriver:
    def __init__(self, dut):
        self.dut = dut

    async def read(self):
        """Read data from FIFO before writing."""
        self.dut.read_en.value = 1
        await RisingEdge(self.dut.CLK)
        self.dut.read_en.value = 0
        await RisingEdge(self.dut.CLK)
        return int(self.dut.D_OUT.value)

    async def write(self, data):
        """Drive data into FIFO after reading."""
        self.dut.D_IN.value = data
        self.dut.write_en.value = 1
        await RisingEdge(self.dut.CLK)
        self.dut.write_en.value = 0
        await RisingEdge(self.dut.CLK)

