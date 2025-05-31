import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time

@cocotb.test()
async def test_fifo_basic_operations(dut):
    """Test basic FIFO write and read operations"""
    dut.RST_N.value = 0
    dut.CLK.value = 0
    dut.write_en.value = 0
    dut.write_address.value = 0
    dut.write_data.value = 0
    dut.read_en.value = 0
    dut.read_address.value = 0

    # Start 100MHz clock (10ns period)
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start(start_high=False))
    cocotb.log.info("Applying reset...")
    await Timer(15, units="ns")  # Hold reset for 1.5 clock cycles
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    cocotb.log.info("Reset released")
    test_addr = 3
    test_data = 0xAA
    
    # Write operation
    cocotb.log.info(f"Writing data 0x{test_data:02X} to address {test_addr}")
    dut.write_address.value = test_addr
    dut.write_data.value = test_data
    dut.write_en.value = 1
    await RisingEdge(dut.CLK)
    dut.write_en.value = 0
    
    # Wait for write to complete (adjust based on your FIFO design)
    for _ in range(2):
        await RisingEdge(dut.CLK)
    
    # Read operation
    cocotb.log.info(f"Reading from address {test_addr}")
    dut.read_address.value = test_addr
    dut.read_en.value = 1
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await RisingEdge(dut.CLK)  # Additional cycle for data to appear
    
    # Verify read data
    read_data = dut.read_data.value.integer
    cocotb.log.info(f"Read data: 0x{read_data:02X}")
    assert read_data == test_data, \
        f"Readback mismatch! Expected 0x{test_data:02X}, got 0x{read_data:02X}"
    test_pairs = [
        (4, 0x55),
        (5, 0xDE),
        (6, 0xAD),
        (7, 0xBE),
        (8, 0xEF)
    ]
    
    for addr, data in test_pairs:
        # Write
        dut.write_address.value = addr
        dut.write_data.value = data
        dut.write_en.value = 1
        await RisingEdge(dut.CLK)
        dut.write_en.value = 0
        await RisingEdge(dut.CLK)
        
        # Read back
        dut.read_address.value = addr
        dut.read_en.value = 1
        await RisingEdge(dut.CLK)
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)
        
        # Verify
        read_data = dut.read_data.value.integer
        assert read_data == data, \
            f"Address {addr}: Expected 0x{data:02X}, got 0x{read_data:02X}"
        cocotb.log.info(f"Address {addr} verified: 0x{data:02X}")

    if hasattr(dut, 'simultaneous_read_write'):
        cocotb.log.info("Testing simultaneous read/write")
        write_addr = 9
        write_data = 0xFE
        read_addr = 4  # Read previously written location
        
        dut.write_address.value = write_addr
        dut.write_data.value = write_data
        dut.write_en.value = 1
        dut.read_address.value = read_addr
        dut.read_en.value = 1
        await RisingEdge(dut.CLK)
        dut.write_en.value = 0
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)
        

        read_data = dut.read_data.value.integer
        expected_data = 0x55  # From test_pairs[0]
        assert read_data == expected_data, \
            f"During concurrent R/W: Expected 0x{expected_data:02X}, got 0x{read_data:02X}"
    if hasattr(dut, 'full'):
        cocotb.log.info("Testing full condition")
        dut.write_en.value = 1
        for i in range(256):  # Assuming 256-depth FIFO
            dut.write_data.value = i
            await RisingEdge(dut.CLK)
            if dut.full.value:
                cocotb.log.info(f"FIFO full at write {i}")
                break
        
        assert dut.full.value, "FIFO should be full"
        dut.write_en.value = 0

    cocotb.log.info("All tests completed successfully!")
