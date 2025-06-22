from cocotb.triggers import RisingEdge, Timer

class DutDriver:
    def __init__(self, dut):
        self.dut = dut

    async def initialize(self):
        self.dut.write_en.value = 0
        self.dut.read_en.value = 0
        self.dut.write_address.value = 0
        self.dut.write_data.value = 0
        self.dut.read_address.value = 0
        await RisingEdge(self.dut.CLK)

    async def write(self, address, data):
        self.dut.write_address.value = address
        self.dut.write_data.value = data
        self.dut.write_en.value = 1
        await RisingEdge(self.dut.CLK)
        self.dut.write_en.value = 0
        await RisingEdge(self.dut.CLK)

    async def read(self, address):
        self.dut.read_address.value = address
        self.dut.read_en.value = 1
        await RisingEdge(self.dut.CLK)
        self.dut.read_en.value = 0
        await RisingEdge(self.dut.CLK)
