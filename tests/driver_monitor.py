import cocotb
from cocotb.triggers import RisingEdge, Timer

class FIFO_Driver:
    def __init__(self, dut):
        self.dut = dut

    async def write(self, address, data):
        self.dut.write_en.value = 1
        self.dut.write_address.value = address
        self.dut.write_data.value = data
        await RisingEdge(self.dut.CLK)
        self.dut.write_en.value = 0
        await Timer(1, units="ns")


class FIFO_Monitor:
    def __init__(self, dut, callback):
        self.dut = dut
        self.callback = callback

    async def read(self, address):
        self.dut.read_en.value = 1
        self.dut.read_address.value = address
        await RisingEdge(self.dut.CLK)
        self.dut.read_en.value = 0
        await Timer(1, units="ns")

        data_out = int(self.dut.read_data.value)
        self.callback(int(address), data_out)
