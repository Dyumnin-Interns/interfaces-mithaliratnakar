import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_waveform(dut):
    # Generate clock
    clock = Clock(dut.CLK, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset DUT
    dut.RST_N.value = 0
    await Timer(20, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    
    # Force some activity for VCD
    dut.write_en.value = 1
    dut.write_address.value = 4
    dut.write_data.value = 1
    await Timer(100, units="ns")
    
    # Ensure long enough simulation for waveform capture
    dut._log.info("Simulation complete, check waveform.vcd")
