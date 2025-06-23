from cocotb.triggers import RisingEdge, ReadOnly

class DutDriver:
    def __init__(self, dut):
        self.dut = dut

    async def initialize(self):
        """Initialize all control signals."""
        self.dut.write_en.value = 0
        self.dut.read_en.value = 0
        self.dut.write_address.value = 0
        self.dut.write_data.value = 0
        self.dut.read_address.value = 0
        await RisingEdge(self.dut.CLK)

    async def write_input(self, address, data):
       await RisingEdge(self.dut.CLK)
       self.dut.write_address.value = address
       self.dut.write_data.value = data
       self.dut.write_en.value = 1
       await RisingEdge(self.dut.CLK)
       self.dut.write_en.value = 0

    async def read_y_ff_valid(self):
        """Check if y_ff has valid output (i.e., not empty)."""
        self.dut.read_address.value = 2  # Address for y_ff EMPTY_N
        self.dut.read_en.value = 1
        await RisingEdge(self.dut.CLK)

        await ReadOnly()
        result = self.dut.read_data.value == 1  # 1 means not empty (valid)

        await RisingEdge(self.dut.CLK)
        self.dut.read_en.value = 0
        return result

    async def read_y_ff_data(self):
        """Read data from y_ff output."""
        self.dut.read_address.value = 3  # Address for y_ff output
        self.dut.read_en.value = 1
        await RisingEdge(self.dut.CLK)

        await ReadOnly()
        result = self.dut.read_data.value.integer

        await RisingEdge(self.dut.CLK)
        self.dut.read_en.value = 0
        return result
